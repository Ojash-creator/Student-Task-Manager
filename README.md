# Student Task and Deadline Management System

A web application that helps students organize assignments, projects, lab records, quizzes and exams by tracking **deadlines, priorities and completion status** in one place. Built with Flask, SQLite and plain HTML/CSS/JavaScript, and managed with Git and GitHub.

---

## Table of Contents
1. [Overview](#overview)
2. [Problem Statement](#problem-statement)
3. [Objectives](#objectives)
4. [Features](#features)
5. [Technology Stack](#technology-stack)
6. [Project Structure](#project-structure)
7. [Database Design](#database-design)
8. [How Deadlines Are Calculated](#how-deadlines-are-calculated)
9. [Installation](#installation)
10. [Running the Application](#running-the-application)
11. [Sample Dataset](#sample-dataset)
12. [Using the Application](#using-the-application)
13. [Application Routes](#application-routes)
14. [Input Validation and Security](#input-validation-and-security)
15. [Testing Checklist](#testing-checklist)
16. [Deployment](#deployment)
17. [Screenshots](#screenshots)
18. [Git and GitHub Workflow](#git-and-github-workflow)
19. [Limitations](#limitations)
20. [Future Enhancements](#future-enhancements)

---

## Overview

Students handle many academic tasks at once, across several subjects, each with its own deadline. This application gives them a single dashboard to add tasks, see what is overdue or due soon, mark work as done, and view simple charts of their progress. All data is stored in a local SQLite database, so it is still there after the application restarts.

The project is deliberately simple: no login system, no external APIs and no heavy frameworks, so it is easy to understand, run, test and explain.

## Problem Statement

Students often track assignments and exams in notebooks, chat messages or memory. This leads to missed deadlines, poor prioritization and no clear view of overall progress. There is a need for a simple, free tool that stores all academic tasks in one place, highlights urgent and overdue work, and shows progress at a glance.

## Objectives

- Provide a central place to record academic tasks with a due date, priority, subject and status.
- Highlight overdue and urgent tasks with clear visual indicators.
- Show summary statistics and charts on a dashboard.
- Let users search and filter tasks by title, status, priority, subject and student.
- Store data reliably in SQLite with input validation and safe queries.
- Offer a clean, responsive interface that works on desktop and mobile.
- Demonstrate practical use of Git and GitHub: repositories, commits, branches, pull requests, Issues, Projects and documentation.

## Features

| Area | What it does |
|---|---|
| **Dashboard** | Total, pending, completed and overdue counts; progress bar; upcoming deadlines; overdue list |
| **Charts** | Doughnut chart of task status, bar chart of priorities, bar chart of tasks per subject |
| **Add Task** | Title, description, student, subject, due date, priority (Low/Medium/High), status (Pending/Completed) |
| **View Tasks** | Table showing due date, days left, priority and status badges |
| **Edit / Delete** | Update any field; delete asks for confirmation first |
| **Mark Complete / Pending** | One-click toggle; dashboard statistics update immediately |
| **Search and Filter** | Search by title; filter by status, priority, subject and student |
| **Deadline Indicators** | Red = overdue, amber = due within 2 days, struck-through = completed |
| **Student View** | The dashboard can be switched between the whole class and a single student |
| **Persistence** | SQLite database file created automatically on first run |
| **Responsive UI** | Sidebar layout on desktop, top navigation on mobile |

## Technology Stack

| Layer | Technology |
|---|---|
| Frontend | HTML5, CSS3, JavaScript, Jinja2 templates |
| Charts | Chart.js (loaded from a CDN) |
| Backend | Python 3, Flask |
| Database | SQLite (Python `sqlite3` module) |
| Version Control | Git |
| Hosting of source code | GitHub |
| Editor | Visual Studio Code |

## Project Structure

```
Student-Task-Manager/
├── app.py               # Flask app: routes, database access, validation, deadline logic
├── seed.py              # Loads the sample dataset and writes sample_tasks.csv
├── sample_tasks.csv     # Sample dataset (64 students, 10 subjects, 320 tasks)
├── requirements.txt     # Python dependencies
├── README.md            # Project documentation
├── .gitignore           # Files Git should ignore (venv, database, cache)
├── templates/
│   ├── base.html        # Layout: sidebar, flash messages, script block
│   ├── _macros.html     # Reusable task table used on several pages
│   ├── dashboard.html   # Statistics, charts, deadline lists
│   ├── tasks.html       # Task list with search and filters
│   └── task_form.html   # Shared form for adding and editing tasks
└── static/
    └── style.css        # Styling and responsive layout
```

`tasks.db` (the SQLite database) is created automatically when the app first runs and is not committed to Git.

## Database Design

The application uses one table, `tasks`.

| Column | Type | Description |
|---|---|---|
| `id` | INTEGER, primary key, auto-increment | Unique task ID |
| `title` | TEXT, not null | Task title (max 100 characters) |
| `description` | TEXT | Optional details |
| `subject` | TEXT | Subject or category |
| `due_date` | TEXT, not null | Due date in `YYYY-MM-DD` format |
| `priority` | TEXT, not null | `Low`, `Medium` or `High` |
| `status` | TEXT, not null | `Pending` or `Completed` |
| `student` | TEXT | Student name or roll number (optional label) |

If an older database without the `student` column exists, the app adds the column automatically on startup.

## How Deadlines Are Calculated

For every task, the app subtracts today's date from the due date to get `days_left`. A task then falls into one of four states:

| Condition | State | Indicator |
|---|---|---|
| Status is Completed | Done | Title struck through |
| Pending and `days_left < 0` | Overdue | Red row, "Overdue by N days" badge |
| Pending and `days_left` is 0, 1 or 2 | Urgent | Amber row, "Due today" or "Due in N days" badge |
| Pending and `days_left > 2` | Normal | "N days left" |

Overdue tasks are counted on the dashboard with the query: status is Pending and due date is earlier than today.

## Installation

**Requirements:** Python 3.9 or newer, pip, and Git.

1. **Clone the repository**
   ```bash
   git clone https://github.com/Ojash-creator/Student-Task-Manager.git
   cd Student-Task-Manager
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   ```

3. **Activate it**
   - Windows (Command Prompt or PowerShell): `venv\Scripts\activate`
   - macOS / Linux: `source venv/bin/activate`

   If PowerShell blocks the script, run `Set-ExecutionPolicy -Scope Process Bypass` first.

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

```bash
python app.py
```

Open **http://127.0.0.1:5000** in your browser. Stop the server with `Ctrl + C`.

The database file `tasks.db` is created automatically in the project folder the first time the app runs.

## Sample Dataset

To explore the dashboard and charts with realistic data, load the sample dataset:

```bash
python seed.py            # adds data only if the tasks table is empty
python seed.py --reset    # deletes all existing tasks, then loads the sample data
```

The dataset contains **64 students** (roll numbers `22CS001` to `22CS064`), each with 5 tasks across **10 subjects**, giving 320 tasks:

Data Structures, DBMS, Operating Systems, Computer Networks, Python Programming, Web Technology, Software Engineering, Discrete Mathematics, Computer Architecture and Technical Communication.

Task due dates are generated relative to today's date, so overdue, urgent and upcoming tasks always appear. The same data is saved as `sample_tasks.csv`. The data is generated with a fixed random seed, so it is the same each time.

## Using the Application

1. **Dashboard:** view the statistics cards, progress bar, charts, overdue tasks and the next five upcoming deadlines. Use the dropdown at the top to switch between the whole class and one student.
2. **Add a task:** click **+ Add Task**, fill in the form and save. Title and due date are required.
3. **View tasks:** open **All Tasks** to see every task, with due dates, priorities and statuses.
4. **Search and filter:** type part of a title, or choose a student, status, priority or subject, then click **Filter**. Click **Reset** to clear.
5. **Complete a task:** click **Complete** to mark it done, or **Mark Pending** to reopen it. The dashboard updates immediately.
6. **Edit a task:** click **Edit**, change any field and save.
7. **Delete a task:** click **Delete** and confirm in the popup.

## Application Routes

| Method | URL | Purpose |
|---|---|---|
| GET | `/` | Dashboard (optional `?student=` filter) |
| GET | `/tasks` | Task list with search and filters (`q`, `status`, `priority`, `subject`, `student`) |
| GET, POST | `/tasks/add` | Show the add form / save a new task |
| GET, POST | `/tasks/<id>/edit` | Show the edit form / save changes |
| POST | `/tasks/<id>/toggle` | Switch a task between Pending and Completed |
| POST | `/tasks/<id>/delete` | Delete a task |

## Input Validation and Security

- **Server-side validation:** the title must be present and at most 100 characters, the due date must be a valid `YYYY-MM-DD` date, and priority and status must be one of the allowed values. Errors are shown to the user and nothing is saved until they are fixed.
- **Safe database queries:** all SQL uses `?` placeholders (parameterized queries), which prevents SQL injection.
- **Safe actions:** deleting and toggling use POST requests, and deletion needs confirmation.
- **Escaped output:** Jinja2 escapes task text by default, which prevents HTML injection.
- **Secret key:** change `app.secret_key` in `app.py` to your own long random string before deploying.

## Testing Checklist

| # | Test | Expected result |
|---|---|---|
| 1 | Add a task with all valid fields | Task appears in the list; success message shown |
| 2 | Add a task with an empty title | Error message; task not saved |
| 3 | Add a task with an invalid or missing date | Error message; task not saved |
| 4 | Add a task due yesterday | Shown in red; counted as overdue |
| 5 | Add a task due today | Shown in amber as "Due today" |
| 6 | Mark a task Completed | Status changes; dashboard counts and progress bar update |
| 7 | Mark a completed task Pending | Task returns to the pending count |
| 8 | Edit a task | Changes are saved and visible in the list |
| 9 | Delete a task and click Cancel | Task is kept |
| 10 | Delete a task and confirm | Task is removed |
| 11 | Search by part of a title | Only matching tasks are shown |
| 12 | Filter by status, priority, subject, student | Only matching tasks are shown |
| 13 | Restart the app | All tasks are still present |
| 14 | Resize the browser to phone width | Layout adapts; navigation stays usable |
| 15 | Select a student on the dashboard | Cards, charts and lists show only that student |

## Deployment

The app needs a Python server, so it cannot run on GitHub Pages. Options:

- **GitHub Codespaces:** open the repository, choose **Code → Codespaces → Create codespace**, then run `pip install -r requirements.txt`, `python seed.py --reset` and `flask --app app run`. Good for demonstrations.
- **PythonAnywhere (free Beginner account):** clone the repository, create a virtualenv, add a web app with manual configuration and point the WSGI file at `app`. SQLite data persists.
- **Render (free tier):** add `gunicorn` to `requirements.txt`, set the start command to `python seed.py && gunicorn app:app`. Free instances sleep when idle, and SQLite data is reset when the service restarts, so the sample data is reloaded on each start.

Check each provider's current free-tier terms before deploying.

## Screenshots
| Screen | Preview |
|---|---|
| Dashboard with charts |<img width="1881" height="973" alt="Screenshot 2026-10-25 110759" src="https://github.com/user-attachments/assets/20eadf04-cc5e-4572-bf2d-ab0d567aa563" /> |

| Task list with filters | <img width="1508" height="952" alt="Screenshot 2026-10-25 110814" src="https://github.com/user-attachments/assets/48799d9b-7378-494e-b435-44622fe4bba1" /> |

| Add / edit task form |<img width="898" height="965" alt="Screenshot 2026-10-25 110846" src="https://github.com/user-attachments/assets/f8522653-5186-4b39-91e2-de0719165768" /> |

## Git and GitHub Workflow

This project is designed to be developed using the GitHub fundamentals:

- **Repository:** all source code is stored in one GitHub repository with a clear folder structure.
- **Commits:** make small commits with clear messages, for example `Add student filter to tasks page`.
- **Branches:** create a branch per feature, such as `feature/dashboard`, `feature/task-management` or `feature/charts-and-sample-data`, and keep `main` stable.
- **Pull requests:** open a pull request for each feature branch, review the changes, then merge into `main`.
- **Issues:** record work items and bugs as GitHub Issues and close them when finished.
- **Projects:** track progress on a board with **To do**, **In progress** and **Done** columns.

Common commands:

```bash
git status                         # see changed files
git add .                          # stage changes
git commit -m "Describe change"    # save a snapshot
git push                           # upload commits to GitHub
git log --oneline                  # view commit history
git checkout -b feature/my-change  # create and switch to a new branch
```

## Limitations

- Single-user application with no login or authentication; the "student" field is only a label on each task.
- The charts need an internet connection to load the Chart.js library from a CDN.
- The task list is not paginated, so very large datasets load on one page.
- No email or push notifications for upcoming deadlines.
- SQLite is suited to small deployments, not many simultaneous users.

## Future Enhancements

- User accounts and login so each student sees only their own tasks.
- Email or browser reminders before deadlines.
- Calendar view of tasks.
- Pagination and sorting options on the task list.
- Export tasks to CSV or PDF.
- Recurring tasks and subtasks.
- Automated tests with `pytest`.
