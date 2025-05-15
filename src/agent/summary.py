from datetime import datetime
import time
import yaml
import os
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
# from langchain_core.memory import ConversationSummaryBufferMemory
from langchain.memory import ConversationSummaryBufferMemory

from langchain_core.messages import SystemMessage
import json
import re
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from src.log import get_logger
from src.agent.llm import get_ali_llm, get_zhipu_llm
from src.agent.incremental_learning import IncrementalLearner

logger = get_logger("agent.summary")



# 定义 Pydantic 模型用于输出解析
class SummaryResponse(BaseModel):
    content: List[str] = Field(default_factory=list, description="内容更新概要")
    key_points: List[str] = Field(default_factory=list, description="关键点列表")
    url_list: List[List[str]] = Field(default_factory=list, description="每个关键点对应的URL列表")
    word_count: int = Field(default=0, description="内容字数统计")
    generated_at: str = Field(default="", description="生成时间")
    status: str = Field(default="success", description="处理状态")
    error_message: Optional[str] = Field(default=None, description="错误信息")
    raw_response: Optional[str] = Field(default=None, description="原始响应")
    learning_examples: Optional[List[Dict[str, Any]]] = Field(default=None, description="使用的学习示例")

class SubscriptionAgent:
    def __init__(self, llm_model=None, max_retries=3, retry_delay=2, max_token_limit=30000):
        """
        Args:
            llm_model: 可选的 LLM 模型，如果为 None，则使用默认配置
            max_retries: 最大重试次数
            retry_delay: 重试间隔时间（秒）
        """
        self.max_token_limit = max_token_limit
        # 初始化增量学习器
        self.learner = IncrementalLearner()
        
        # 根据配置文件选择模型
        if llm_model:
            self.llm = llm_model
        else:
            from src.services import ConfigManager
            config = ConfigManager().get_config()
            provider = config["app"]["provider"]
            model_name = config["app"]["model"]
            base_url = config["app"]["base_url"]
            api_key = config["app"]["api_key"]
            
            if provider == "DASHSCOPE":
                self.llm = get_ali_llm(model_name, base_url,api_key)
                logger.info(f"使用阿里云模型: {model_name}")
            elif provider == "ZHIPU":
                if not api_key:
                    from dotenv import load_dotenv
                    load_dotenv()
                    api_key = os.getenv("ZHIPU_API_KEY")
                self.llm = get_zhipu_llm(model_name, base_url,api_key)
                logger.info(f"使用智谱模型: {model_name}")
            else:
                # logger.warning(f"未知的模型提供商: {provider}，默认使用阿里云模型")
                # self.llm = get_ali_llm(model_name)
                logger.warning(f"未知的模型提供商: {provider}，默认使用智谱模型")
                self.llm = get_zhipu_llm(model_name)
        
        self.max_retries = max_retries  # 最大重试次数
        self.retry_delay = retry_delay  # 重试间隔时间（秒）
        
        # 定义 Pydantic 输出解析器
        self.parser = PydanticOutputParser(pydantic_object=SummaryResponse)
        
        # 定义提示模板
        self.prompt_template = PromptTemplate(
            input_variables=["contentdiff", "similar_examples"],
            partial_variables={"format_instructions": self.parser.get_format_instructions()},
            template="""
            你是一个订阅号运营专家，可以根据差异内容总结出订阅内容的更新情况。请对以下内容差异进行总结：
            {contentdiff}

            ###注意，有些内容的可能仅仅是时间或者数据的变化，这样的内容更新是不需要总结的，可以看作没有更新，返回空数组
            ###注意：content和key_points的列表长度应当一致，也就是他们是一一对应关系
            ###注意：url_list是一个二维数组，每个元素对应key_points中的一个元素，包含该关键点中提到的所有URL

            ###历史学习示例：
            {similar_examples}

            ###要求：
            1. 提供内容更新概要（content），用数组形式返回。
            2. 提取每个内容的关键点（key_points），每个关键点应简洁且突出重点。
            3. 从内容中提取每个关键点相关的URL（url_list），如果没有URL则返回空数组。
            4. 计算 content 字段的总字数（仅统计中文和英文字符，不包括标点和空格）。
            5. 返回结果使用中文，如果没有实质性更新或关键点，返回空数组。
            6. 参考历史学习示例中的成功案例，特别关注那些评分较高的示例，模仿其摘要风格和关键点提取方式。
            7. 优先选取评分大于0.8的高质量示例作为参考模板。
            8. 严格按照以下 JSON 格式返回结果，不添加任何多余的说明文字或注释：
            {format_instructions}
            """
        )

        # 初始化 Langchain 记忆组件
        self.memory = ConversationSummaryBufferMemory(
            llm=self.llm,
            max_token_limit=self.max_token_limit,
            return_messages=True,
            verbose=True
        )



    def extract_json(self, raw_content: str) -> str:
        """从原始响应中提取 JSON 字符串 extract JSON string from raw response
        Args:
            raw_content: 原始响应内容
        Returns:
            str: 提取的 JSON 字符串
        """
        json_match = re.search(r'\{.*\}', raw_content, re.DOTALL)
        return json_match.group(0) if json_match else raw_content

    def generate_summary(self, contentdiff: str) -> SummaryResponse:
        """
        生成 summary 的主函数
        参数:
            contentdiff: 输入的内容差异文本
        返回:
            SummaryResponse: 包含摘要内容的 Pydantic 模型
        """
        # 获取相似的历史示例，特别关注高评分示例
        similar_examples = self.learner.get_similar_examples(contentdiff, top_k=5)
        
        # 过滤并优先使用评分高的示例
        high_rated_examples = [ex for ex in similar_examples if ex.feedback_score >= 0.8]
        if high_rated_examples:
            logger.info(f"找到 {len(high_rated_examples)} 个高评分学习示例")
            selected_examples = high_rated_examples
        else:
            logger.info("没有找到高评分学习示例，使用所有相似示例")
            selected_examples = similar_examples

        # 构建示例文本，包含评分信息以便模型参考
        similar_examples_text = "\n\n".join([
            f"示例 {i+1} (评分: {ex.feedback_score:.1f}):\n输入: {ex.input_text[:200]}...\n输出: {ex.output_text}\n"
            for i, ex in enumerate(selected_examples)
        ])
        
        # 记录使用的学习示例，以便后续分析
        used_examples = [
            {
                "input_text": ex.input_text[:100] + "...",
                "output_text": ex.output_text,
                "feedback_score": ex.feedback_score,
                "similarity_score": ex.metadata.get('similarity_score', 0)
            }
            for ex in selected_examples
        ]

        # 估算 token 数量
        avg_token_per_char = 0.5
        estimated_tokens = len(contentdiff) * avg_token_per_char
        
        # 如果内容可能超出 token 限制，使用带内存的处理方法
        if estimated_tokens > self.max_token_limit:
            logger.info(f"内容估计 token 数 ({int(estimated_tokens)}) 超过限制 ({self.max_token_limit})，使用内存处理")
            response = self.generate_summary_with_memory(contentdiff)
            response.learning_examples = used_examples
            return response

        logger.debug(f"开始生成摘要...")
        retries = 0
        last_exception = None
        raw_response = None
        
        while retries < self.max_retries:
            try:
                # 执行 LLM 调用获取原始响应
                chain = self.prompt_template | self.llm
                raw_response = chain.invoke({
                    "contentdiff": contentdiff,
                    "similar_examples": similar_examples_text
                })

                logger.debug(f"similar_examples: {similar_examples_text}")
                
                # 检查并提取原始内容
                raw_content = raw_response.content if hasattr(raw_response, 'content') else str(raw_response)
                json_content = self.extract_json(raw_content)
                
                # 尝试解析响应
                response = self.parser.parse(json_content)
                
                # 确保生成时间字段有值
                if not response.generated_at:
                    response.generated_at = datetime.now().isoformat()
                
                # 计算字数（如果 LLM 未提供，则基于 content 计算）
                if response.word_count == 0 and response.content:
                    response.word_count = len("".join(response.content).replace(" ", "").replace(",", "").replace(".", ""))
                
                # 添加原始响应到结果中
                response.raw_response = raw_content
                # 添加使用的学习示例
                response.learning_examples = used_examples
                
                logger.debug(f"摘要生成成功: {raw_content}")
                
                return response

            except Exception as e:
                logger.error(f"摘要生成失败 at line {e.__traceback__.tb_lineno}: {e}")
                last_exception = e
                retries += 1
                if retries < self.max_retries:
                    time.sleep(self.retry_delay)
                    continue
        
        # 所有重试都失败后，返回错误响应
        raw_content = raw_response.content if raw_response and hasattr(raw_response, 'content') else str(raw_response) if raw_response else "No response"
        logger.error(f"摘要生成重试全部失败，返回错误响应: {str(last_exception)}")
        return SummaryResponse(
            content=[],
            key_points=[],
            word_count=0,
            generated_at=datetime.now().isoformat(),
            status="error",
            error_message=f"Failed to parse SummaryResponse: {str(last_exception)}",
            raw_response=raw_content,
            learning_examples=used_examples
        )

    def chunking_content(self, contentdiff: str) -> List[str]:
        """
        将大型内容差异分块
        参数:
            contentdiff: 输入的内容差异文本
        返回:
            List[str]: 分块后的内容列表
        """
        # 估计平均每个字符对应的 token 数（这是一个简化的估算）
        avg_token_per_char = 0.5
        # 计算内容的预估 token 数
        estimated_tokens = len(contentdiff) * avg_token_per_char
        
        if estimated_tokens <= self.max_token_limit:
            return [contentdiff]
        
        # 按照变更单元进行分割
        chunks = []
        change_units = re.findall(r'""(?:Changed|Added|Deleted):.*?""', contentdiff, re.DOTALL)
        
        if not change_units:
            # 如果没有识别到变更单元，则按照字符数简单分割
            chars_per_chunk = int(self.max_token_limit / avg_token_per_char)
            for i in range(0, len(contentdiff), chars_per_chunk):
                chunks.append(contentdiff[i:i+chars_per_chunk])
        else:
            # 组织变更单元成块，控制每块大小
            current_chunk = ""
            chars_per_chunk = int(self.max_token_limit / avg_token_per_char)
            
            for unit in change_units:
                if len(current_chunk) + len(unit) > chars_per_chunk:
                    chunks.append(current_chunk)
                    current_chunk = unit
                else:
                    if current_chunk:
                        current_chunk += "\n"
                    current_chunk += unit
            
            if current_chunk:
                chunks.append(current_chunk)
        
        logger.info(f"内容已分成 {len(chunks)} 个块进行处理")
        return chunks

    def generate_summary_with_memory(self, contentdiff: str) -> SummaryResponse:
        """
        使用内存功能生成摘要
        参数:
            contentdiff: 输入的内容差异文本
        返回:
            SummaryResponse: 包含摘要内容的 Pydantic 模型
        """
        logger.debug(f"开始使用记忆功能生成摘要...")
        
        # 分块处理内容
        content_chunks = self.chunking_content(contentdiff)
        
        # 收集所有块的分析结果
        collected_content = []
        collected_key_points = []
        collected_urls = []
        
        # 使用记忆处理多个内容块
        memory = ConversationSummaryBufferMemory(
            llm=self.llm,
            max_token_limit=self.max_token_limit // 2,  # 预留一半给输入和输出
            return_messages=True
        )
        
        # 首先添加系统指令
        memory.chat_memory.add_message(SystemMessage(content="""
        你是一个专业的内容分析专家，需要分析内容差异并提取关键信息。
        你将分析多个内容块，为每个块提取关键点和URL。
        最后，你需要整合所有信息，生成符合指定格式的JSON摘要。
        """))
        
        # 处理每个块，提取信息并累积到记忆中
        for i, chunk in enumerate(content_chunks):
            logger.info(f"处理内容块 {i+1}/{len(content_chunks)}")
            
            # 构建块处理提示模板
            chunk_prompt = PromptTemplate(
                input_variables=["chunk_content"],
                template="""
                请分析以下内容差异块，提取关键信息：
                {chunk_content}
                
                请提供以下内容（JSON格式）：
                1. content: 内容更新概要列表
                2. key_points: 对应的关键点列表
                3. urls: 从内容中提取的URL列表（二维数组）
                
                只返回JSON格式结果，不要添加额外说明。
                """
            )
            
            # 为该块创建链
            chunk_chain = chunk_prompt | self.llm
            
            # 获取该块的分析结果
            try:
                chunk_result = chunk_chain.invoke({"chunk_content": chunk})
                chunk_content = chunk_result.content if hasattr(chunk_result, 'content') else str(chunk_result)
                
                # 尝试解析该块的JSON结果
                json_match = re.search(r'\{.*\}', chunk_content, re.DOTALL)
                if json_match:
                    chunk_json = json.loads(json_match.group(0))
                    
                    # 收集结果
                    if 'content' in chunk_json and isinstance(chunk_json['content'], list):
                        collected_content.extend(chunk_json['content'])
                    if 'key_points' in chunk_json and isinstance(chunk_json['key_points'], list):
                        collected_key_points.extend(chunk_json['key_points'])
                    if 'urls' in chunk_json and isinstance(chunk_json['urls'], list):
                        collected_urls.extend(chunk_json['urls'])
                
                # 将分析结果添加到记忆中
                memory.save_context(
                    {"input": f"内容块 {i+1}:\n{chunk[:200]}..."},
                    {"output": f"分析结果:\n{chunk_content[:200]}..."}
                )
                
            except Exception as e:
                logger.error(f"块处理失败: {e}")
                continue

        # 获取相似的历史示例作为参考
        similar_examples = self.learner.get_similar_examples(contentdiff, top_k=3)
        # 优先选择高评分示例
        high_rated_examples = [ex for ex in similar_examples if ex.feedback_score >= 0.8]
        if high_rated_examples:
            selected_examples = high_rated_examples
        else:
            selected_examples = similar_examples
            
        similar_examples_text = "\n\n".join([
            f"示例 {i+1} (评分: {ex.feedback_score:.1f}):\n输入: {ex.input_text[:100]}...\n输出: {ex.output_text}\n"
            for i, ex in enumerate(selected_examples)
        ])
        
        # 记录使用的学习示例
        used_examples = [
            {
                "input_text": ex.input_text[:100] + "...",
                "output_text": ex.output_text,
                "feedback_score": ex.feedback_score,
                "similarity_score": ex.metadata.get('similarity_score', 0)
            }
            for ex in selected_examples
        ]
        
        # 最终使用收集的信息构建符合Pydantic模型的结果
        final_prompt_template = PromptTemplate(
            input_variables=["collected_content", "collected_key_points", "collected_urls", "similar_examples", "format_instructions"],
            template="""
            根据以下收集的信息，生成最终摘要：
            
            内容更新概要: {collected_content}
            关键点列表: {collected_key_points}
            URL列表: {collected_urls}
            
            ###历史学习示例：
            {similar_examples}
            
            请严格按以下格式返回JSON结果：
            {format_instructions}
            
            注意：
            1. content 和 key_points 必须一一对应
            2. url_list 是二维数组，对应每个 key_point 中的URL
            3. 计算 word_count (内容字符总数，不含标点和空格)
            4. 如果发现重复内容，请合并或删除
            5. 参考历史学习示例中高评分示例的摘要风格
            6. 只返回JSON，不要添加额外说明
            """
        )
        
        # 创建最终链
        final_chain = final_prompt_template | self.llm
        
        # 尝试获取最终结果
        retries = 0
        last_exception = None
        raw_response = None
        
        while retries < self.max_retries:
            try:
                # 使用收集的信息生成最终摘要
                raw_response = final_chain.invoke({
                    "collected_content": collected_content,
                    "collected_key_points": collected_key_points,
                    "collected_urls": collected_urls,
                    "similar_examples": similar_examples_text,
                    "format_instructions": self.parser.get_format_instructions()
                })
                
                # 提取JSON内容
                raw_content = raw_response.content if hasattr(raw_response, 'content') else str(raw_response)
                json_content = self.extract_json(raw_content)
                
                # 使用Pydantic解析器确保结果符合模型定义
                response = self.parser.parse(json_content)
                
                # 确保生成时间字段有值
                if not response.generated_at:
                    response.generated_at = datetime.now().isoformat()
                
                # 计算字数（如果未提供）
                if response.word_count == 0 and response.content:
                    content_text = "".join(response.content)
                    # 移除标点和空格后计算字数
                    word_count = len(re.sub(r'[\s\p{P}]', '', content_text, flags=re.UNICODE))
                    response.word_count = word_count
                
                # 确保URL列表格式正确
                if len(response.url_list) < len(response.key_points):
                    # 补充空URL列表，使长度匹配
                    for _ in range(len(response.key_points) - len(response.url_list)):
                        response.url_list.append([])
                
                # 添加原始响应和学习示例
                response.raw_response = raw_content
                response.learning_examples = used_examples
                logger.debug(f"使用记忆功能摘要生成成功")
                
                return response
                
            except Exception as e:
                logger.error(f"使用记忆功能摘要生成失败: {e}")
                last_exception = e
                retries += 1
                if retries < self.max_retries:
                    time.sleep(self.retry_delay)
        
        # 所有重试失败后，构建空响应
        logger.error(f"使用记忆功能摘要生成全部失败: {str(last_exception)}")
        return SummaryResponse(
            content=[],
            key_points=[],
            url_list=[],
            word_count=0,
            generated_at=datetime.now().isoformat(),
            status="error",
            error_message=f"使用记忆功能摘要生成失败: {str(last_exception)}",
            raw_response=str(raw_response) if raw_response else "No response",
            learning_examples=used_examples
        )

    def save_feedback(self, input_text: str, output_text: str | List[str], feedback_score: float, metadata: dict = None):
        """
        保存用户反馈用于增量学习
        Args:
            input_text: 原始输入文本
            output_text: 生成的输出文本（字符串或字符串列表）
            feedback_score: 反馈分数 (0-1)
            metadata: 额外的元数据
        """
        # 如果output_text是列表，将其转换为字符串
        if isinstance(output_text, list):
            output_text = "\n".join(output_text)
            
        self.learner.save_example(
            input_text=input_text,
            output_text=output_text,
            feedback_score=feedback_score,
            metadata=metadata
        )
        logger.info(f"保存反馈，反馈分数: {feedback_score}")

    def get_learning_stats(self):
        """
        获取学习统计信息
        Returns:
            Dict: 学习统计信息
        """
        return self.learner.get_learning_statistics()



