from datetime import date, timedelta
from app import decorate


def make(days, status="Pending"):
    due = (date.today() + timedelta(days=days)).isoformat()
    return {"due_date": due, "status": status}


def test_overdue():
    assert decorate([make(-1)])[0]["state"] == "overdue"


def test_urgent():
    assert decorate([make(0)])[0]["state"] == "urgent"
    assert decorate([make(2)])[0]["state"] == "urgent"


def test_normal():
    assert decorate([make(3)])[0]["state"] == "normal"


def test_completed_is_done():
    assert decorate([make(-5, "Completed")])[0]["state"] == "done"
