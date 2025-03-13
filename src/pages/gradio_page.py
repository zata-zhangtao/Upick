import gradio as gr
import sqlite3
from datetime import datetime
from src.db import add_subscription, refresh_content, get_updates




def create_ui():
    """Create Gradio interface for subscription management"""
    with gr.Blocks() as app:
        gr.Markdown("# Subscription Manager")
        
        with gr.Tabs():
            with gr.Tab("Add/Refresh"):
                with gr.Row():
                    url_input = gr.Textbox(label="Subscription URL")
                    interval_input = gr.Number(label="Check Interval (minutes)", 
                                             minimum=1, 
                                             value=60)
                
                with gr.Row():
                    submit_btn = gr.Button("Add Subscription")
                    refresh_btn = gr.Button("Refresh")
                    
                output = gr.Textbox(label="Status")
                
                submit_btn.click(fn=add_subscription,
                               inputs=[url_input, interval_input],
                               outputs=output)
                
                refresh_btn.click(fn=refresh_content,
                                outputs=output)
                                
            with gr.Tab("Updates"):
                updates_table = gr.DataFrame(
                    headers=["URL", "Updated At", "Changes"],
                    label="Content Updates",
                    interactive=False
                )
                view_btn = gr.Button("View Updates")
                
                view_btn.click(fn=get_updates,
                             outputs=updates_table)
    
    return app


# Create and launch the interface
app = create_ui()
if __name__ == "__main__":
    app.launch()
