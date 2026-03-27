from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Question(db.Model):
    __tablename__ = 'questions'
    id         = db.Column(db.Integer, primary_key=True)
    question   = db.Column(db.Text, nullable=False)
    option1    = db.Column(db.String(300), nullable=False)
    option2    = db.Column(db.String(300), nullable=False)
    option3    = db.Column(db.String(300), nullable=False)
    option4    = db.Column(db.String(300), nullable=False)
    answer     = db.Column(db.String(300), nullable=False)
    difficulty = db.Column(db.String(20), nullable=False)   # easy/medium/hard
    topic      = db.Column(db.String(100), nullable=False)
    source     = db.Column(db.String(20), default='manual') # manual/ai

class Result(db.Model):
    __tablename__ = 'results'
    id          = db.Column(db.Integer, primary_key=True)
    username    = db.Column(db.String(100), nullable=False)
    score       = db.Column(db.Integer, nullable=False)
    total       = db.Column(db.Integer, nullable=False)
    time_taken  = db.Column(db.Float, nullable=False)       # seconds
    topic       = db.Column(db.String(100), nullable=False)
    difficulty  = db.Column(db.String(20), nullable=False)
    timestamp   = db.Column(db.DateTime, default=datetime.utcnow)
    answers_log = db.Column(db.JSON)                        # {q_id: chosen_answer}