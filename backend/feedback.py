import json
from pathlib import Path

FILE = Path("data/feedback.json")

def save_feedback(username, rating, comments):
    FILE.parent.mkdir(parents=True, exist_ok=True)

    if FILE.exists():
        data = json.loads(FILE.read_text())
    else:
        data = []

    data.append({
        "username": username,
        "rating": rating,
        "comments": comments
    })

    FILE.write_text(json.dumps(data, indent=2))
def load_feedback():
    if FILE.exists():
        return json.loads(FILE.read_text())
    return []
def get_average_rating():
    feedbacks = load_feedback()
    if not feedbacks:
        return 0
    total = sum(fb["rating"] for fb in feedbacks)
    return total / len(feedbacks)
def get_feedback_count():
    feedbacks = load_feedback()
    return len(feedbacks)
def get_all_feedback():
    return load_feedback()
def clear_feedback():
    if FILE.exists():
        FILE.unlink()
    FILE.write_text("[]")
    return True
def export_feedback_to_json(export_path: str):
    feedbacks = load_feedback()
    with open(export_path, "w") as f:
        json.dump(feedbacks, f, indent=2)
    return True
def export_feedback_to_csv(export_path: str):
    import csv
    feedbacks = load_feedback()
    if not feedbacks:
        return False

    keys = feedbacks[0].keys()
    with open(export_path, "w", newline='', encoding='utf-8') as f:
        dict_writer = csv.DictWriter(f, fieldnames=keys)
        dict_writer.writeheader()
        dict_writer.writerows(feedbacks)
    return True
def summarize_feedback():
    feedbacks = load_feedback()
    if not feedbacks:
        return "No feedback available."

    avg_rating = get_average_rating()
    count = get_feedback_count()
    comments = [fb["comments"] for fb in feedbacks if fb["comments"].strip()]

    summary = f"Total Feedbacks: {count}\nAverage Rating: {avg_rating:.2f}\n\nComments:\n"
    for comment in comments:
        summary += f"- {comment}\n"

    return summary
    return summary