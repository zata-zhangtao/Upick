
import gradio as gr

# 定义两个简单的函数，分别用于不同的选项卡
def greet(name):
    return f"你好，{name}！"

def farewell(name):
    return f"再见，{name}！"

# 使用 Blocks 创建界面
with gr.Blocks() as demo:
    # 创建 Tabs 容器
    with gr.Tabs():
        # 第一个选项卡：打招呼
        with gr.TabItem("添加订阅地址"):
            name_input_1 = gr.Textbox(label="输入你的名字")
            greet_output = gr.Textbox(label="输出")
            greet_button = gr.Button("提交")
            greet_button.click(fn=greet, inputs=name_input_1, outputs=greet_output)

        # 第二个选项卡：告别
        with gr.TabItem("告别"):
            name_input_2 = gr.Textbox(label="输入你的名字")
            farewell_output = gr.Textbox(label="输出")
            farewell_button = gr.Button("提交")
            farewell_button.click(fn=farewell, inputs=name_input_2, outputs=farewell_output)

# 启动应用
demo.launch()
