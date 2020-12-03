import os
from flask import Flask,request, render_template, redirect
from flask_login import login_required, current_user, login_user, logout_user
from book_handler import fetch_books
from models import db, login, UserModel, BookModel

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///optolibro_data'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'xyz'

login.init_app(app)
login.login_view = 'login'

db.init_app(app)
@app.before_first_request
def create_table():
    db.create_all()

@app.route("/")
def list():
    books = BookModel.query.all()
    return render_template("list.html", books=books)

@app.route("/fetch")
def fetch():

    books = fetch_books()

    for i,b in enumerate(books):

        existing_book = BookModel.query.filter_by(name=b[0]).first()

        if(existing_book):
            existing_book.cardinal = i+1
            existing_book.author = b[1]
            existing_book.url = b[2]
            existing_book.img_url = b[3]
            existing_book.description = b[4][:500]
        else:
            book = BookModel(cardinal=i+1,name=b[0],author=b[1],url=b[2],img_url=b[3],description=b[4][:500])
            db.session.add(book)

        db.session.commit()

    return redirect("/")

@app.route("/fulfill", methods=['POST'])
@login_required
def fulfill():
    if request.method == 'POST':
        book_id = request.args.get("book_id")
        reset = request.args.get("reset")
        book = BookModel.query.filter_by(id = book_id).first()
        book.fulfilled = not reset
        db.session.commit()
    return redirect("/")

@app.route("/login", methods = ['POST','GET'])
def login():
    if current_user.is_authenticated:
        return redirect("/")
    if request.method == 'POST':
        username = request.form['username']
        user = UserModel.query.filter_by(username = username).first()
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

        if UserModel.query.filter_by(username=username).first():
            return ('Brukernavnet er allerede i bruk')

        if password != confirm_password:
            return ('Passordene stemmer ikke overensen')

        user = UserModel(username=username)
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
