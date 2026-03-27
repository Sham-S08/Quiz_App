import os, time, json
from functools import wraps
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_socketio import SocketIO, emit
from dotenv import load_dotenv

from models import db, Question
from database import (
    get_questions,
    save_result,
    get_leaderboard,
    save_question,
    export_results_df
)
from ai_generator import generate_questions

load_dotenv()

# ─── Flask Setup ─────────────────────────────────────────────

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev-secret")

app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///quiz.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)
socketio = SocketIO(app, async_mode="eventlet", cors_allowed_origins="*")

with app.app_context():
    db.create_all()

# ─── Admin Auth Decorator ────────────────────────────────────

def admin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not session.get("admin"):
            return redirect(url_for("admin_login"))
        return f(*args, **kwargs)
    return wrapper

# ─── Admin Login Routes ──────────────────────────────────────

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        key = request.form.get("admin_key")
        if key == os.getenv("ADMIN_KEY"):
            session["admin"] = True
            return redirect(url_for("admin"))
        return render_template("admin_login.html", error="Invalid key")
    return render_template("admin_login.html")


@app.route("/admin/logout")
def admin_logout():
    session.pop("admin", None)
    return redirect(url_for("index"))

# ─── Student Routes ──────────────────────────────────────────

@app.route("/")
def index():
    return render_template("quiz.html")


@app.route("/start", methods=["POST"])
def start_quiz():
    username   = request.form.get("username", "Anonymous")
    topic      = request.form.get("topic")
    difficulty = request.form.get("difficulty")
    timer      = int(request.form.get("timer", 0))

    questions = get_questions(topic, difficulty, limit=10)

    if not questions:
        return render_template(
            "quiz.html",
            error="No questions found. Ask admin to generate or add."
        )

    session["quiz"] = {
        "username": username,
        "topic": topic,
        "difficulty": difficulty,
        "start_time": time.time(),
        "q_ids": [q.id for q in questions],
        "timer": timer
    }

    q_list = [{
        "id": q.id,
        "question": q.question,
        "options": [q.option1, q.option2, q.option3, q.option4]
    } for q in questions]

    return render_template(
        "quiz.html",
        questions=q_list,
        username=username,
        topic=topic,
        difficulty=difficulty,
        timer=timer
    )


@app.route("/submit", methods=["POST"])
def submit_quiz():
    quiz = session.get("quiz")
    if not quiz:
        return redirect(url_for("index"))

    answers = request.form.to_dict()
    time_taken = round(time.time() - quiz["start_time"], 2)

    # Timer enforcement
    if quiz["timer"] and time_taken > quiz["timer"]:
        time_taken = quiz["timer"]

    questions = Question.query.filter(
        Question.id.in_(quiz["q_ids"])
    ).all()

    # Safe scoring logic
    score = 0
    for q in questions:
        user_ans = answers.get(str(q.id))
        if user_ans == q.answer:
            score += 1

    result = save_result(
        username=quiz["username"],
        score=score,
        total=len(questions),
        time_taken=time_taken,
        topic=quiz["topic"],
        difficulty=quiz["difficulty"],
        answers_log=answers
    )

    # Real-time leaderboard update
    socketio.emit("score_update", {
        "username": quiz["username"],
        "score": score,
        "total": len(questions),
        "topic": quiz["topic"]
    })

    # Badge logic
    pct = round(score / len(questions) * 100)

    if pct >= 80:
        badge = "Proficient"
        badge_color = "#1D9E75"
    elif pct >= 60:
        badge = "Intermediate"
        badge_color = "#BA7517"
    else:
        badge = "Beginner"
        badge_color = "#D85A30"

    # Clear session after submit
    session.pop("quiz", None)

    return render_template(
        "result.html",
        score=score,
        total=len(questions),
        time_taken=time_taken,
        username=quiz["username"],
        topic=quiz["topic"],
        difficulty=quiz["difficulty"],
        pct=pct,
        badge=badge,
        badge_color=badge_color
    )

# ─── Leaderboard ─────────────────────────────────────────────

@app.route("/leaderboard")
def leaderboard():
    topic = request.args.get("topic")
    board = get_leaderboard(topic=topic)
    return render_template("leaderboard.html", board=board, topic=topic)

# ─── Admin Routes ────────────────────────────────────────────

@app.route("/admin")
@admin_required
def admin():
    return render_template("admin.html")


@app.route("/admin/add", methods=["POST"])
@admin_required
def admin_add():
    data = {k: request.form[k] for k in [
        "question",
        "option1",
        "option2",
        "option3",
        "option4",
        "answer",
        "difficulty",
        "topic"
    ]}
    save_question(data, source="manual")
    return redirect(url_for("admin"))


@app.route("/admin/generate", methods=["POST"])
@admin_required
def admin_generate():
    topic      = request.form.get("topic")
    difficulty = request.form.get("difficulty")
    num        = int(request.form.get("num", 5))
    context    = request.form.get("context", "").strip() or None

    questions, ctx_used = generate_questions(
        topic,
        difficulty,
        num,
        context
    )

    return render_template(
        "admin.html",
        generated=questions,
        topic=topic,
        difficulty=difficulty,
        context=ctx_used
    )


@app.route("/admin/approve", methods=["POST"])
@admin_required
def admin_approve():
    questions  = json.loads(request.form.get("questions_json"))
    topic      = request.form.get("topic")
    difficulty = request.form.get("difficulty")

    for q in questions:
        q.update({
            "topic": topic,
            "difficulty": difficulty
        })
        save_question(q, source="ai")

    return redirect(url_for("admin"))

# ─── Analytics Export ────────────────────────────────────────

@app.route("/analytics/export")
def analytics_export():
    df = export_results_df()
    path = "static/results_export.csv"
    df.to_csv(path, index=False)

    return jsonify({
        "message": "Exported successfully",
        "path": path,
        "rows": len(df)
    })

# ─── SocketIO ────────────────────────────────────────────────

@socketio.on("connect")
def on_connect():
    board = get_leaderboard(limit=10)
    emit("init_board", [{
        "username": r.username,
        "score": r.score,
        "total": r.total,
        "topic": r.topic
    } for r in board])

# ─── Run App ─────────────────────────────────────────────────

if __name__ == "__main__":
    socketio.run(app, debug=True)
