from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///books.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return f'Book {self.id}: {self.title} by {self.author}'


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        book = Book(title=title, author=author)
        with app.app_context():
            db.session.add(book)
            db.session.commit()

        # Here we redirect to the index page after processing the form to avoid resubmission
        return redirect(url_for('index'))

    with app.app_context():
        all_books = Book.query.all()
    return render_template('index.html', all_books=all_books)


@app.route('/delete/<int:id>')
def delete(id):
    with app.app_context():
        book_to_delete = Book.query.get_or_404(id)
        db.session.delete(book_to_delete)
        db.session.commit()
    return redirect(url_for('index'))


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
