from flask import Flask, render_template, request, redirect, flash, url_for
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import UserMixin, LoginManager, login_user, login_required, logout_user
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.secret_key = 'some'
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'database.db')
db = SQLAlchemy(app)
log_manager = LoginManager(app)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(20), nullable=False)
    login = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return '<User %r>' % self.id


@app.route('/')
@app.route('/test', methods=['POST', 'GET'])
@login_required
def index():
    return render_template('names_f.html')


@app.route('/name_reg', methods=['POST', 'GET'])
def name_reg():
    login = request.form.get('login')
    password = request.form.get('password')
    password2 = request.form.get('password2')
    nickname = request.form.get('nickname')

    if request.method == 'POST':
        if not (login or password2 or password or nickname):
            flash('Заполните все поля')
        elif password != password2:
            flash('Пароли не одинаковые')
        else:
            pwd = generate_password_hash(password)
            new_user = User(login=login, password=pwd, nickname=nickname)
            db.session.add(new_user)
            db.session.commit()

            return redirect(url_for('name_log'))

    return render_template('name_reg.html')


@app.route('/name_log', methods=['POST', 'GET'])
def name_log():
    login = request.form.get('login')
    password = request.form.get('password')

    if login and password:
        user = User.query.filter_by(login=login).first()

        if user and check_password_hash(user.password, password):
            login_user(user)

            return render_template('names_f.html')
        else:
            flash('Неправильный логин или пароль')
    return render_template('login.html')


@log_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/names')
@login_required
def names():
    user = User.query.all()
    return render_template('names_f.html', user=user or [])


@app.route('/names/<user_id>/del')
@login_required
def names_del(user_id):
    user = User.query.get_or_404(user_id)

    try:
        db.session.delete(user)
        db.session.commit()
        return redirect('/names')
    except:
        return "Миша всё ху@ня давай по новой"


@app.route('/names/<user_id>/up', methods=['POST', 'GET'])
@login_required
def name_up(user_id):
    if request.method == "POST":
        login = request.form['login']
        user = User(login=login)

        try:
            db.session.add(user)
            db.session.commit()
            return redirect('/success')
        except:
            return 'Миша всё ху@ня давай по новой'
    else:
        user = User.query.get(user_id)
        return render_template("name_up.html", user=user)


@app.route('/names/<user_id>')
@login_required
def names_item(user_id):
    user = User.query.get(user_id)
    return render_template('names_item.html', user=user)


@app.route('/success')
@login_required
def success():
    return render_template("success.html")


@app.after_request
def redirect_to_sigin(response):
    if response.status_code == 401:
        return redirect(url_for('name_log') + '?next=' + request.url)

    return response


if __name__ == "__main__":
    app.run(debug=True)
