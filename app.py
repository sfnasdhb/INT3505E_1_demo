import connexion

db_books = {
    1: {"id": 1, "title": "Lão Hạc", "author": "Nam Cao"},
    2: {"id": 2, "title": "Số Đỏ", "author": "Vũ Trọng Phụng"},
    3: {"id": 1, "title": "Lão Hạc2", "author": "Nam Cao"},
    4: {"id": 2, "title": "Số Đỏ2", "author": "Vũ Trọng Phụng"},
    5: {"id": 1, "title": "Lão Hạc3", "author": "Nam Cao"},
    6: {"id": 2, "title": "Số Đỏ3", "author": "Vũ Trọng Phụng"},
}

book_id_counter = len(db_books)

def get_all_books():
    return list(db_books.values()), 200

def get_book_by_id(bookID):
    book = db_books.get(bookID)
    if book:
        return book, 200
    return {"message": "Book not found"}, 404

def create_book(body):
    global book_id_counter
    book_id_counter+=1
    body['id']=book_id_counter
    new_book = {
        "id": book_id_counter,
        "title": body['title'],
        "author": body['author']
    }
    db_books[book_id_counter] = new_book
    return new_book, 201

def update_book_by_id(bookID, body):
    existing_book = db_books.get(bookID)
    if existing_book:
        existing_book['title'] = body['title']
        existing_book['author'] = body['author']
        return existing_book, 200

def delete_book_by_id(bookID):
    if bookID in db_books:
        title = db_books[bookID]['title']
        del db_books[bookID]
        return {"message": f"Book deleted: {title}"}, 200
    return {"message": "Book not found"}, 404

app = connexion.App(__name__, specification_dir='.')
app.add_api('openapi.yaml')

if __name__ == '__main__':
    app.run(port=8080)