# 使用示例
def main():
    # 创建示例 contentdiff，确保包含可提取的关键点
    sample_contentdiff = """
"[""Changed: '1' -> '2  分钟前\n.\nAIbase\nFlower Labs 颠覆AI应用模式，2360万美元打造首个全开放混合计算平台\n人工智能正在以前所未有的速度融入我们的日常应用，而一家名为Flower Labs的初创公司正以革命性的方式改变AI模型的部署和运行方式。这家获得Y Combinator支持的新锐企业近日推出了Flower Intelligence，一个创新的分布式云平台，专为在移动设备、个人电脑和网络应用中提供AI模型服务而设计。Flower Intelligence的核心优势在于其独特的混合计算策略。该平台允许应用程序在本地设备上运行AI模型，既保证了速度，又增强了隐私保护。当需要更强大的计算能力时，系统会在获得用户同意的情况下，无\n7'"", ""Added: '美国埃隆大学的一项调查显示，5'"", ""Added: '%的美国成年人都曾使用过像ChatGPT、Gemini、Claude这样的AI大语言模型。这项由北卡罗来纳州埃隆大学"想象数字未来中心"在'"", ""Added: '月份开展的调查，选取了500名受访者。结果发现，在使用过AI的人群中，34%的人表示至少每天会使用一次大语言模型。其中，ChatGPT最受欢迎，72%的受访者都用过;谷歌的Gemini位居第二，使用率为50% 。图源备注：图片由AI生成，图片授权服务商Midjourney越来越多的人开始和AI聊天机器人建立起特殊的关系。调查显示，38%的用户认为大语言模\n27'"", ""Changed: '3' -> '9'"", ""Changed: '49' -> '55'"", ""Changed: '1' -> '2'"", ""Deleted: '\n2  小时前\n.\nAIbase\n叫板Sora？潞晨科技开源视频大模型Open-Sora 2.0，降本提速\n听说过壕无人性的 OpenAI Sora 吧?动辄几百万美元的训练成本，简直就是视频生成界的"劳斯莱斯"。现在，潞晨科技宣布开源视频生成模型 Open-Sora2.0!仅仅花费了区区20万美元（相当于224张 GPU 的投入），就成功训练出了一个拥有 110亿参数的商业级视频生成大模型。性能直追"OpenAI Sora "别看 Open-Sora2.0成本不高，实力可一点都不含糊。它可是敢于叫板行业标杆 HunyuanVideo 和拥有300亿参数的 Step-Video 的狠角色。在权威评测 VBench 和用户偏好测试中，Open-Sora2.0的表现都令人刮目相看，多项关键指'""]"
    """

    # 将示例内容重复20倍以测试大内容处理能力
    if True:
        sample_contentdiff = sample_contentdiff * 20
        
    # 打印内容长度信息用于调试
    content_length = len(sample_contentdiff)
    logger.debug(f"测试内容长度: {content_length} 字符")

    
    
    # 初始化智能体
    agent = SubscriptionAgent(max_retries=3, retry_delay=2, max_token_limit=30000)
    
    # 自动处理，会根据内容大小选择合适的方法
    summary_result = agent.generate_summary(sample_contentdiff)
    
    # 打印调试信息
    print(json.dumps(summary_result.model_dump(), indent=2, ensure_ascii=False))

    # 保存用户反馈
    agent.save_feedback(
        input_text=sample_contentdiff,
        output_text=summary_result.content,  # 这里传入的是列表，会被自动转换为字符串
        feedback_score=0.8,
        metadata={"user_id": "user123"}
    )

if __name__ == "__main__":
    main()