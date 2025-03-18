from src.services import add_refresh_job, shutdown_scheduler, start_scheduler
from src.pages.gradio_page import create_ui

# if __name__ == "__main__":
#     create_ui().launch(share=False)

if __name__ == "__main__":
    
    # 添加默认的刷新任务（每小时刷新一次）
    add_refresh_job(hours=0, minutes=30)
    
    # 启动调度器
    start_scheduler()
    
    try:
        # 启动Gradio界面
        create_ui().launch(server_name="0.0.0.0", server_port=7860)
    finally:
        # 应用关闭时优雅地关闭调度器
        shutdown_scheduler()