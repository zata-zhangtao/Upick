import gradio as gr
import sqlite3
from datetime import datetime
from src.db import add_subscription, refresh_content, get_updates, save_summary_feedback
import json
from src.log import get_logger
from src.agent.incremental_learning import IncrementalLearner
from src.agent.summary import SubscriptionAgent

logger = get_logger("pages.gradio_page")

# Initialize the learner and agent
learner = IncrementalLearner()
subscription_agent = SubscriptionAgent()

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
        .url-list {
            margin-top: 4px;
            margin-left: 16px;
            font-size: 0.875rem;
        }
        .url-link {
            display: block;
            color: #3b82f6;
            text-decoration: none;
            margin-bottom: 2px;
            word-break: break-all;
        }
        .url-link:hover {
            text-decoration: underline;
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
        .feedback-container {
            margin-top: 16px;
            padding: 16px;
            background-color: #f9fafb;
            border-radius: 8px;
            border: 1px solid #e5e7eb;
        }
        .rating-container {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 12px;
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
                
                # State to store the current updates data
                updates_data_state = gr.State([])
                
                # Add feedback components
                with gr.Accordion("提供反馈", open=False) as feedback_accordion:
                    gr.Markdown("### 给内容摘要评分")
                    
                    with gr.Row():
                        update_selector = gr.Dropdown(
                            choices=[],
                            label="选择要评分的内容",
                            interactive=True
                        )
                    
                    with gr.Row():
                        feedback_rating = gr.Slider(
                            minimum=0,
                            maximum=1,
                            value=0.8,
                            step=0.1,
                            label="质量评分 (0-1)"
                        )
                    
                    feedback_comment = gr.Textbox(
                        label="反馈意见 (可选)",
                        placeholder="请输入您对此摘要的意见或建议..."
                    )
                    
                    submit_feedback_btn = gr.Button("提交反馈", variant="primary")
                    feedback_status = gr.Textbox(label="反馈状态")
                
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
                            title = update[0]
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
                            url_list = changes.get('url_list', [])
                            if isinstance(content, list):
                                content_html = '<ol>'
                                for i, point in enumerate(content):
                                    content_html += f'<li>{point}'
                                    # 添加对应的URL列表
                                    if i < len(url_list) and url_list[i]:
                                        content_html += '<div class="url-list">'
                                        for url in url_list[i]:
                                            content_html += f'<a href="{url}" target="_blank" class="url-link">{url}</a>'
                                        content_html += '</div>'
                                    content_html += '</li>'
                                content_html += '</ol>'
                            else:
                                content_html = content
                            
                            html += f"""
                            <div class='card'>
                                <div class='card-header'>
                                    <a href="{title}" target="_blank" title="Visit original page">{title}</a>
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


                    
                    # Update dropdown options for feedback
                    update_options = []
                    for i, update in enumerate(updates_data):
                        if isinstance(update, (list, tuple)) and len(update) >= 1:
                            url = update[0]
                            label = f"{i+1}. {url[:40]}..." if len(url) > 40 else f"{i+1}. {url}"
                            update_options.append(label)
                    
                    return format_updates_as_cards(updates_data), updates_data, gr.update(choices=update_options)
                
                view_btn.click(
                    fn=get_updates_as_cards,
                    inputs=time_range,
                    outputs=[updates_container, updates_data_state, update_selector]
                )
                
                # 使时间范围选择实时更新
                time_range.change(
                    fn=get_updates_as_cards,
                    inputs=time_range,
                    outputs=[updates_container, updates_data_state, update_selector]
                )
                
                # Handle feedback submission
                def submit_feedback(selection, rating, comment, updates_data):
                    if not selection or not updates_data:
                        return "请选择要评分的内容"
                    
                    try:
                        # Extract index from selection (format: "1. url...")
                        index = int(selection.split('.')[0]) - 1
                        
                        if index < 0 or index >= len(updates_data):
                            return "无效的选择"
                        
                        update = updates_data[index]
                        url = update[0]
                        diff_details = update[3]  # Get the diff_details from the updates_data
                        summary_id = update[5]  # Get the summary_id from the updates_data
                        
                        # Save feedback using the database function
                        result = save_summary_feedback(
                            summary_id=summary_id,
                            feedback_score=rating,
                            feedback_comment=comment
                        )
                        
                        return f"{result} - URL: {url}, 评分: {rating}"
                        
                    except Exception as e:
                        logger.error(f"提交反馈时出错: {str(e)}")
                        return f"提交反馈时出错: {str(e)}"
                
                submit_feedback_btn.click(
                    fn=submit_feedback,
                    inputs=[update_selector, feedback_rating, feedback_comment, updates_data_state],
                    outputs=feedback_status
                )
            
            with gr.Tab("Learning Stats"):
                gr.Markdown("## 增量学习统计")
                
                refresh_stats_btn = gr.Button("刷新统计", variant="secondary")
                
                with gr.Row():
                    total_examples = gr.Number(label="总学习样本数", value=0)
                    avg_feedback = gr.Number(label="平均反馈分数", value=0)
                
                with gr.Row():
                    vocab_size = gr.Number(label="词汇量", value=0)
                    last_update = gr.Textbox(label="最后更新时间", value="")
                
                # Get learning statistics
                def get_learning_stats():
                    stats = subscription_agent.get_learning_stats()
                    
                    return (
                        stats.get("total_examples", 0),
                        stats.get("average_feedback", 0),
                        stats.get("vocabulary_size", 0),
                        stats.get("latest_update", "从未更新")
                    )
                
                refresh_stats_btn.click(
                    fn=get_learning_stats,
                    inputs=[],
                    outputs=[total_examples, avg_feedback, vocab_size, last_update]
                )
                
                # Add example list and visualization
                gr.Markdown("### 高质量学习示例")
                
                # Example retrieval
                def get_high_quality_examples():
                    examples = learner.examples
                    
                    # Sort by feedback score (highest first)
                    examples.sort(key=lambda ex: ex.feedback_score, reverse=True)
                    
                    # Take top 10 examples
                    top_examples = examples[:10] if len(examples) > 10 else examples
                    
                    # Format examples for display
                    if not top_examples:
                        return "暂无学习示例数据"
                    
                    html = "<div style='max-height: 400px; overflow-y: auto;'>"
                    for i, ex in enumerate(top_examples):
                        html += f"""
                        <div style='margin-bottom: 20px; padding: 16px; border: 1px solid #e5e7eb; border-radius: 8px; background-color: white;'>
                            <div style='font-weight: bold; margin-bottom: 8px; display: flex; justify-content: space-between;'>
                                <span>示例 {i+1}</span>
                                <span style='color: {"#10b981" if ex.feedback_score >= 0.8 else "#f59e0b"};'>
                                    评分: {ex.feedback_score:.1f}
                                </span>
                            </div>
                            <div style='margin-bottom: 10px;'>
                                <div style='font-size: 0.875rem; color: #6b7280; margin-bottom: 4px;'>输入:</div>
                                <div style='padding: 8px; background-color: #f9fafb; border-radius: 4px; max-height: 100px; overflow-y: auto;'>
                                    {ex.input_text[:200]}...
                                </div>
                            </div>
                            <div>
                                <div style='font-size: 0.875rem; color: #6b7280; margin-bottom: 4px;'>输出:</div>
                                <div style='padding: 8px; background-color: #f9fafb; border-radius: 4px;'>
                                    {ex.output_text}
                                </div>
                            </div>
                            <div style='font-size: 0.75rem; color: #9ca3af; margin-top: 10px;'>
                                {ex.timestamp}
                            </div>
                        </div>
                        """
                    html += "</div>"
                    return html
                
                with gr.Row():
                    refresh_examples_btn = gr.Button("查看高质量示例", variant="secondary")
                    examples_display = gr.HTML(label="高质量示例")
                
                refresh_examples_btn.click(
                    fn=get_high_quality_examples,
                    inputs=[],
                    outputs=examples_display
                )
                
                # Performance chart
                gr.Markdown("### 反馈分数分布")
                
                def get_feedback_distribution():
                    examples = learner.examples
                    if not examples:
                        return "暂无学习示例数据"
                    
                    # Count examples in each score range
                    bins = {
                        "0.0-0.2": 0,
                        "0.2-0.4": 0,
                        "0.4-0.6": 0,
                        "0.6-0.8": 0,
                        "0.8-1.0": 0
                    }
                    
                    for ex in examples:
                        score = ex.feedback_score
                        if score < 0.2:
                            bins["0.0-0.2"] += 1
                        elif score < 0.4:
                            bins["0.2-0.4"] += 1
                        elif score < 0.6:
                            bins["0.4-0.6"] += 1
                        elif score < 0.8:
                            bins["0.6-0.8"] += 1
                        else:
                            bins["0.8-1.0"] += 1
                    
                    # Create bar chart
                    import matplotlib.pyplot as plt
                    import io
                    import base64
                    
                    fig, ax = plt.subplots(figsize=(8, 4))
                    colors = ['#f87171', '#fbbf24', '#34d399', '#60a5fa', '#818cf8']
                    
                    ax.bar(bins.keys(), bins.values(), color=colors)
                    ax.set_xlabel('反馈分数区间')
                    ax.set_ylabel('示例数量')
                    ax.set_title('反馈分数分布')
                    
                    # Save to base64 string
                    buf = io.BytesIO()
                    plt.savefig(buf, format='png')
                    buf.seek(0)
                    img_str = base64.b64encode(buf.read()).decode('utf-8')
                    
                    plt.close()
                    
                    html = f"<img src='data:image/png;base64,{img_str}' style='width:100%;'>"
                    return html
                
                with gr.Row():
                    refresh_chart_btn = gr.Button("查看分数分布", variant="secondary")
                    chart_display = gr.HTML(label="分数分布")
                
                refresh_chart_btn.click(
                    fn=get_feedback_distribution,
                    inputs=[],
                    outputs=chart_display
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

            with gr.Tab("Configuration"):
                gr.Markdown("## 应用配置设置")
                
                # 初始化配置管理器
                from src.services.configmanager import ConfigManager
                config_manager = ConfigManager()
                
                # 获取当前配置
                current_config = config_manager.get_config()
                if current_config is None:
                    current_config = {}
                app_config = current_config.get('app', {})
                
                # 设置默认值
                default_values = {
                    'log_level': 'debug',
                    'provider': 'ZHIPU',
                    'model': 'GLM-Z1-Flash',
                    'base_url': '',
                    'api_key': ''
                }
                
                with gr.Row():
                    log_level = gr.Dropdown(
                        choices=["debug", "info", "warning", "error", "critical"],
                        label="日志级别",
                        value=app_config.get('log_level', default_values['log_level'])
                    )
                    provider = gr.Dropdown(
                        choices=["DASHSCOPE", "ZHIPU"],
                        label="接口厂商",
                        value=app_config.get('provider', default_values['provider'])
                    )
                
                with gr.Row():
                    model = gr.Textbox(
                        label="默认模型",
                        value=app_config.get('model', default_values['model'])
                    )
                    base_url = gr.Textbox(
                        label="Base URL",
                        value=app_config.get('base_url', default_values['base_url'])
                    )
                
                with gr.Row():
                    api_key = gr.Textbox(
                        label="API密钥",
                        value=app_config.get('api_key', default_values['api_key']),
                        type="password"
                    )
                
                save_config_btn = gr.Button("保存配置")
                config_output = gr.Textbox(label="配置状态")
                
                def save_config(log_level_val, provider_val, model_val, base_url_val, api_key_val):
                    try:
                        # 准备配置数据
                        app_config = {
                            "log_level": log_level_val,
                            "provider": provider_val,
                            "model": model_val,
                            "base_url": base_url_val,
                            "api_key": api_key_val
                        }
                        
                        # 使用ConfigManager保存配置
                        if config_manager.save_config(app_config):
                            return "配置已成功保存！"
                        else:
                            return "保存配置失败，请查看日志获取详细信息"
                    except Exception as e:
                        logger.error(f"保存配置时出错: {str(e)}")
                        return f"保存配置时出错: {str(e)}"
                
                save_config_btn.click(
                    fn=save_config,
                    inputs=[log_level, provider, model, base_url, api_key],
                    outputs=config_output
                )
            
    
    return app


# Create and launch the interface
app = create_ui()
if __name__ == "__main__":
    app.launch()
