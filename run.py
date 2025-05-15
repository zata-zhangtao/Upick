from src.services import add_refresh_job, shutdown_scheduler, start_scheduler
from src.pages.gradio_page import app as subscription_app
from src.pages.gradio_page import app as index_page
from src.pages.delete_page import app as delete_record_app
import gradio as gr
import apscheduler




def main():
        # 添加默认的刷新任务（每小时刷新一次）
    add_refresh_job(hours=0, minutes=30)
    
    # 启动调度器
    start_scheduler()
    
    try:
        delete_record_app.queue().launch(
            server_name="127.0.0.1", 
            server_port=7861,
            prevent_thread_lock=True,
            share=False,
        ),


        
        # Launch index_page
        index_page.queue().launch(
            server_name="127.0.0.1",  # 允许所有IP访问
            server_port=7860,       # 使用一个不同的端口
            share=False
        )
    finally:
        # 应用关闭时优雅地关闭调度器
        shutdown_scheduler()

if __name__ == "__main__":
    main()