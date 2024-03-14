from flask_sqlalchemy import SQLAlchemy
from flask import render_template, request, session, Flask
from collections import defaultdict


app = Flask("Quiz App",  template_folder='templates')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'kodland'
db = SQLAlchemy(app)


class Answer(db.Model):
    __tablename__ = 'answer'
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(200), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)


class Question(db.Model):
    __tablename__ = 'question'
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(200), nullable=False)
    answer_id = db.Column(db.Integer, db.ForeignKey('answer.id'), nullable=False)

    def is_answer_correct(self, answer_id):
        return self.answer_id == answer_id


with app.app_context():
    db.create_all()


@app.route("/", methods=["GET"])
def index():
    session['max_score'] = session.get('max_score', 0)
    questions_choices = db.session.query(
        Question, Answer
    ).outerjoin(Answer, Answer.question_id == Question.id).all()
    questions = defaultdict(list)
    for question, choice in questions_choices:
        questions[question] += [choice]

    return render_template("index.html", questions=questions, session=session)


@app.route("/result", methods=["POST"])
def result():
    score = sum(
        1 for question_id, answer_id in request.form.items()
        if Question.query.get(int(question_id)).is_answer_correct(int(answer_id))
    )

    session['max_score'] = score if score > session['max_score'] else session['max_score']

    total = len(request.form)

    return render_template("results.html", score=score, total=total, session=session)
