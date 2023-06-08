from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'database.db')
db = SQLAlchemy(app)


class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(5, 20), nullable=False)

    def __repr__(self):
        return '<Article %r>' % self.id


@app.route('/')
@app.route('/test', methods=['POST', 'GET'])
def index():
    if request.method == "POST":
        def write_file(date):
            with open('list.txt', 'a') as f:
                f.write(str(date))
        text = request.form['text']
        write_file(text + '\n')
        article = Article(text=text)

        try:
            db.session.add(article)
            db.session.commit()
            return redirect('/success')
        except:
            return 'Миша всё ху@ня давай по новой'
    else:
        return render_template("index.html")


@app.route('/names')
def names():
    articles = Article.query.all()
    return render_template('names_f.html', articles=articles or [])


@app.route('/names/<article_id>/del')
def names_del(article_id):
    article = Article.query.get_or_404(article_id)

    try:
        db.session.delete(article)
        db.session.commit()
        return redirect('/names')
    except:
        return "Миша всё ху@ня давай по новой"


@app.route('/names/<article_id>')
def names_item(article_id):
    article = Article.query.get(article_id)
    return render_template('names_item.html', article=article)


@app.route('/success')
def succes():
    return render_template("success.html")


if __name__ == "__main__":
    app.run(debug=True)