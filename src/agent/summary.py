from datetime import datetime
import time
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
import json
import re
from pydantic import BaseModel, Field
from typing import List, Optional
from src.log import get_logger
logger = get_logger("agent.summary")

# 导入LLM获取函数
from src.agent.llm import get_ali_llm, get_zhipu_llm
import yaml
import os

# 加载配置文件
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
yaml_path = os.path.join(ROOT_DIR, "config.yaml")
with open(yaml_path, "r", encoding="utf-8") as file:
    config_data = yaml.safe_load(file)

# 定义 Pydantic 模型用于输出解析
class SummaryResponse(BaseModel):
    content: List[str] = Field(default_factory=list, description="内容更新概要")
    key_points: List[str] = Field(default_factory=list, description="关键点列表")
    word_count: int = Field(default=0, description="内容字数统计")
    generated_at: str = Field(default="", description="生成时间")
    status: str = Field(default="success", description="处理状态")
    error_message: Optional[str] = Field(default=None, description="错误信息")
    raw_response: Optional[str] = Field(default=None, description="原始响应")

class SubscriptionAgent:
    def __init__(self, llm_model=None, max_retries=3, retry_delay=2):
        """
        Args:
            llm_model: 可选的 LLM 模型，如果为 None，则使用默认配置
            max_retries: 最大重试次数
            retry_delay: 重试间隔时间（秒）
        """
        # 根据配置文件选择模型
        if llm_model:
            self.llm = llm_model
        else:
            provider = config_data["app"]["provider"]
            model_name = config_data["app"]["model"]
            base_url = config_data["app"]["api_base"]
            
            if provider == "DASHSCOPE":
                self.llm = get_ali_llm(model_name, base_url)
                logger.info(f"使用阿里云模型: {model_name}")
            elif provider == "ZHIPU":
                self.llm = get_zhipu_llm(model_name, base_url)
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
        
        # 定义提示模板，进一步优化以确保提取 key_points
        self.prompt_template = PromptTemplate(
            input_variables=["contentdiff"],
            partial_variables={"format_instructions": self.parser.get_format_instructions()},
            template="""
            你是一个订阅号运营专家，可以根据差异内容总结出订阅内容的更新情况。请对以下内容差异进行总结：
            {contentdiff}

            ###注意，有些内容的可能仅仅是时间或者数据的变化，这样的内容更新是不需要总结的，可以看作没有更新，返回空数组
            ###注意：content和key_points的列表长度应当一致，也就是他们是一一对应关系
            ###要求：
            1. 提供内容更新概要（content），用数组形式返回。
            2. 提取每个内容的关键点（key_points），每个关键点应简洁且突出重点。
            3. 计算 content 字段的总字数（仅统计中文和英文字符，不包括标点和空格）。
            4. 返回结果使用中文，如果没有实质性更新或关键点，返回空数组。
            5. 严格按照以下 JSON 格式返回结果，不添加任何多余的说明文字或注释：
            {format_instructions}
            """
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
        logger.debug(f"开始生成摘要...")
        retries = 0
        last_exception = None
        raw_response = None
        
        while retries < self.max_retries:
            try:
                # 执行 LLM 调用获取原始响应
                chain = self.prompt_template | self.llm
                raw_response = chain.invoke({"contentdiff": contentdiff})
                logger.debug(f"llm——raw_response: {raw_response}")


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
                logger.debug(f"摘要生成成功")
                
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
            raw_response=raw_content
        )

# 使用示例
def main():
    # 创建示例 contentdiff，确保包含可提取的关键点
    sample_contentdiff = """
"[""Changed: '1' -> '2  分钟前\n.\nAIbase\nFlower Labs 颠覆AI应用模式，2360万美元打造首个全开放混合计算平台\n人工智能正在以前所未有的速度融入我们的日常应用，而一家名为Flower Labs的初创公司正以革命性的方式改变AI模型的部署和运行方式。这家获得Y Combinator支持的新锐企业近日推出了Flower Intelligence，一个创新的分布式云平台，专为在移动设备、个人电脑和网络应用中提供AI模型服务而设计。Flower Intelligence的核心优势在于其独特的混合计算策略。该平台允许应用程序在本地设备上运行AI模型，既保证了速度，又增强了隐私保护。当需要更强大的计算能力时，系统会在获得用户同意的情况下，无\n7'"", ""Added: '美国埃隆大学的一项调查显示，5'"", ""Added: '%的美国成年人都曾使用过像ChatGPT、Gemini、Claude这样的AI大语言模型。这项由北卡罗来纳州埃隆大学"想象数字未来中心"在'"", ""Added: '月份开展的调查，选取了500名受访者。结果发现，在使用过AI的人群中，34%的人表示至少每天会使用一次大语言模型。其中，ChatGPT最受欢迎，72%的受访者都用过;谷歌的Gemini位居第二，使用率为50% 。图源备注：图片由AI生成，图片授权服务商Midjourney越来越多的人开始和AI聊天机器人建立起特殊的关系。调查显示，38%的用户认为大语言模\n27'"", ""Changed: '3' -> '9'"", ""Changed: '49' -> '55'"", ""Changed: '1' -> '2'"", ""Deleted: '\n2  小时前\n.\nAIbase\n叫板Sora？潞晨科技开源视频大模型Open-Sora 2.0，降本提速\n听说过壕无人性的 OpenAI Sora 吧?动辄几百万美元的训练成本，简直就是视频生成界的"劳斯莱斯"。现在，潞晨科技宣布开源视频生成模型 Open-Sora2.0!仅仅花费了区区20万美元（相当于224张 GPU 的投入），就成功训练出了一个拥有 110亿参数的商业级视频生成大模型。性能直追"OpenAI Sora "别看 Open-Sora2.0成本不高，实力可一点都不含糊。它可是敢于叫板行业标杆 HunyuanVideo 和拥有300亿参数的 Step-Video 的狠角色。在权威评测 VBench 和用户偏好测试中，Open-Sora2.0的表现都令人刮目相看，多项关键指'""]"

    """
    
    # 初始化智能体
    agent = SubscriptionAgent(max_retries=3, retry_delay=2)
    summary_result = agent.generate_summary(sample_contentdiff)
    
    # 打印调试信息
    print(json.dumps(summary_result.model_dump(), indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()