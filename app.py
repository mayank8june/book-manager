import io
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import csv
from flask import Response
from flask_migrate import Migrate

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///books.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)


class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(200), nullable=False)
    genre = db.Column(db.String(200))

    def __repr__(self):
        return f'Book {self.id}: {self.title} by {self.author}'


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        genre = request.form['genre']
        book = Book(title=title, author=author, genre=genre)
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


@app.route('/import', methods=['POST'])
def import_books():
    if 'file' not in request.files:
        # No file part in the request
        return redirect(url_for('index'))

    file = request.files['file']

    if file.filename == '':
        # No selected file
        return redirect(url_for('index'))

    if file:
        # Read and import data from the uploaded CSV file
        data = csv.reader(file.stream.read().decode('utf-8').splitlines())
        next(data)  # Skip header row if it exists

        with app.app_context():
            for row in data:
                title, author = row
                new_book = Book(title=title, author=author)
                db.session.add(new_book)

            db.session.commit()

        return redirect(url_for('index'))


@app.route('/export', methods=['GET'])
def export_books():
    books = Book.query.all()

    # Prepare data for CSV export
    data = [
               ['Title', 'Author']
           ] + [
               [book.title, book.author]
               for book in books
           ]
    # Set up the response
    csv_filename = 'books_export.csv'
    response = Response(
        generate_csv(data),
        content_type='text/csv',
        headers={'Content-Disposition': f'attachment; filename={csv_filename}'}
    )

    return response


def generate_csv(data):
    output = io.StringIO()
    writer = csv.writer(output)

    # Write header
    writer.writerow(['Title', 'Author'])

    # Write data
    writer.writerows(data)

    return output.getvalue()


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
