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


class Article(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return '<Article %r>' % self.id


@app.route('/')
@app.route('/test', methods=['POST', 'GET'])
def index():
    if request.method == "POST":
        login = request.form.get('login')
        password = request.form.get('password')
        article = Article(login=login, password=password)

        try:
            db.session.add(article)
            db.session.commit()
            return redirect('/success')
        except:
            return 'Миша всё ху@ня давай по новой'
    else:
        return redirect('/name_log')


@app.route('/name_reg', methods=['POST', 'GET'])
def name_reg():
    login = request.form.get('login')
    password = request.form.get('password')
    password2 = request.form.get('password2')

    if request.method == 'POST':
        if not(login or password2 or password):
            flash('Заполните все поля')
        elif password != password2:
            flash('Пароли не одинаковые')
        else:
            pwd = generate_password_hash(password)
            new_user = Article(login=login, password=pwd)
            db.session.add(new_user)
            db.session.commit()

            return render_template('login.html')

    return render_template('name_reg.html')


@app.route('/name_log', methods=['POST', 'GET'])
def name_log():
    login = request.form.get('login')
    password = request.form.get('password')

    if login and password:
        log = Article.query.filter_by(login=login).first()

        if log and check_password_hash(Article.password, password):
            login_user(log)

            next = request.args.get('next')

            redirect(next)
        else:
            flash('Заполните все поля')
    else:
        flash('Error')
        return render_template('login.html')


@log_manager.user_loader
def load_user(article_id):
    return Article.query.get(article_id)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/names')
@login_required
def names():
    articles = Article.query.all()
    return render_template('names_f.html', articles=articles or [])


@app.route('/names/<article_id>/del')
@login_required
def names_del(article_id):
    article = Article.query.get_or_404(article_id)

    try:
        db.session.delete(article)
        db.session.commit()
        return redirect('/names')
    except:
        return "Миша всё ху@ня давай по новой"


@app.route('/names/<article_id>/up', methods=['POST', 'GET'])
@login_required
def name_up(article_id):
    if request.method == "POST":
        login = request.form['login']
        article = Article(login=login)

        try:
            db.session.add(article)
            db.session.commit()
            return redirect('/success')
        except:
            return 'Миша всё ху@ня давай по новой'
    else:
        article = Article.query.get(article_id)
        return render_template("name_up.html", article=article)


@app.route('/names/<article_id>')
@login_required
def names_item(article_id):
    article = Article.query.get(article_id)
    return render_template('names_item.html', article=article)


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