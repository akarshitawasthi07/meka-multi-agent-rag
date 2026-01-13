import json
import os
import uuid
from datetime import datetime

HISTORY_FILE = "query_history.json"

def get_history():
    if not os.path.exists(HISTORY_FILE):
        return {}
    try:
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_history(history):
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=4)

def add_query_to_history(query_id, query_data):
    history = get_history()
    history[query_id] = {
        **query_data,
        "timestamp": datetime.now().isoformat()
    }
    save_history(history)

def update_query_status(query_id, status, result=None):
    history = get_history()
    if query_id in history:
        history[query_id]["status"] = status
        if result:
            history[query_id]["result"] = result
        save_history(history)

def get_query_by_id(query_id):
    history = get_history()
    return history.get(query_id)

def delete_history_item(query_id):
    history = get_history()
    if query_id in history:
        del history[query_id]
        save_history(history)
        return True
    return False

def get_all_history():
    history = get_history()
    # Return as list sorted by timestamp
    return sorted(history.values(), key=lambda x: x.get("timestamp", ""), reverse=True)
