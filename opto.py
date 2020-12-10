import os
from flask import Flask,request, render_template, redirect
from flask_login import login_required, current_user, login_user, logout_user
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from book_handler import fetch_books
from models import db, login, User, List, Book
from views import AdminModelView

app = Flask(__name__)


app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'

admin = Admin(app, name='optolibro',template_mode='bootstrap3')
admin.add_view(AdminModelView(User, db.session))
admin.add_view(AdminModelView(List, db.session))
admin.add_view(AdminModelView(Book, db.session))

login.init_app(app)
login.login_view = 'login'

db.init_app(app)
@app.before_first_request
def create_table():
    db.create_all()

@app.route("/")
def lists():
    lists = List.query.order_by(List.id.desc()).all()
    return render_template("lists.html", lists=lists)

@app.route("/list")
def list():
    list_id = request.args.get("id")
    list = List.query.filter_by(id=list_id).first()
    return render_template("list.html", list=list)

@app.route("/fetch")
def fetch():

    if not (current_user.is_authenticated and current_user.super):
        return redirect("/")

    books = fetch_books()

    list = List.query.first()

    for i,b in enumerate(books):

        existing_book = Book.query.filter_by(name=b[0]).first()

        if(existing_book):
            existing_book.ordinal = i+1
            existing_book.author = b[1]
            existing_book.url = b[2]
            existing_book.img_url = b[3]
            existing_book.description = b[4][:500]
        else:
            book = Book(ordinal=i+1,name=b[0],author=b[1],url=b[2],img_url=b[3],description=b[4][:500])
            list.books.append(book)

    db.session.add(list)
    db.session.commit()

    return redirect("/")

@app.route("/fulfill", methods=['POST'])
@login_required
def fulfill():
    if request.method == 'POST':
        book_id = request.args.get("book_id")
        reset = request.args.get("reset")
        book = Book.query.filter_by(id = book_id).first()
        book.fulfilled = not reset
        db.session.commit()
    return redirect("/")

@app.route("/login", methods = ['POST','GET'])
def login():
    if current_user.is_authenticated:
        return redirect("/")
    if request.method == 'POST':
        username = request.form['username']
        user = User.query.filter_by(username = username).first()
        if user is not None and user.check_password(request.form['password']):
            login_user(user)
            return redirect('/')

    return render_template('login.html')

@app.route("/register",methods=['POST','GET'])
def register():
    if current_user.is_authenticated:
        return redirect('/')

    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password'].strip()
        confirm_password = request.form['confirm_password'].strip()

        if User.query.filter_by(username=username).first():
            return ('Brukernavnet er allerede i bruk')

        if password != confirm_password:
            return ('Passordene stemmer ikke overensen')

        user = User(username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return redirect('/login')

    return render_template('register.html')

@app.route("/logout")
def logout():
    logout_user()
    return redirect("/")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host='0.0.0.0', port=port)
