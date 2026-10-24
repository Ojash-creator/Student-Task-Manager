import sqlite3
from datetime import date, datetime
from flask import Flask, render_template, request, redirect, url_for, flash, g, abort

app = Flask(__name__)
app.secret_key = "change-this-secret-key"
DB = "tasks.db"
PRIORITIES = ["Low", "Medium", "High"]
STATUSES = ["Pending", "Completed"]


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(error=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    with sqlite3.connect(DB) as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            subject TEXT,
            due_date TEXT NOT NULL,
            priority TEXT NOT NULL DEFAULT 'Medium',
            status TEXT NOT NULL DEFAULT 'Pending',
            student TEXT DEFAULT '')""")
        cols = [r[1] for r in conn.execute("PRAGMA table_info(tasks)")]
        if "student" not in cols:  # upgrade an older database
            conn.execute("ALTER TABLE tasks ADD COLUMN student TEXT DEFAULT ''")


def decorate(rows):
    """Add days_left and a 'state' (overdue / urgent / normal / done) to each task."""
    today = date.today()
    out = []
    for r in rows:
        t = dict(r)
        t["days_left"] = (date.fromisoformat(t["due_date"]) - today).days
        if t["status"] == "Completed":
            t["state"] = "done"
        elif t["days_left"] < 0:
            t["state"] = "overdue"
        elif t["days_left"] <= 2:
            t["state"] = "urgent"
        else:
            t["state"] = "normal"
        out.append(t)
    return out


def validate(form):
    data = {k: form.get(k, "").strip() for k in
            ["title", "description", "subject", "due_date", "priority", "status", "student"]}
    errors = []
    if not data["title"]:
        errors.append("Title is required.")
    elif len(data["title"]) > 100:
        errors.append("Title must be 100 characters or fewer.")
    try:
        datetime.strptime(data["due_date"], "%Y-%m-%d")
    except ValueError:
        errors.append("Please enter a valid due date.")
    if data["priority"] not in PRIORITIES:
        errors.append("Invalid priority.")
    if data["status"] not in STATUSES:
        errors.append("Invalid status.")
    return data, errors


@app.route("/")
def dashboard():
    db = get_db()
    today = date.today().isoformat()
    student = request.args.get("student", "")
    where, p = ("WHERE student = ?", [student]) if student else ("WHERE 1=1", [])

    def count(extra="", args=()):
        return db.execute(f"SELECT COUNT(*) FROM tasks {where} {extra}", p + list(args)).fetchone()[0]

    total = count()
    completed = count("AND status='Completed'")
    overdue = count("AND status='Pending' AND due_date < ?", [today])
    pending = total - completed
    percent = round(completed * 100 / total) if total else 0
    upcoming = db.execute(f"SELECT * FROM tasks {where} AND status='Pending' AND due_date >= ? "
                          "ORDER BY due_date LIMIT 5", p + [today]).fetchall()
    late = db.execute(f"SELECT * FROM tasks {where} AND status='Pending' AND due_date < ? "
                      "ORDER BY due_date LIMIT 10", p + [today]).fetchall()
    subj = db.execute(f"SELECT COALESCE(NULLIF(subject,''), 'Other') AS s, COUNT(*) FROM tasks {where} GROUP BY s ORDER BY s", p).fetchall()
    prio = [count("AND priority=?", [x]) for x in PRIORITIES]
    charts = dict(status=[completed, pending - overdue, overdue], priority=prio,
                  subjects=[r[0] for r in subj], subject_counts=[r[1] for r in subj])
    students = [r[0] for r in db.execute("SELECT DISTINCT student FROM tasks WHERE student != '' ORDER BY student")]
    stats = dict(total=total, pending=pending, completed=completed, overdue=overdue, percent=percent)
    return render_template("dashboard.html", stats=stats, charts=charts, upcoming=decorate(upcoming),
                           late=decorate(late), students=students, student=student)


@app.route("/tasks")
def tasks():
    q = request.args.get("q", "").strip()
    status = request.args.get("status", "")
    priority = request.args.get("priority", "")
    subject = request.args.get("subject", "")
    student = request.args.get("student", "")
    sql, params = "SELECT * FROM tasks WHERE 1=1", []
    if q:
        sql += " AND title LIKE ?"; params.append(f"%{q}%")
    if status in STATUSES:
        sql += " AND status = ?"; params.append(status)
    if priority in PRIORITIES:
        sql += " AND priority = ?"; params.append(priority)
    if subject:
        sql += " AND subject = ?"; params.append(subject)
    if student:
        sql += " AND student = ?"; params.append(student)
    sql += " ORDER BY due_date"
    db = get_db()
    rows = db.execute(sql, params).fetchall()
    subjects = [r[0] for r in db.execute(
        "SELECT DISTINCT subject FROM tasks WHERE subject != '' ORDER BY subject")]
    students = [r[0] for r in db.execute("SELECT DISTINCT student FROM tasks WHERE student != '' ORDER BY student")]
    return render_template("tasks.html", tasks=decorate(rows), subjects=subjects, students=students,
                           f=dict(q=q, status=status, priority=priority, subject=subject, student=student),
                           priorities=PRIORITIES, statuses=STATUSES)


@app.route("/tasks/add", methods=["GET", "POST"])
def add_task():
    data = dict(title="", description="", subject="", due_date=date.today().isoformat(),
                priority="Medium", status="Pending", student="")
    if request.method == "POST":
        data, errors = validate(request.form)
        if not errors:
            db = get_db()
            db.execute("INSERT INTO tasks (title, description, subject, due_date, priority, status, student) "
                       "VALUES (?, ?, ?, ?, ?, ?, ?)",
                       (data["title"], data["description"], data["subject"],
                        data["due_date"], data["priority"], data["status"], data["student"]))
            db.commit()
            flash("Task added successfully.", "success")
            return redirect(url_for("tasks"))
        for e in errors:
            flash(e, "error")
    return render_template("task_form.html", task=data, heading="Add Task",
                           priorities=PRIORITIES, statuses=STATUSES)


@app.route("/tasks/<int:task_id>/edit", methods=["GET", "POST"])
def edit_task(task_id):
    db = get_db()
    row = db.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    if row is None:
        abort(404)
    data = dict(row)
    if request.method == "POST":
        data, errors = validate(request.form)
        if not errors:
            db.execute("UPDATE tasks SET title=?, description=?, subject=?, due_date=?, "
                       "priority=?, status=?, student=? WHERE id=?",
                       (data["title"], data["description"], data["subject"],
                        data["due_date"], data["priority"], data["status"], data["student"], task_id))
            db.commit()
            flash("Task updated.", "success")
            return redirect(url_for("tasks"))
        for e in errors:
            flash(e, "error")
    return render_template("task_form.html", task=data, heading="Edit Task",
                           priorities=PRIORITIES, statuses=STATUSES)


@app.route("/tasks/<int:task_id>/toggle", methods=["POST"])
def toggle_task(task_id):
    db = get_db()
    db.execute("UPDATE tasks SET status = CASE status WHEN 'Pending' THEN 'Completed' "
               "ELSE 'Pending' END WHERE id = ?", (task_id,))
    db.commit()
    return redirect(request.referrer or url_for("tasks"))


@app.route("/tasks/<int:task_id>/delete", methods=["POST"])
def delete_task(task_id):
    db = get_db()
    db.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    db.commit()
    flash("Task deleted.", "success")
    return redirect(request.referrer or url_for("tasks"))


@app.errorhandler(404)
def not_found(error):
    return render_template("base.html", content_404=True), 404


init_db()

if __name__ == "__main__":
    app.run(debug=True)
