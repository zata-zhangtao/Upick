import gradio as gr
import sqlite3
from datetime import datetime
from src.db import add_subscription, refresh_content, get_updates
import json




def create_ui():
    """Create Gradio interface for subscription management"""
    with gr.Blocks(css="""
        .updates-container {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 16px;
        }
        .card {
            background: white;
            border-radius: 10px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
            transition: all 0.3s ease;
            border: 1px solid #e5e7eb;
            overflow: hidden;
        }
        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.15);
        }
        .card-header {
            background: linear-gradient(90deg, #4f46e5 0%, #7c3aed 100%);
            color: white;
            padding: 12px 16px;
            font-weight: bold;
            word-break: break-all;
        }
        .card-body {
            padding: 16px;
        }
        .timestamp {
            color: #6b7280;
            font-size: 0.875rem;
            margin-bottom: 12px;
            display: flex;
            align-items: center;
        }
        .timestamp svg {
            margin-right: 6px;
        }
        .content {
            color: #1f2937;
            line-height: 1.5;
        }
        .content ol {
            padding-left: 20px;
        }
        .content li {
            margin-bottom: 6px;
        }
        .empty-state {
            background-color: #f9fafb;
            border-radius: 8px;
            padding: 32px;
            text-align: center;
            color: #6b7280;
        }
        .empty-state svg {
            width: 64px;
            height: 64px;
            margin: 0 auto 16px;
            color: #9ca3af;
        }
    """) as app:
        gr.Markdown("# Subscription Manager")
        
        with gr.Tabs():
            with gr.Tab("Add/Refresh"):
                with gr.Row():
                    url_input = gr.Textbox(label="Subscription URL")
                    interval_input = gr.Number(label="Check Interval (minutes)", 
                                             minimum=1, 
                                             value=60)
                
                with gr.Row():
                    submit_btn = gr.Button("Add Subscription", variant="primary")
                    refresh_btn = gr.Button("Refresh", variant="secondary")
                    
                output = gr.Textbox(label="Status")
                
                submit_btn.click(fn=add_subscription,
                               inputs=[url_input, interval_input],
                               outputs=output)
                
                refresh_btn.click(fn=refresh_content,
                                outputs=output)
                                
            with gr.Tab("Updates"):
                updates_container = gr.HTML(label="Content Updates")
                view_btn = gr.Button("View Updates", variant="primary")
                
                def format_updates_as_cards(updates_data):
                    if not updates_data or len(updates_data) == 0:
                        return """
                        <div class='empty-state'>
                            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
                            </svg>
                            <h3 class="text-lg font-medium mb-2">No updates found</h3>
                            <p>Click "Refresh Updates" to check for new content.</p>
                        </div>
                        """
                    
                    html = "<div class='updates-container'>"
                    for update in updates_data:
                        # Handle the case where update might have more than 3 values
                        if isinstance(update, (list, tuple)):
                            if len(update) >= 3:
                                url = update[0]
                                updated_at = update[1]
                                try:
                                    print(update[2])
                                    changes = json.loads(update[2]) if isinstance(update[2], (str, bytes, bytearray)) else {}
                                except json.JSONDecodeError:
                                    changes = {}
                                    changes['key_points'] = update[2]
                            else:
                                continue  # Skip if not enough values
                        else:
                            # If update is a dictionary or has another structure
                            # Adjust this part based on the actual structure of your data
                            continue
                            
                        date_formatted = updated_at
                        if isinstance(updated_at, str):
                            try:
                                date_formatted = datetime.fromisoformat(updated_at).strftime("%Y-%m-%d %H:%M:%S")
                            except ValueError:
                                # Keep original if parsing fails
                                pass
                        
                        content = changes.get('key_points', '')
                        if isinstance(content, list):
                            content_html = '<ol>' + ''.join([f'<li>{point}</li>' for point in content]) + '</ol>'
                        else:
                            content_html = content
                        
                        html += f"""
                        <div class='card'>
                            <div class='card-header'>{url}</div>
                            <div class='card-body'>
                                <div class='timestamp'>
                                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
                                        <path d="M8 3.5a.5.5 0 0 0-1 0V9a.5.5 0 0 0 .252.434l3.5 2a.5.5 0 0 0 .496-.868L8 8.71V3.5z"/>
                                        <path d="M8 16A8 8 0 1 0 8 0a8 8 0 0 0 0 16zm7-8A7 7 0 1 1 1 8a7 7 0 0 1 14 0z"/>
                                    </svg>
                                    {date_formatted}
                                </div>
                                <div class='content'>
                                    {content_html}
                                </div>
                            </div>
                        </div>
                        """
                    html += "</div>"
                    return html
                
                def get_updates_as_cards():
                    updates_data = get_updates()
                    return format_updates_as_cards(updates_data)
                
                view_btn.click(fn=get_updates_as_cards,
                             outputs=updates_container)
    
    return app


# Create and launch the interface
app = create_ui()
if __name__ == "__main__":
    app.launch()
