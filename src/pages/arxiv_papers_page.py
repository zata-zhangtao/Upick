import gradio as gr
import json
import sqlite3
from datetime import datetime, timedelta
from src.crawler.arxiv import ArxivCrawler
from src.log import get_logger
from src.db.arxiv_db import save_papers, get_papers, get_categories, delete_old_papers
from src.db.config import SUBSCRIPTIONS_DB_PATH

logger = get_logger("pages.arxiv_papers_page")

def create_ui():
    """Create Gradio interface for arXiv paper browsing
    创建arXiv论文浏览的Gradio界面
    """
    with gr.Blocks(css="""
        .paper-container {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }
        .paper-card {
            background: white;
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
            transition: all 0.2s ease;
            border: 1px solid #e5e7eb;
            overflow: hidden;
            display: flex;
            flex-direction: column;
            height: 100%;
        }
        .paper-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.15);
        }
        .paper-header {
            background: linear-gradient(135deg, #2563eb 0%, #3b82f6 100%);
            color: white;
            padding: 16px;
            font-weight: bold;
        }
        .paper-title {
            font-size: 1.1rem;
            line-height: 1.4;
            margin-bottom: 8px;
        }
        .paper-id {
            font-size: 0.8rem;
            opacity: 0.8;
        }
        .paper-body {
            padding: 16px;
            flex-grow: 1;
            display: flex;
            flex-direction: column;
        }
        .paper-abstract {
            color: #1f2937;
            line-height: 1.6;
            margin-bottom: 16px;
            flex-grow: 1;
            overflow: hidden;
            display: -webkit-box;
            -webkit-line-clamp: 5;
            -webkit-box-orient: vertical;
        }
        .paper-meta {
            color: #4b5563;
            font-size: 0.9rem;
            border-top: 1px solid #e5e7eb;
            padding-top: 12px;
        }
        .paper-authors {
            margin-bottom: 8px;
        }
        .paper-subjects {
            font-style: italic;
        }
        .paper-link {
            text-align: center;
            margin-top: 12px;
        }
        .paper-link a {
            display: inline-block;
            padding: 8px 16px;
            background-color: #3b82f6;
            color: white;
            text-decoration: none;
            border-radius: 6px;
            font-weight: 500;
            transition: background-color 0.2s;
        }
        .paper-link a:hover {
            background-color: #2563eb;
        }
        .empty-state {
            background-color: #f9fafb;
            border-radius: 8px;
            padding: 40px;
            text-align: center;
            color: #6b7280;
            grid-column: 1 / -1;
        }
        .empty-state svg {
            width: 64px;
            height: 64px;
            margin: 0 auto 16px;
            color: #9ca3af;
        }
        .filter-chip {
            display: inline-block;
            background: #e5e7eb;
            border-radius: 16px;
            padding: 4px 12px;
            margin-right: 8px;
            margin-bottom: 8px;
            font-size: 0.9rem;
            cursor: pointer;
            transition: all 0.2s;
        }
        .filter-chip:hover, .filter-chip.active {
            background: #3b82f6;
            color: white;
        }
        .category-card {
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
            padding: 12px;
            margin-bottom: 12px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            cursor: pointer;
            transition: all 0.2s;
        }
        .category-card:hover {
            background: #f3f4f6;
            transform: translateX(5px);
        }
        .category-name {
            font-weight: 500;
        }
        .timestamp {
            color: #6b7280;
            font-size: 0.9rem;
        }
        .stats-container {
            display: flex;
            gap: 20px;
            margin-bottom: 24px;
        }
        .stat-card {
            background: white;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
            padding: 20px;
            flex: 1;
            text-align: center;
            border: 1px solid #e5e7eb;
        }
        .stat-value {
            font-size: 2rem;
            font-weight: 600;
            color: #3b82f6;
            margin-bottom: 8px;
        }
        .stat-label {
            color: #6b7280;
            font-size: 0.9rem;
        }
        .tabs-container {
            margin-top: 20px;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
        }
    """) as app:
        gr.Markdown("# arXiv Papers Explorer") # title 标题
        
        # Create paper stats state
        paper_count_state = gr.State(0) # 论文数量状态
        category_count_state = gr.State(0) # 类别数量状态
        
        # Function to get database stats  获取数据库统计信息
        def get_stats():
            conn = sqlite3.connect(SUBSCRIPTIONS_DB_PATH) # connect to database  连接数据库
            c = conn.cursor()
            
            # Get paper count  获取论文数量
            c.execute("SELECT COUNT(*) FROM arxiv_papers")
            paper_count = c.fetchone()[0]

            print(f"paper_count: {paper_count}")
            
            # Get category count  获取类别数量
            c.execute("SELECT COUNT(*) FROM arxiv_categories")
            category_count = c.fetchone()[0]
            
            # Get latest paper date  获取最新论文日期
            c.execute("SELECT MAX(fetched_at) FROM arxiv_papers")
            latest_date = c.fetchone()[0] or "No papers"
            
            conn.close()
            
            return paper_count, category_count, latest_date
        
        with gr.Tabs() as tabs:
            # Create tabs  创建标签页
            dashboard_tab = gr.Tab("Dashboard") # 仪表盘标签页
            fetch_tab = gr.Tab("Fetch Papers") # 抓取论文标签页
            browse_tab = gr.Tab("Browse Papers") # 浏览论文标签页
            popular_tab = gr.Tab("Popular Categories") # 热门类别标签页
            manage_tab = gr.Tab("Data Management") # 数据管理标签页
            
            with dashboard_tab:
                # Stats cards
                with gr.Row(elem_classes="stats-container"):
                    with gr.Column(elem_classes="stat-card"):
                        paper_count = gr.Number(value=0, label="Total Papers", elem_classes="stat-value")
                        gr.Markdown("Papers in Database", elem_classes="stat-label")
                    
                    with gr.Column(elem_classes="stat-card"):
                        category_count = gr.Number(value=0, label="Categories", elem_classes="stat-value")
                        gr.Markdown("arXiv Categories", elem_classes="stat-label")
                    
                    with gr.Column(elem_classes="stat-card"):
                        latest_update = gr.Textbox(value="", label="Latest Update", elem_classes="stat-value")
                        gr.Markdown("Most Recent Paper", elem_classes="stat-label")
                
                # Quick actions
                with gr.Row():
                    with gr.Column():
                        gr.Markdown("## Quick Actions")
                        
                        with gr.Row():
                            fetch_ai_btn = gr.Button("Fetch AI Papers", variant="primary")
                            fetch_ml_btn = gr.Button("Fetch ML Papers", variant="primary")
                            fetch_cv_btn = gr.Button("Fetch CV Papers", variant="primary")
                            refresh_btn = gr.Button("Refresh Stats")
                            refresh_btn.click(
                                fn=lambda: get_stats(),
                                outputs=[paper_count, category_count, latest_update]
                                )
                
                # Recent papers preview
                with gr.Row():
                    gr.Markdown("## Recent Papers")
                    recent_papers = gr.HTML()
                    
                    def load_recent_papers(tab_index):
                        if tab_index == 0:  # Dashboard tab
                            papers = get_papers(limit=6)
                            return format_papers_as_cards(papers)
                        return gr.update()
                
                # Update stats function
                def update_stats(tab_index):
                    if tab_index == 0:  # Dashboard tab
                        paper_count, category_count, latest_date = get_stats()
                        return paper_count, category_count, latest_date
                    return gr.update(), gr.update(), gr.update()
                
                # Quick fetch buttons
                def fetch_category_papers(category_code):
                    crawler = ArxivCrawler()
                    url = f"https://arxiv.org/list/{category_code}/new"
                    papers = crawler.crawl(url)
                    if papers:
                        save_papers(papers, category_code)
                        return format_papers_as_cards(papers)
                    return "<div class='empty-state'>No papers found</div>"
                
                fetch_ai_btn.click(
                    fn=lambda: fetch_category_papers("cs.AI"),
                    outputs=recent_papers
                )
                
                fetch_ml_btn.click(
                    fn=lambda: fetch_category_papers("cs.LG"),
                    outputs=recent_papers
                )
                
                fetch_cv_btn.click(
                    fn=lambda: fetch_category_papers("cs.CV"),
                    outputs=recent_papers
                )
            
            with fetch_tab:
                with gr.Row():
                    with gr.Column(scale=3):
                        url_input = gr.Textbox(
                            label="arXiv URL", 
                            placeholder="Enter arXiv URL or leave empty for default",
                            value="https://arxiv.org/list/cs.AI/new"
                        )
                    with gr.Column(scale=1):
                        fetch_btn = gr.Button("Fetch Papers", variant="primary")
                
                status_output = gr.Textbox(label="Status")
                
                def fetch_papers(url):
                    try:
                        crawler = ArxivCrawler()
                        target_url = url if url else crawler.default_url
                        
                        logger.info(f"Fetching papers from: {target_url}")
                        papers = crawler.crawl(target_url)
                        
                        if papers:
                            # Extract category from URL
                            category = "cs.AI"  # Default category
                            if "list/" in target_url:
                                category_part = target_url.split("list/")[1].split("/")[0]
                                if category_part:
                                    category = category_part
                            
                            # Save papers to database
                            result = save_papers(papers, category)
                            return f"Successfully fetched {len(papers)} papers from {target_url}. {result}"
                        else:
                            return "No papers found. Please check the URL or try again later."
                    except Exception as e:
                        logger.error(f"Error fetching papers: {e}")
                        return f"Error: {str(e)}"
                
                fetch_btn.click(
                    fn=fetch_papers,
                    inputs=url_input,
                    outputs=status_output
                )
            
            with browse_tab:
                with gr.Row():
                    with gr.Column(scale=3):
                        search_input = gr.Textbox(
                            label="Search", 
                            placeholder="Search by title, author, or subject"
                        )
                    with gr.Column(scale=1):
                        view_btn = gr.Button("View Papers", variant="primary")
                
                with gr.Row():
                    with gr.Column(scale=2):
                        subject_filter = gr.Radio(
                            choices=["All Subjects", "Computer Science", "Physics", "Mathematics", "Other"],
                            label="Filter by Subject",
                            value="All Subjects"
                        )
                    with gr.Column(scale=1):
                        category_filter = gr.Dropdown(
                            choices=["All Categories", "cs.AI", "cs.CL", "cs.CV", "cs.LG", "cs.RO"],
                            label="Filter by Category",
                            value="All Categories"
                        )
                        
                        # Add limit selection
                        limit_slider = gr.Slider(
                            minimum=10, 
                            maximum=100, 
                            value=30, 
                            step=10, 
                            label="Results Limit"
                        )
                
                papers_container = gr.HTML(label="Papers")
                
                def format_papers_as_cards(papers):
                    if not papers or len(papers) == 0:
                        return """
                        <div class='empty-state'>
                            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                            </svg>
                            <h3 class="text-lg font-medium mb-2">No papers found</h3>
                            <p>Try fetching papers first or modify your search criteria.</p>
                        </div>
                        """
                    
                    html = "<div class='paper-container'>"
                    for paper in papers:
                        title = paper.get("title", "Untitled Paper")
                        abstract = paper.get("abstract", "No abstract available")
                        arxiv_id = paper.get("arxiv_id", "")
                        arxiv_url = paper.get("arxiv_url", "#")
                        
                        # Format authors
                        authors = paper.get("authors", [])
                        if len(authors) > 3:
                            authors_text = f"{authors[0]}, {authors[1]}, {authors[2]}, et al."
                        elif authors:
                            authors_text = ", ".join(authors)
                        else:
                            authors_text = "Unknown Authors"
                        
                        subjects = paper.get("subjects", "")
                        comments = paper.get("comments", "")
                        
                        # Format date
                        fetched_at = paper.get("fetched_at", "")
                        try:
                            date_obj = datetime.strptime(fetched_at, '%Y-%m-%d %H:%M:%S')
                            fetched_at = date_obj.strftime('%Y-%m-%d')
                        except (ValueError, TypeError):
                            fetched_at = ""
                        
                        html += f"""
                        <div class='paper-card'>
                            <div class='paper-header'>
                                <div class='paper-title'>{title}</div>
                                <div class='paper-id'>arXiv: {arxiv_id} | {fetched_at}</div>
                            </div>
                            <div class='paper-body'>
                                <div class='paper-abstract'>{abstract}</div>
                                <div class='paper-meta'>
                                    <div class='paper-authors'><strong>Authors:</strong> {authors_text}</div>
                                    <div class='paper-subjects'><strong>Subjects:</strong> {subjects}</div>
                                    {f"<div class='paper-comments'><strong>Comments:</strong> {comments}</div>" if comments else ""}
                                </div>
                                <div class='paper-link'>
                                    <a href="{arxiv_url}" target="_blank">Read on arXiv</a>
                                </div>
                            </div>
                        </div>
                        """
                    html += "</div>"
                    return html
                
                def view_papers(search_term, subject, category, limit):
                    try:
                        # Get category code
                        category_code = None
                        if category != "All Categories":
                            category_code = category
                        
                        # Get papers from database
                        papers = get_papers(
                            category=category_code,
                            search_term=search_term,
                            subject_filter=subject,
                            limit=int(limit)
                        )
                        
                        return format_papers_as_cards(papers)
                    except Exception as e:
                        logger.error(f"Error viewing papers: {e}")
                        return f"<div class='error'>Error: {str(e)}</div>"
                
                view_btn.click(
                    fn=view_papers,
                    inputs=[search_input, subject_filter, category_filter, limit_slider],
                    outputs=papers_container
                )
                
                # Update when search or filter changes
                search_input.change(
                    fn=view_papers,
                    inputs=[search_input, subject_filter, category_filter, limit_slider],
                    outputs=papers_container
                )
                
                subject_filter.change(
                    fn=view_papers,
                    inputs=[search_input, subject_filter, category_filter, limit_slider],
                    outputs=papers_container
                )
                
                category_filter.change(
                    fn=view_papers,
                    inputs=[search_input, subject_filter, category_filter, limit_slider],
                    outputs=papers_container
                )
                
                limit_slider.change(
                    fn=view_papers,
                    inputs=[search_input, subject_filter, category_filter, limit_slider],
                    outputs=papers_container
                )
                
                # Function to update category dropdown choices
                def update_categories(tab_index):
                    if tab_index == 2:  # Browse Papers tab
                        categories = get_categories()
                        category_choices = ["All Categories"]
                        for cat in categories:
                            category_choices.append(cat["category_code"])
                        return gr.update(choices=category_choices)
                    return gr.update()
            
            with popular_tab:
                gr.Markdown("## Popular arXiv Categories")
                
                with gr.Row():
                    categories = [
                        ("cs.AI", "Artificial Intelligence"),
                        ("cs.CL", "Computation and Language"),
                        ("cs.CV", "Computer Vision"),
                        ("cs.LG", "Machine Learning"),
                        ("cs.RO", "Robotics"),
                        ("stat.ML", "Statistics - Machine Learning"),
                        ("physics.comp-ph", "Computational Physics"),
                        ("cs.NE", "Neural and Evolutionary Computing"),
                        ("cs.CY", "Computers and Society"),
                        ("cs.HC", "Human-Computer Interaction")
                    ]
                    
                    for i in range(0, len(categories), 2):
                        with gr.Column():
                            for j in range(i, min(i+2, len(categories))):
                                code, name = categories[j]
                                url = f"https://arxiv.org/list/{code}/recent"
                                with gr.Group(elem_classes="category-card"):
                                    with gr.Row():
                                        with gr.Column(scale=3):
                                            gr.Markdown(f"**{name}**  \n`{code}`")
                                        with gr.Column(scale=1):
                                            fetch_btn = gr.Button("Fetch", size="sm")
                                            fetch_btn.click(
                                                fn=lambda url=url: url,
                                                outputs=url_input
                                            )
            
            with manage_tab:
                gr.Markdown("## Manage arXiv Papers Database")
                
                with gr.Row():
                    with gr.Column():
                        gr.Markdown("### Data Cleanup")
                        
                        with gr.Row():
                            retention_slider = gr.Slider(
                                minimum=1,
                                maximum=180,
                                value=30,
                                step=1,
                                label="Days to Keep Papers"
                            )
                            cleanup_btn = gr.Button("Clean Up Old Data", variant="secondary")
                        
                        cleanup_status = gr.Textbox(label="Cleanup Status")
                        
                        def do_cleanup(days):
                            try:
                                result = delete_old_papers(int(days))
                                return result
                            except Exception as e:
                                logger.error(f"Error cleaning up: {e}")
                                return f"Error: {str(e)}"
                        
                        cleanup_btn.click(
                            fn=do_cleanup,
                            inputs=retention_slider,
                            outputs=cleanup_status
                        )
                
                with gr.Row():
                    with gr.Column():
                        gr.Markdown("### Category Management")
                        
                        categories_table = gr.Dataframe(
                            headers=["Category", "Name", "Last Updated"],
                            datatype=["str", "str", "str"],
                            row_count=10
                        )
                        
                        refresh_cat_btn = gr.Button("Refresh Categories")
                        
                        def load_categories_table(tab_index):
                            if tab_index == 4:  # Data Management tab
                                categories = get_categories()
                                table_data = []
                                for cat in categories:
                                    table_data.append([
                                        cat["category_code"],
                                        cat["category_name"],
                                        cat["last_fetched_at"]
                                    ])
                                return table_data
                            return gr.update()
                        
                        refresh_cat_btn.click(
                            fn=lambda: load_categories_table(4),  # 手动调用时模拟 tab 4
                            outputs=categories_table
                        )
        
        # Set up tab selection event handlers
        tabs.select(
            fn=load_recent_papers,
            outputs=recent_papers
        )
        
        tabs.select(
            fn=update_stats,
            outputs=[paper_count, category_count, latest_update]
        )
        
        tabs.select(
            fn=update_categories,
            outputs=category_filter
        )
        
        tabs.select(
            fn=load_categories_table,
            outputs=categories_table
        )
    
    return app

app = create_ui()
if __name__ == "__main__":
    app.launch()