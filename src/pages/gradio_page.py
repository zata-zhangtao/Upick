import gradio as gr
import sqlite3
from datetime import datetime
from src.db  import add_subscription



def create_ui():
    """Create Gradio interface for subscription management"""
    with gr.Blocks() as app:
        gr.Markdown("# Subscription Manager")
        
        with gr.Row():
            url_input = gr.Textbox(label="Subscription URL")
            interval_input = gr.Number(label="Check Interval (minutes)", 
                                     minimum=1, 
                                     value=60)
        
        submit_btn = gr.Button("Add Subscription")
        output = gr.Textbox(label="Status")
        
        submit_btn.click(fn=add_subscription,
                        inputs=[url_input, interval_input],
                        outputs=output)
    
    return app



# Create and launch the interface
app = create_ui()
if __name__ == "__main__":
    app.launch()
