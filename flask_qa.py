from flask import Flask, render_template, request, redirect, url_for, session
import config
from models import User, Question
from exts import db
from decorators import login_required


app = Flask(__name__)
app.config.from_object(config)
db.init_app(app)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        telephone = request.form.get('telephone')
        password = request.form.get('password')
        user = User.query.filter(User.telephone == telephone, password == password).first()
        if user:
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
                user = User(telephone = telephone, username = username, password = password1)
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
        user_id = session.get('user_id')
        user = User.query.filter(User.id == user_id).first()
        question.author = user
        db.session.add(question)
        db.session.commit()
        return redirect(url_for('index'))


@app.context_processor
def my_context_processor():
    user_id = session.get('user_id')
    if user_id:
        user = User.query.filter(User.id == user_id).first()
        if user:
            return {'user': user}
    return {}



if __name__ == '__main__':
    app.run()
