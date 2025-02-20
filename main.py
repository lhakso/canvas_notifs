import requests
from models import Course, Assignment
from zoneinfo import ZoneInfo
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv
import os

API_TOKEN = os.getenv("API_TOKEN")
BASE_URL = os.getenv("BASE_URL")
PUSHOVER_USER_KEY = os.getenv("PUSHOVER_USER_KEY")
PUSHOVER_API_TOKEN = os.getenv("PUSHOVER_API_TOKEN")
PUSHOVER_URL = "https://api.pushover.net/1/messages.json"

headers = {"Authorization": f"Bearer {API_TOKEN}"}

response = requests.get(f"{BASE_URL}/courses?per_page=20", headers=headers).json()

courses = [Course(name=course["name"], course_id=course["id"]) for course in response]

all_assignments = []
for course in courses:
    if course.course_name in (
        "25sp empirical engagement - sec2",
        "25sp emergence of states and cities",
        "25sp principles of econ: microecon",
        "queer writing",
    ):
        class_assignments = requests.get(
            f"{BASE_URL}/courses/{course.course_id}/assignments?per_page=100",
            headers=headers,
        ).json()
        current_group = [
            Assignment(
                course=course.course_name,
                name=assignment.get("name"),
                due_at=assignment.get("due_at"),
            )
            for assignment in class_assignments
        ]
        all_assignments.extend(current_group)


def format_date(due_at):
    if due_at is None:
        return "No due date"
    est = ZoneInfo("America/New_York")
    due_at_est = due_at.astimezone(est)
    now_est = datetime.now(timezone.utc).astimezone(est).date()

    if due_at_est.date() == now_est:
        return f"Today at {due_at_est.strftime('%-I:%M %p')}"
    elif due_at_est.date() == now_est + timedelta(days=1):
        return f"Tomorrow at {due_at_est.strftime('%-I:%M %p')}"
    else:
        return due_at_est.strftime("%A, %b %d at %-I:%M %p")


def send_notif(assignment):
    data = {
        "token": PUSHOVER_API_TOKEN,
        "user": PUSHOVER_USER_KEY,
        "message": f"{assignment.name}\nCourse: {assignment.course}\nDue: {format_date(assignment.due_at)}",
        "title": "Assignment Due",
        "priority": 1,
    }
    response = requests.post(PUSHOVER_URL, data=data)
    print(f"Sent notification for {assignment.name}, Response: {response.text}")


for assignment in all_assignments:
    if assignment.near_due:
        send_notif(assignment)
