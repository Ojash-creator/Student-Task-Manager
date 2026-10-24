"""Load a sample dataset: 64 students x 5 tasks each (320 tasks) across 10 subjects.
Dates are relative to today, so overdue and upcoming tasks always appear.
Also saves the dataset as sample_tasks.csv.
Usage:  python seed.py          -> adds sample data only if the table is empty
        python seed.py --reset  -> deletes all tasks first, then adds sample data
"""
import csv
import random
import sqlite3
import sys
from datetime import date, timedelta
from itertools import product
from app import DB, init_db

random.seed(42)  # same dataset every time
SUBJECTS = ["Data Structures", "DBMS", "Operating Systems", "Computer Networks", "Python Programming",
            "Web Technology", "Software Engineering", "Discrete Mathematics", "Computer Architecture",
            "Technical Communication"]
KINDS = [("Assignment", ["Low", "Medium"]), ("Lab Record", ["Low", "Medium"]), ("Quiz", ["Medium", "High"]),
         ("Mini Project", ["Medium", "High"]), ("Exam Preparation", ["High"])]
FIRST = ["Aarav", "Vivaan", "Aditya", "Arjun", "Rohan", "Karthik", "Sai", "Ravi", "Ananya", "Priya", "Sneha",
         "Divya", "Meera", "Kavya", "Ishita", "Neha", "Rahul", "Varun", "Harsh", "Pooja", "Nikhil", "Sanjana",
         "Tanvi", "Manish"]
LAST = ["Sharma", "Reddy", "Patel", "Rao", "Kumar", "Singh", "Gupta", "Nair", "Verma", "Iyer", "Das", "Joshi"]

names = random.sample(list(product(FIRST, LAST)), 64)
students = [f"22CS{i:03d} - {f} {l}" for i, (f, l) in enumerate(names, start=1)]

rows = []
for student in students:
    for subject in random.sample(SUBJECTS, 5):
        kind, prios = random.choice(KINDS)
        offset = random.randint(-14, 25)
        if offset < -3:
            done = random.random() < 0.8
        elif offset < 0:
            done = random.random() < 0.4
        else:
            done = random.random() < 0.15
        rows.append((f"{subject} {kind} {random.randint(1, 4)}", f"{kind} for {subject}", subject,
                     (date.today() + timedelta(days=offset)).isoformat(), random.choice(prios),
                     "Completed" if done else "Pending", student))

init_db()
with open("sample_tasks.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["title", "description", "subject", "due_date", "priority", "status", "student"])
    w.writerows(rows)
with sqlite3.connect(DB) as conn:
    if "--reset" in sys.argv:
        conn.execute("DELETE FROM tasks")
    if conn.execute("SELECT COUNT(*) FROM tasks").fetchone()[0] == 0:
        conn.executemany("INSERT INTO tasks (title, description, subject, due_date, priority, status, student) "
                         "VALUES (?, ?, ?, ?, ?, ?, ?)", rows)
        print(f"Inserted {len(rows)} tasks for {len(students)} students across {len(SUBJECTS)} subjects.")
    else:
        print("Table already has tasks. Use: python seed.py --reset")
