from flask import Flask, render_template, request, redirect, url_for, session, g
import config
from models import User, Question, Answer
from exts import db
from decorators import login_required
from sqlalchemy import or_

app = Flask(__name__)
app.config.from_object(config)
db.init_app(app)


@app.route('/')
def index():
    context = {
        'questions': Question.query.order_by('create_time desc').all()
    }
    return render_template('index.html', **context)


@app.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        telephone = request.form.get('telephone')
        password = request.form.get('password')
        user = User.query.filter(User.telephone == telephone, password == password).first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            # session 保存时间
            session.permanent = True
            return redirect(url_for('index'))
        else:
            return "手机或密码错误"
            # return redirect(url_for('register'))


@app.route('/register/', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    else:
        telephone = request.form.get('telephone')
        username = request.form.get('username')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        # 手机号验证
        user = User.query.filter(User.telephone == telephone).first()
        if user:
            return "该手机号码已注册"
        else:
            # 密码验证
            if password1 != password2:
                return "两次密码不相等"
            else:
                user = User(telephone=telephone, username=username, password=password1)
                db.session.add(user)
                db.session.commit()
                # 如果注册成功，跳转登录页面
                return redirect(url_for('login'))


@app.route('/logout/')
def logout():
    session.pop('user_id')
    return redirect(url_for('login'))


@app.route('/question/', methods=['GET', 'POST'])
@login_required
def question():
    if request.method == 'GET':
        return render_template('question.html')
    else:
        title = request.form.get('title')
        content = request.form.get('content')
        question = Question(title=title, content=content)
        question.author = g.user
        db.session.add(question)
        db.session.commit()
        return redirect(url_for('index'))


@app.route('/search/')
def search():
    q = request.args.get('q')
    questions = Question.query.filter(or_(Question.title.contains(q), Question.content.contains(q))).order_by('-create-time')
    return render_template('index.html', questions = questions)


@app.route('/detail/<question_id>')
def detail(question_id):
    question_model = Question.query.filter(Question.id == question_id).first()
    return render_template('detail.html', question = question_model)


@app.route('/add_answer/', methods=['POST'])
@login_required
def add_answer():
    content = request.form.get('answer-content')
    question_id = request.form.get('question-id')
    answer = Answer(content=content)
    answer.author = g.user
    question = Question.query.filter(Question.id == question_id).first()
    answer.question = question
    db.session.add(answer)
    db.session.commit()
    return redirect(url_for('detail', question_id=question_id))


@app.before_request
def my_before_request():
    user_id = session.get('user_id')
    if user_id:
        user = User.query.filter(User.id == user_id).first()
        if user:
            g.user = user


@app.context_processor
def my_context_processor():
    if hasattr(g, 'user'):
        return {'user': g.user}
    return {}


if __name__ == '__main__':
    app.run()
