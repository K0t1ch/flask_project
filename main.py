from data import db_session
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask import Flask, render_template, redirect, request, abort, url_for
import os

from forms.news import NewsForm
from forms.user import RegisterForm, LoginForm
from data.users import User
from data.news import News

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

login_manager = LoginManager()
login_manager.init_app(app)


def main():
    db_session.global_init("db/blogs.db")
    app.run()


@app.route("/photos.html")
def photo():

    folder_path = r'C:\Users\dselc\PycharmProjects\flask_project2\static\img\image'
    file_names = []
    for file_name in os.listdir(folder_path):
        if os.path.isfile(os.path.join(folder_path, file_name)):
            file_names.append(file_name)

    print(file_names)

    return render_template('photos.html', file_names=file_names)






@app.route("/ict.html")
def ict():
    db_sess = db_session.create_session()
    news = db_sess.query(News).filter(News.title == 'Информатика').filter(News.is_question != True)
    return render_template("ict.html", news=news, title='ICT Documentation')


@app.route("/allnews.html")
def all():
    db_sess = db_session.create_session()
    news = db_sess.query(News).filter(News.is_question != True)
    return render_template("allnews.html", news=news, title='ALL Documentation')


@app.route("/questions.html")
def questions():
    db_sess = db_session.create_session()
    news = db_sess.query(News).filter(News.is_question == True)
    return render_template("questions.html", news=news, title='QUESTIONS')


@app.route("/math.html")
def math():
    db_sess = db_session.create_session()
    news = db_sess.query(News).filter(News.title == 'Математика').filter(News.is_question != True)
    return render_template("math.html", news=news, title='MATHS Documentation')


@app.route("/phys.html")
def phys():
    db_sess = db_session.create_session()
    news = db_sess.query(News).filter(News.title == 'Физика').filter(News.is_question != True)
    return render_template("phys.html", news=news, title='PHYSICS Documentation')


@app.route("/rus.html")
def rus():
    db_sess = db_session.create_session()
    news = db_sess.query(News).filter(News.title == 'Русский язык').filter(News.is_question != True)
    return render_template("rus.html", news=news, title='RUSSIAN LANGUAGE Documentation')


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/')
@app.route('/index.html')
def index():
    return render_template('index.html')


@app.route('/testiki.html')
def tests():
    return render_template('testiki.html')


@app.route('/Support.html')
def sup():
    return render_template('Support.html')


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            email=form.email.data,
            about=form.about.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/news',  methods=['GET', 'POST'])
@login_required
def add_news():
    dictionary = {'Информатика': 'ict.html',
                  'Математика': 'math.html',
                  'Русский язык': 'rus.html',
                  'Физика': 'phys.html'}
    form = NewsForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        news = News()
        news.title = form.title.data
        news.content = form.content.data
        news.is_question = form.is_question.data
        current_user.news.append(news)
        db_sess.merge(current_user)
        db_sess.commit()

        if news.title in dictionary.keys():
            return redirect(f'/{dictionary[news.title]}')
        else:
            return redirect(f'/allnews.html')

    return render_template('news.html', title='Добавление новости',
                           form=form)


@app.route('/news/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_news(id):
    dictionary = {'Информатика': 'ict.html',
                  'Математика': 'math.html',
                  'Русский язык': 'rus.html',
                  'Физика': 'phys.html'}

    form = NewsForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        news = db_sess.query(News).filter(News.id == id,
                                          News.user == current_user
                                          ).first()
        if news:
            form.title.data = news.title
            form.content.data = news.content
            form.is_question.data = news.is_question
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        news = db_sess.query(News).filter(News.id == id,
                                          News.user == current_user
                                          ).first()
        if news:
            news.title = form.title.data
            news.content = form.content.data
            news.is_question = form.is_question.data
            db_sess.commit()

            if news.title in dictionary.keys():
                return redirect(f'/{dictionary[news.title]}')
            else:
                return redirect(f'/allnews.html')

        else:
            abort(404)
    return render_template('news.html',
                           title='Редактирование новости',
                           form=form)


@app.route('/news_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def news_delete(id):
    dictionary = {'Информатика': 'ict.html',
                  'Математика': 'math.html',
                  'Русский язык': 'rus.html',
                  'Физика': 'phys.html'}

    db_sess = db_session.create_session()
    news = db_sess.query(News).filter(News.id == id,
                                      News.user == current_user
                                      ).first()
    if news:
        db_sess.delete(news)
        db_sess.commit()
    else:
        abort(404)
    try:
        if news.title in dictionary.keys():
            return redirect(f'/{dictionary[news.title]}')
        else:
            return redirect(f'/allnews.html')
    except Exception:
        return redirect(f'/questions.html')


@app.route('/upload', methods=['POST', 'GET'])
def sample_file_upload():
    if request.method == 'POST':
        f = request.files['file']

        f.save(fr"static\img\image\{f.filename}")

        return redirect('photos.html')

    else:
        return f'''<!doctype html>
        <html lang="en">

        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
            <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.0-beta1/dist/css/bootstrap.min.css"
                integrity="sha384-giJF6kkoqNQ00vy+HMDP7azOuL0xtbfIcaT9wjKHr8RbDVddVHyTfAAsrekwKmP1" crossorigin="anonymous">
            <link rel="stylesheet" type="text/css" href="{url_for('static', filename='css/style.css')}" />
            <title>Пример загрузки файла</title>
        </head>

        <body>
            <h1 style="text-align: center;">Загрузка фотографии</h1>
            <h2 style="text-align: center;">для участия в миссии</h2>
            <form method="post" enctype="multipart/form-data">
                <div class="form-group"
                    style="background-color: yellow; border: 3px solid yellowgreen;width: fit-content; height: fit-content; margin-left: auto; margin-right: auto;">
                    Приложите фотографию<br>

                    <input type="file" class="form-control-file" id="photo" name="file"><br>
                    <button type="submit" class="btn btn-primary">Отправить</button>
                </div>

            </form>
        </body>

        </html>'''






if __name__ == '__main__':
    main()

