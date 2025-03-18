import gradio as gr
import sqlite3
from datetime import datetime
from src.db import add_subscription, refresh_content, get_updates
import json
from src.log import get_logger
logger = get_logger("pages.gradio_page")

def create_ui():
    """Create Gradio interface for subscription management"""
    with gr.Blocks(css="""
        # ... (保持原有的 CSS 不变)
    """) as app:
        gr.Markdown("# Subscription Manager")
        
        with gr.Tabs():
            with gr.Tab("Add/Refresh"):
                # ... (保持原有的 Add/Refresh 标签页内容不变)
                










            
            with gr.Tab("Updates"):
                with gr.Row():
                    time_range = gr.Dropdown(
                        choices=["最近1小时", "最近24小时", "最近7天", "最近30天", "全部"],
                        label="显示时间范围",
                        value="最近24小时"
                    )
                    view_btn = gr.Button("View Updates", variant="primary")
                
                updates_container = gr.HTML(label="Content Updates")
                
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
                        if isinstance(update, (list, tuple)) and len(update) >= 3:
                            url = update[0]
                            updated_at = update[1]
                            try:
                                changes = json.loads(update[2]) if isinstance(update[2], (str, bytes, bytearray)) else {}
                            except json.JSONDecodeError:
                                changes = {'key_points': update[2]}
                            
                            date_formatted = updated_at
                            if isinstance(updated_at, str):
                                try:
                                    date_formatted = datetime.fromisoformat(updated_at).strftime("%Y-%m-%d %H:%M:%S")
                                except ValueError:
                                    pass
                            
                            content = changes.get('key_points', '')
                            if isinstance(content, list):
                                content_html = '<ol>' + ''.join([f'<li>{point}</li>' for point in content]) + '</ol>'
                            else:
                                content_html = content
                            
                            html += f"""
                            <div class='card'>
                                <div class='card-header'>
                                    <a href="{url}" target="_blank" title="Visit original page">{url}</a>
                                    <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" fill="currentColor" viewBox="0 0 16 16" style="display: inline-block; vertical-align: middle; margin-left: 5px;">
                                        <path fill-rule="evenodd" d="M8.636 3.5a.5.5 0 0 0-.5-.5H1.5A1.5 1.5 0 0 0 0 4.5v10A1.5 1.5 0 0 0 1.5 16h10a1.5 1.5 0 0 0 1.5-1.5V7.864a.5.5 0 0 0-1 0V14.5a.5.5 0 0 1-.5.5h-10a.5.5 0 0 1-.5-.5v-10a.5.5 0 0 1 .5-.5h6.636a.5.5 0 0 0 .5-.5z"/>
                                        <path fill-rule="evenodd" d="M16 .5a.5.5 0 0 0-.5-.5h-5a.5.5 0 0 0 0 1h3.793L6.146 9.146a.5.5 0 1 0 .708.708L15 1.707V5.5a.5.5 0 0 0 1 0v-5z"/>
                                    </svg>
                                </div>
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
                
                def get_updates_as_cards(time_range_selection):
                    from datetime import timedelta
                    
                    logger.debug(f"点击获取更新内容 : click get updates with range {time_range_selection}")
                    
                    # 根据选择确定时间范围
                    now = datetime.now()
                    if time_range_selection == "最近1小时":
                        time_filter = now - timedelta(hours=1)
                    elif time_range_selection == "最近24小时":
                        time_filter = now - timedelta(hours=24)
                    elif time_range_selection == "最近7天":
                        time_filter = now - timedelta(days=7)
                    elif time_range_selection == "最近30天":
                        time_filter = now - timedelta(days=30)
                    else:  # "全部"
                        time_filter = None
                    
                    # 获取更新数据
                    updates_data = get_updates()
                    
                    # 过滤时间范围
                    if time_filter:
                        filtered_updates = []
                        for update in updates_data:
                            if isinstance(update, (list, tuple)) and len(update) >= 2:
                                updated_at = update[1]
                                try:
                                    update_time = datetime.fromisoformat(updated_at)
                                    if update_time >= time_filter:
                                        filtered_updates.append(update)
                                except (ValueError, TypeError):
                                    continue
                        updates_data = filtered_updates
                    
                    return format_updates_as_cards(updates_data)
                
                view_btn.click(
                    fn=get_updates_as_cards,
                    inputs=time_range,
                    outputs=updates_container
                )
                
                # 使时间范围选择实时更新
                time_range.change(
                    fn=get_updates_as_cards,
                    inputs=time_range,
                    outputs=updates_container
                )
            














            
            with gr.Tab("Schedule Settings"):
                # ... (保持原有的 Schedule Settings 标签页内容不变)

    return app

# Create and launch the interface
app = create_ui()
if __name__ == "__main__":
    app.launch()