from models import db, Question, Result

def get_questions(topic, difficulty, limit=10):
    return Question.query.filter_by(
        topic=topic, difficulty=difficulty
    ).order_by(db.func.random()).limit(limit).all()

def save_result(username, score, total, time_taken, topic, difficulty, answers_log):
    result = Result(
        username=username, score=score, total=total,
        time_taken=time_taken, topic=topic,
        difficulty=difficulty, answers_log=answers_log
    )
    db.session.add(result)
    db.session.commit()
    return result

def get_leaderboard(topic=None, limit=20):
    query = Result.query
    if topic:
        query = query.filter_by(topic=topic)
    return query.order_by(
        Result.score.desc(), Result.time_taken.asc()
    ).limit(limit).all()

def save_question(data, source='manual'):
    q = Question(source=source, **data)
    db.session.add(q)
    db.session.commit()
    return q

def export_results_df():
    import pandas as pd
    results = Result.query.all()
    return pd.DataFrame([{
        'username': r.username, 'score': r.score, 'total': r.total,
        'pct': round(r.score / r.total * 100, 1),
        'time_taken': r.time_taken, 'topic': r.topic,
        'difficulty': r.difficulty, 'timestamp': r.timestamp
    } for r in results])