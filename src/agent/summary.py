from datetime import datetime
from langchain.prompts import PromptTemplate
from langchain_core.runnables import RunnableSequence
from langchain.chains import LLMChain, SequentialChain
from langchain_core.output_parsers.json import SimpleJsonOutputParser
import json
from src.agent.llm import get_ali_llm

# 定义固定的summary JSON格式模板
SUMMARY_TEMPLATE = {
    "summary": {
        "content": "",
        "key_points": [],
        "word_count": 0,
        "generated_at": ""
    },
    "status": "success",
    "error_message": None
}

class SubscriptionAgent:
    def __init__(self, llm_model=None):
        # 初始化LLM，如果没有传入特定模型，使用默认配置
        self.llm = llm_model if llm_model else get_ali_llm("qwen-7b-chat")

        # test
        print("----")
        print(self.llm.invoke("你好"))
        print("----")
        
        # 定义提示模板
        self.prompt_template = PromptTemplate(
            input_variables=["contentdiff"],
            template="""
            你是一个订阅号运营专家，可以根据差异内容总结出订阅内容的更新情况，请对以下内容差异进行总结：
            {contentdiff}
            
            要求：
            1. 提供简洁的内容更新概要
            2. 提取关键点
            3. 计算总字数
            返回结果使用中文

            返回格式json（请严格按照以下格式返回）：
            {{
                "summary": {{
                    "content": "",
                    "key_points": [],
                    "word_count": 0,
                    "generated_at": ""
                }},
            }}


            """
        )
        
        # 创建LLM链
        self.chain = self.prompt_template | self.llm 



    def generate_summary(self, contentdiff: str) -> dict:
        """
        生成summary的主函数
        参数:
            contentdiff: 输入的内容差异文本
        返回:
            dict: 固定格式的JSON结果
        """
        try:
            # 执行LLM链获取结果，输入需要是字典格式
            result = self.chain.invoke({"contentdiff": contentdiff}).content
            print("result: ", result)
            # 解析结果（假设LLM返回的是JSON字符串）
    
            # 假设返回的是JSON格式字符串，尝试解析
            parsed_result = json.loads(result)
            summary_content = parsed_result["summary"]["content"]
            key_points = parsed_result["summary"]["key_points"]
            word_count = parsed_result["summary"]["word_count"]
            generated_at = parsed_result["summary"]["generated_at"]
    

            # 创建响应对象
            print("summary_content: ", summary_content)
            print("key_points: ", key_points)
            print("word_count: ", word_count)
            print("generated_at: ", generated_at)
            response = SUMMARY_TEMPLATE.copy()
            response["summary"]["content"] = summary_content
            response["summary"]["key_points"] = key_points
            response["summary"]["word_count"] = word_count
            response["summary"]["generated_at"] = generated_at

            return response

        except Exception as e:
            # 错误处理
            error_response = SUMMARY_TEMPLATE.copy()
            error_response["status"] = "error"
            error_response["error_message"] = f"Error on line {e.__traceback__.tb_lineno}: {str(e)}"
            return error_response
# 使用示例
def main():
    # 创建示例contentdiff
    sample_contentdiff = """
    Original: The quick brown fox jumps over the lazy dog.
    Updated: The swift brown fox leaps over the idle dog quickly.
    """
    
    # 初始化智能体
    agent = SubscriptionAgent()
    summary_result = agent.generate_summary(sample_contentdiff)
    print(summary_result)
    
    # 生成summary
    # summary_result = agent.generate_summary(sample_contentdiff)
    
    # 打印格式化的JSON结果
    # print(json.dumps(summary_result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()