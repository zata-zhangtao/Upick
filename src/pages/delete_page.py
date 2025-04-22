import gradio as gr
import sqlite3
from typing import List, Tuple
from src.db.config import SUBSCRIPTIONS_DB_PATH
from src.log import get_logger

logger = get_logger("pages.delete_page")

def get_table_names() -> List[str]:
    """Get all table names from the database"""
    conn = sqlite3.connect(SUBSCRIPTIONS_DB_PATH)
    c = conn.cursor()
    c.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in c.fetchall()]
    conn.close()
    return tables

def get_table_columns(table_name: str) -> List[str]:
    """Get column names for a specific table"""
    conn = sqlite3.connect(SUBSCRIPTIONS_DB_PATH)
    c = conn.cursor()
    c.execute(f"PRAGMA table_info({table_name})")
    columns = [row[1] for row in c.fetchall()]
    conn.close()
    return columns

def get_table_data(table_name: str) -> List[Tuple]:
    """Get all data from a specific table"""
    conn = sqlite3.connect(SUBSCRIPTIONS_DB_PATH)
    c = conn.cursor()
    c.execute(f"SELECT * FROM {table_name}")
    data = c.fetchall()
    conn.close()
    return data

def delete_record(table_name: str, record_id: int) -> str:
    """Delete a record from a table with proper foreign key handling"""
    conn = sqlite3.connect(SUBSCRIPTIONS_DB_PATH)
    c = conn.cursor()
    
    try:
        # Start transaction
        conn.execute("BEGIN TRANSACTION")
        
        # Handle foreign key relationships based on table
        if table_name == "subscriptions":
            # Delete related records in content_updates
            c.execute("""
                DELETE FROM content_updates 
                WHERE subscription_id = ?
            """, (record_id,))
            
            # Delete related records in contents
            c.execute("""
                DELETE FROM contents 
                WHERE subscription_id = ?
            """, (record_id,))
            
            # Delete the subscription
            c.execute("""
                DELETE FROM subscriptions 
                WHERE id = ?
            """, (record_id,))
            
        elif table_name == "content_updates":
            # Delete related summaries first
            c.execute("""
                DELETE FROM summaries 
                WHERE content_update_id = ?
            """, (record_id,))
            
            # Delete the content update
            c.execute("""
                DELETE FROM content_updates 
                WHERE id = ?
            """, (record_id,))
            
        elif table_name == "contents":
            # Delete the content
            c.execute("""
                DELETE FROM contents 
                WHERE id = ?
            """, (record_id,))
            
        elif table_name == "summaries":
            # Delete the summary
            c.execute("""
                DELETE FROM summaries 
                WHERE id = ?
            """, (record_id,))
        
        conn.commit()
        return f"Successfully deleted record {record_id} from {table_name}"
        
    except Exception as e:
        conn.rollback()
        logger.error(f"Error deleting record: {str(e)}")
        return f"Error deleting record: {str(e)}"
        
    finally:
        conn.close()

def create_delete_interface():
    """Create the Gradio interface for database deletion"""
    
    def update_table_info(table_name):
        if not table_name:
            return None, None, None
        
        columns = get_table_columns(table_name)
        data = get_table_data(table_name)
        
        # Create a formatted table display
        table_html = "<table style='width:100%; border-collapse: collapse;'>"
        # Header
        table_html += "<tr style='background-color: #f2f2f2;'>"
        for col in columns:
            table_html += f"<th style='border: 1px solid #ddd; padding: 8px;'>{col}</th>"
        table_html += "</tr>"
        
        # Data rows
        for row in data:
            table_html += "<tr>"
            for cell in row:
                table_html += f"<td style='border: 1px solid #ddd; padding: 8px;'>{cell}</td>"
            table_html += "</tr>"
        table_html += "</table>"
        
        return table_html, gr.Dropdown(choices=columns), gr.Dropdown(choices=[str(row[0]) for row in data])
    
    with gr.Blocks(title="Database Deletion Interface") as interface:
        gr.Markdown("# Database Deletion Interface")
        gr.Markdown("Select a table and record to delete. Please be careful with deletion operations!")
        
        with gr.Row():
            table_dropdown = gr.Dropdown(
                choices=get_table_names(),
                label="Select Table",
                interactive=True
            )
            
            refresh_btn = gr.Button("Refresh Data")
        
        with gr.Row():
            table_display = gr.HTML(label="Table Data")
        
        with gr.Row():
            id_column = gr.Dropdown(label="ID Column")
            record_id = gr.Dropdown(label="Record ID to Delete")
        
        with gr.Row():
            delete_btn = gr.Button("Delete Record", variant="stop")
            result = gr.Textbox(label="Operation Result")
        
        # Event handlers
        table_dropdown.change(
            fn=update_table_info,
            inputs=[table_dropdown],
            outputs=[table_display, id_column, record_id]
        )
        
        refresh_btn.click(
            fn=update_table_info,
            inputs=[table_dropdown],
            outputs=[table_display, id_column, record_id]
        )
        
        delete_btn.click(
            fn=delete_record,
            inputs=[table_dropdown, record_id],
            outputs=[result]
        ).then(
            fn=update_table_info,
            inputs=[table_dropdown],
            outputs=[table_display, id_column, record_id]
        )
    
    return interface

app = create_delete_interface()

if __name__ == "__main__":
    app.launch() 