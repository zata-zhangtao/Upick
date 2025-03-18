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
                gr.Markdown("## 定时刷新设置")
                
                # 使用 State 来控制显示状态
                schedule_type_state = gr.State(value="间隔刷新")
                
                with gr.Row():
                    schedule_type = gr.Radio(
                        ["间隔刷新", "每日定时"],
                        label="刷新类型",
                        value="间隔刷新"
                    )
                
                # 定义两个区域，使用 Column 并通过 visible 参数控制显示
                interval_column = gr.Column(visible=True)
                with interval_column:
                    hours_input = gr.Slider(0, 24, 1, label="间隔小时", step=1)
                    minutes_input = gr.Slider(0, 59, 0, label="间隔分钟", step=1)
                
                daily_column = gr.Column(visible=False)
                with daily_column:
                    hour_input = gr.Slider(0, 23, 0, label="小时 (0-23)", step=1)
                    minute_input = gr.Slider(0, 59, 0, label="分钟 (0-59)", step=1)
                
                # 更新 State 并返回可见性
                def update_schedule_type(selected_type):
                    return (
                        selected_type,  # 更新 schedule_type_state
                        gr.update(visible=selected_type == "间隔刷新"),  # interval_column 的可见性
                        gr.update(visible=selected_type == "每日定时")   # daily_column 的可见性
                    )
                
                schedule_type.change(
                    fn=update_schedule_type,
                    inputs=schedule_type,
                    outputs=[schedule_type_state, interval_column, daily_column]
                )
                
                # 保存设置按钮
                save_btn = gr.Button("保存定时设置")
                schedule_output = gr.Textbox(label="定时设置状态")
                
                # 保存设置的处理函数
                def save_schedule(sched_type, hours, minutes, hour, minute):
                    from src.services import add_refresh_job, add_daily_refresh_job, scheduler
                    
                    if scheduler is None or not scheduler.running:
                        return "错误：调度器未运行，请重启应用"
                    
                    if sched_type == "间隔刷新":
                        if hours == 0 and minutes == 0:
                            return "错误：间隔时间不能为零"
                        job_id = add_refresh_job(hours=hours, minutes=minutes)
                        return f"成功设置间隔刷新任务：每{hours}小时{minutes}分钟，任务ID: {job_id}"
                    else:
                        job_id = add_daily_refresh_job(hour=hour, minute=minute)
                        return f"成功设置每日定时刷新任务：每天{hour:02d}:{minute:02d}，任务ID: {job_id}"
                
                save_btn.click(
                    fn=save_schedule,
                    inputs=[schedule_type_state, hours_input, minutes_input, hour_input, minute_input],
                    outputs=schedule_output
                )
    
    return app


# Create and launch the interface
app = create_ui()
if __name__ == "__main__":
    app.launch()
