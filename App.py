from flask import Flask
from flask import render_template, url_for, request, redirect

from sqlalchemy import func
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    gender = db.Column(db.Text)
    age = db.Column(db.Integer)


class Answers(db.Model):
    __tablename__ = 'tea_answers'
    id = db.Column(db.Integer, primary_key=True)
    tea = db.Column(db.Text)
    sugartea = db.Column(db.Text)
    milktea = db.Column(db.Text)
    addings = db.Column(db.Text)


class Teatypes(db.Model):
    __tablename__ = 'teatypes'
    user_id = db.Column(db.Integer)
    teatype = db.Column(db.Text)
    counter = db.Column(db.Integer, primary_key=True)


@app.route('/')
def main():
    return render_template('main.html')


@app.route('/stats')
def stats():
    all_info = {}
    age_stats = db.session.query(
        func.avg(User.age),
        func.min(User.age),
        func.max(User.age)
    ).one()
    all_info['age_mean'] = round(age_stats[0])
    all_info['age_min'] = age_stats[1]
    all_info['age_max'] = age_stats[2]
    all_info['sugar_a'] = len(db.session.query(Answers.sugartea).filter(Answers.sugartea == 'always').all())
    all_info['sugar_s'] = len(db.session.query(Answers.sugartea).filter(Answers.sugartea == 'sometimes').all())
    all_info['sugar_n'] = len(db.session.query(Answers.sugartea).filter(Answers.sugartea == 'never').all())
    all_info['milk_a'] = len(db.session.query(Answers.milktea).filter(Answers.milktea == 'always').all())
    all_info['milk_s'] = len(db.session.query(Answers.milktea).filter(Answers.milktea == 'sometimes').all())
    all_info['milk_n'] = len(db.session.query(Answers.milktea).filter(Answers.milktea == 'never').all())
    return render_template("stats.html", all_info=all_info)


@app.route('/form')
def form():
    return render_template('form.html')


@app.route('/process', methods=['get'])
def answer_process():
    if not request.args:
        return redirect(url_for('form'))
    gender = request.args.get('gender')
    age = request.args.get('age')
    user = User(
        age=age,
        gender=gender
    )
    db.session.add(user)
    db.session.commit()
    db.session.refresh(user)
    tea = request.args.get('tea')
    sugartea = request.args.get('sugartea')
    milktea = request.args.get('milktea')
    addings = request.args.get('addings')
    answer = Answers(
        id=user.id,
        tea=tea,
        sugartea=sugartea,
        milktea=milktea,
        addings=addings)
    db.session.add(answer)
    teatype_list = request.args.getlist('teatype')
    for t in teatype_list:
        if t is not None and t != '':
            line = Teatypes(
                user_id=user.id,
                teatype=t)
            db.session.add(line)
    db.session.commit()
    return render_template('process.html')


if __name__ == "__main__":
    app.run()
