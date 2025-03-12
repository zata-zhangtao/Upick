from langgraph.graph import StateGraph, END
from typing import TypedDict

# 定义状态
class AgentState(TypedDict):
    question: str
    answer: str
    processed: bool

# 节点1：处理问题
def process_question_node(state: AgentState) -> AgentState:
    state["answer"] = f"正在处理你的问题：{state['question']}  state[\"processed\"] = False 直接结束 "
    # state["processed"] = True
    return state

# 节点2：生成最终回答
def generate_answer_node(state: AgentState) -> AgentState:
    if "天气" in state["question"]:
        state["answer"] = "今天天气晴朗，温度25摄氏度。"
    else:
        state["answer"] = "这是一个好问题，但我需要更多信息来回答。"
    return state

# 条件函数：决定下一步
def decide_next(state: AgentState):
    if state["processed"]:
        return "generate_answer"
    return END

# 创建状态图
workflow = StateGraph(AgentState)

# 添加节点
workflow.add_node("process_question", process_question_node)
workflow.add_node("generate_answer", generate_answer_node)

# 设置入口点
workflow.set_entry_point("process_question")

# 添加边
workflow.add_conditional_edges(
    "process_question",
    decide_next,
    {
        "generate_answer": "generate_answer",
        END: END
    }
)
workflow.add_edge("generate_answer", END)

# 编译并运行
graph = workflow.compile()
result = graph.invoke({"question": "今天天气如何？", "processed": True})
print(result["answer"])
