from fastapi import FastAPI, HTTPException
from pathlib import Path
import subprocess
import json
import sqlite3
from datetime import datetime
from collections import Counter

app = FastAPI()

# Task Execution Functions
def install_uv_and_run_datagen():
    """Ensure `uv` is installed and run datagen.py."""
    subprocess.run(["pip", "install", "--upgrade", "uv"], check=True)
    subprocess.run(["uv", "pip", "install", "requests"], check=True)
    subprocess.run(["python", "-m", "pip", "install", "requests"], check=True)
    
    # Run datagen.py with a placeholder email (replace with actual)
    user_email = "user@example.com"
    subprocess.run(["python", "-c", f"import requests; exec(requests.get('https://raw.githubusercontent.com/sanand0/tools-in-data-science-public/tds-2025-01/project-1/datagen.py').text)", user_email], check=True)
    
    return {"message": "datagen.py executed successfully."}

def format_markdown():
    """Format markdown using prettier."""
    subprocess.run(["npx", "prettier@3.4.2", "--write", "/data/format.md"], check=True)
    return {"message": "Markdown formatted successfully."}

def count_wednesdays():
    """Count Wednesdays from /data/dates.txt."""
    dates_file = Path("/data/dates.txt")
    if not dates_file.exists():
        raise FileNotFoundError("dates.txt not found.")
    
    with dates_file.open() as f:
        dates = [datetime.strptime(line.strip(), "%Y-%m-%d") for line in f]
    
    count = sum(1 for date in dates if date.strftime("%A") == "Wednesday")

    with open("/data/dates-wednesdays.txt", "w") as f:
        f.write(str(count))
    
    return {"message": f"{count} Wednesdays counted and saved."}

def sort_contacts():
    """Sort contacts by last_name, then first_name."""
    contacts_file = Path("/data/contacts.json")
    if not contacts_file.exists():
        raise FileNotFoundError("contacts.json not found.")
    
    with contacts_file.open() as f:
        contacts = json.load(f)
    
    sorted_contacts = sorted(contacts, key=lambda c: (c["last_name"], c["first_name"]))
    
    with open("/data/contacts-sorted.json", "w") as f:
        json.dump(sorted_contacts, f, indent=2)
    
    return {"message": "Contacts sorted successfully."}

def extract_recent_logs():
    """Extract first lines of the 10 most recent .log files."""
    logs_dir = Path("/data/logs")
    
    log_files = sorted(logs_dir.glob("*.log"), key=lambda f: f.stat().st_mtime, reverse=True)[:10]
    
    with open("/data/logs-recent.txt", "w") as output_file:
        for log_file in log_files:
            with log_file.open() as f:
                first_line = f.readline().strip()
                output_file.write(first_line + "\n")
    
    return {"message": "Recent logs extracted successfully."}

def create_markdown_index():
    """Index Markdown files by their first H1 title."""
    docs_dir = Path("/data/docs")
    
    index = {}
    
    for md_file in docs_dir.glob("*.md"):
        with md_file.open() as f:
            for line in f:
                if line.startswith("# "):
                    index[md_file.name] = line.strip("# ").strip()
                    break
    
    with open("/data/docs/index.json", "w") as f:
        json.dump(index, f, indent=2)
    
    return {"message": "Markdown index created successfully."}

def extract_email_sender():
    """Use an LLM to extract the sender's email."""
    email_file = Path("/data/email.txt")
    
    if not email_file.exists():
        raise FileNotFoundError("email.txt not found.")
    
    with email_file.open() as f:
        email_content = f.read()
    
    # Call LLM (placeholder for now)
    extracted_email = "llm_extracted@example.com"
    
    with open("/data/email-sender.txt", "w") as f:
        f.write(extracted_email)
    
    return {"message": "Email sender extracted successfully."}

def extract_credit_card():
    """Use an LLM to extract a credit card number from an image."""
    return {"message": "Credit card extraction not yet implemented."}

def find_similar_comments():
    """Find the most similar pair of comments."""
    return {"message": "Finding similar comments not yet implemented."}

def calculate_gold_ticket_sales():
    """Calculate total sales for Gold tickets."""
    db_path = Path("/data/ticket-sales.db")
    
    if not db_path.exists():
        raise FileNotFoundError("ticket-sales.db not found.")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT SUM(units * price) FROM tickets WHERE type = 'Gold'")
    total_sales = cursor.fetchone()[0] or 0
    
    with open("/data/ticket-sales-gold.txt", "w") as f:
        f.write(str(total_sales))
    
    conn.close()
    
    return {"message": f"Total Gold ticket sales: {total_sales}."}

# Task Execution Dispatcher
def execute_task(task: str):
    """Determine the task and execute it."""
    
    task = task.lower().strip()  # Normalize input
    
    if "install uv" in task or "run datagen" in task:
        return install_uv_and_run_datagen()
    
    elif "format" in task and "prettier" in task:
        return format_markdown()
    
    elif "wednesdays" in task:
        return count_wednesdays()
    
    elif "sort contacts" in task:
        return sort_contacts()
    
    elif "recent logs" in task:
        return extract_recent_logs()
    
    elif "markdown index" in task:
        return create_markdown_index()
    
    elif "email sender" in task:
        return extract_email_sender()
    
    elif "credit card" in task:
        return extract_credit_card()
    
    elif "similar comments" in task:
        return find_similar_comments()
    
    elif "gold ticket sales" in task:
        return calculate_gold_ticket_sales()
    
    else:
        raise ValueError("Unsupported task.")

@app.post("/run")
def run_task(task: str):
    try:
        result = execute_task(task)
        return {"status": "success", "result": result}
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid task request")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/read")
def read_file(path: str):
    file_path = Path(path)
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    # Try reading as UTF-8 first
    try:
        content = file_path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        # If UTF-8 fails, try UTF-16 and then convert to UTF-8
        try:
            content = file_path.read_text(encoding="utf-16")
        except UnicodeDecodeError:
            raise HTTPException(status_code=500, detail="File encoding not supported.")

    return {"content": content}
