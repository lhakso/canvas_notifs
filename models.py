from datetime import datetime, timedelta, timezone

class Course:
    def __init__(self, name, course_id):
        self.course_id = course_id
        self.course_name = name.strip().lower()
        
class Assignment:
    def __init__(self, course, name, due_at=None):
        self.course = course
        self.name = name
        self.due_at = datetime.strptime(due_at, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc) if due_at else None
        self.near_due = self.is_near_due()
    
    def is_near_due(self) -> bool:
        if self.due_at is None:
            return False
        
        now = datetime.now(timezone.utc)
        day_before_due = self.due_at-timedelta(days=1)


        return now >= day_before_due and now < self.due_at