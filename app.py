from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///library.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# Model
class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    is_borrowed = db.Column(db.Boolean, default=False)

class Borrow(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey("book.id"), nullable=False)
    borrower_name = db.Column(db.String(100), nullable=False)
    borrow_date = db.Column(db.DateTime, default=datetime.utcnow)
    return_date = db.Column(db.DateTime, nullable=True)

    book = db.relationship("Book", backref="borrows")

# Routes
@app.route("/")
def index():
    books = Book.query.all()
    return render_template("index.html", books=books)

@app.route("/add", methods=["POST"])
def add_book():
    title = request.form["title"]
    author = request.form["author"]
    new_book = Book(title=title, author=author)
    db.session.add(new_book)
    db.session.commit()
    return redirect(url_for("index"))

@app.route("/borrow/<int:book_id>", methods=["POST"])
def borrow_book(book_id):
    borrower = request.form["borrower"]
    book = Book.query.get_or_404(book_id)
    if not book.is_borrowed:
        book.is_borrowed = True
        new_borrow = Borrow(book_id=book.id, borrower_name=borrower)
        db.session.add(new_borrow)
        db.session.commit()
    return redirect(url_for("index"))

@app.route("/return/<int:borrow_id>")
def return_book(borrow_id):
    borrow = Borrow.query.get_or_404(borrow_id)
    borrow.return_date = datetime.utcnow()
    borrow.book.is_borrowed = False
    db.session.commit()
    return redirect(url_for("index"))

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
