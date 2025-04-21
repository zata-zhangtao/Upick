import gradio as gr
from src.db.db_operate import (
    add_subscription, 
    refresh_content, 
    get_updates, 
    delete_subscription, 
    get_subscriptions,
    delete_old_content
)
import json
from datetime import datetime
from src.log import get_logger

logger = get_logger("pages.db_manage_page")

def create_ui():
    """Create Gradio interface for database management"""
    with gr.Blocks(title="Database Manager", css="""
        .status-box {
            margin: 10px 0;
            padding: 10px;
            border-radius: 4px;
        }
        .success {
            background-color: #d1fae5;
            border: 1px solid #10b981;
            color: #065f46;
        }
        .error {
            background-color: #fee2e2;
            border: 1px solid #ef4444;
            color: #b91c1c;
        }
        .subscription-table {
            width: 100%;
            border-collapse: collapse;
        }
        .subscription-table th, .subscription-table td {
            padding: 8px;
            text-align: left;
            border-bottom: 1px solid #e5e7eb;
        }
        .subscription-table th {
            background-color: #f3f4f6;
            font-weight: bold;
        }
        .subscription-table tr:hover {
            background-color: #f9fafb;
        }
        .button-row {
            display: flex;
            gap: 10px;
            margin-top: 10px;
        }
    """) as app:
        gr.Markdown("# Database Management Interface")
        
        with gr.Tabs():
            # Tab 1: Add Subscription
            with gr.Tab("Add Subscription"):
                with gr.Row():
                    url_input = gr.Textbox(label="Website URL", placeholder="Enter website URL")
                    interval_input = gr.Number(label="Check Interval (minutes)", 
                                             minimum=1, 
                                             value=60)
                
                add_btn = gr.Button("Add Subscription", variant="primary")
                add_status = gr.Textbox(label="Status", interactive=False)
                
                add_btn.click(
                    fn=add_subscription,
                    inputs=[url_input, interval_input],
                    outputs=add_status
                )
            
            # Tab 2: Refresh Content
            with gr.Tab("Refresh Content"):
                similarity_threshold = gr.Slider(
                    minimum=0.1, 
                    maximum=1.0, 
                    value=0.95, 
                    step=0.05, 
                    label="Similarity Threshold (lower value = more updates)"
                )
                
                refresh_btn = gr.Button("Refresh All Subscriptions", variant="primary")
                refresh_status = gr.Textbox(label="Status", interactive=False)
                
                refresh_btn.click(
                    fn=refresh_content,
                    inputs=[similarity_threshold],
                    outputs=refresh_status
                )
            
            # Tab 3: Manage Subscriptions
            with gr.Tab("Manage Subscriptions"):
                
                def format_subscriptions(subscriptions):
                    if not subscriptions or len(subscriptions) == 0:
                        return "<p>No subscriptions found.</p>"
                    
                    html = "<table class='subscription-table'>"
                    html += "<tr><th>ID</th><th>URL</th><th>Last Updated</th><th>Check Interval (min)</th><th>Actions</th></tr>"
                    
                    for sub_id, url, last_updated, check_interval in subscriptions:
                        html += f"""
                        <tr>
                            <td>{sub_id}</td>
                            <td><a href="{url}" target="_blank">{url}</a></td>
                            <td>{last_updated}</td>
                            <td>{check_interval}</td>
                            <td>
                                <button onclick="window.subscription_to_delete = {sub_id}; document.getElementById('delete-id-input').value = {sub_id};">Delete</button>
                            </td>
                        </tr>
                        """
                    
                    html += "</table>"
                    return html
                
                def load_subscriptions():
                    subs = get_subscriptions()
                    return format_subscriptions(subs)
                
                refresh_list_btn = gr.Button("Refresh Subscription List", variant="secondary")
                subscriptions_html = gr.HTML(label="Subscriptions")
                
                with gr.Row():
                    delete_id_input = gr.Number(label="Subscription ID to Delete", 
                                               minimum=1, 
                                               step=1,
                                               elem_id="delete-id-input")
                    delete_btn = gr.Button("Delete Subscription", variant="stop")
                
                delete_status = gr.Textbox(label="Status", interactive=False)
                
                # Load subscriptions when tab is opened or refresh button clicked
                refresh_list_btn.click(
                    fn=load_subscriptions,
                    inputs=[],
                    outputs=subscriptions_html
                )
                
                # Handle subscription deletion
                def delete_sub_and_refresh(sub_id):
                    result = delete_subscription(int(sub_id))
                    subs = get_subscriptions()
                    return result, format_subscriptions(subs)
                
                delete_btn.click(
                    fn=delete_sub_and_refresh,
                    inputs=[delete_id_input],
                    outputs=[delete_status, subscriptions_html]
                )
                
                # Initial load of subscriptions
                app.load(
                    fn=load_subscriptions,
                    inputs=[],
                    outputs=subscriptions_html
                )
            
            # Tab 4: Cleanup Old Content
            with gr.Tab("Cleanup Database"):
                days_to_keep = gr.Slider(
                    minimum=1, 
                    maximum=365, 
                    value=30, 
                    step=1, 
                    label="Days of Content to Keep"
                )
                
                cleanup_btn = gr.Button("Delete Old Content", variant="stop")
                cleanup_status = gr.Textbox(label="Status", interactive=False)
                
                cleanup_btn.click(
                    fn=delete_old_content,
                    inputs=[days_to_keep],
                    outputs=cleanup_status
                )
            
    return app

# Create app instance
app = create_ui()

if __name__ == "__main__":
    app.launch() 