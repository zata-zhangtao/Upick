from src.services import add_refresh_job, shutdown_scheduler, start_scheduler
from src.pages.gradio_page import app as subscription_app
# from src.pages.arxiv_papers_page import app as arxiv_app
from src.pages.Upick_for_arxiv import app as arxiv_app
import gradio as gr

def create_combined_ui():
    """Create a combined UI with tabs for different apps"""
    # For older versions of Gradio, we can't easily nest Blocks inside Tabs
    # So we'll launch each app independently
    
    # Create subscription app
    subscription_interface = subscription_app
    
    # Create arXiv papers app
    arxiv_interface = arxiv_app
    
    # Return one app and use kwargs to set the initial one
    # In older Gradio, we have to choose one app to return
    return subscription_interface

if __name__ == "__main__":
    
    # 添加默认的刷新任务（每小时刷新一次）
    add_refresh_job(hours=0, minutes=30)
    
    # 启动调度器
    start_scheduler()
    
    try:
        # Launch apps on different ports
        # subscription_thread = subscription_app.queue().launch(
        #     server_name="0.0.0.0", 
        #     server_port=7860,
        #     share=False,
        #     prevent_thread_lock=True
        # )
        
        # Launch arXiv app on a different port
        # arxiv_app.queue().launch(
        #     server_name="0.0.0.0", 
        #     server_port=7861,
        #     share=False
        # )
        arxiv_app.queue().launch(
            server_name="0.0.0.0", 
            server_port=7861,
            share=False,
        )
    finally:
        # 应用关闭时优雅地关闭调度器
        shutdown_scheduler()