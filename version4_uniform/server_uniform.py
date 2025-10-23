# version4_uniform/server_uniform.py
from flask import Flask, jsonify, request, url_for

app = Flask(__name__)

books = {
    1: {"title": "Lão Hạc", "author": "Nam Cao"},
    2: {"title": "Số Đỏ", "author": "Vũ Trọng Phụng"}
}
next_book_id = 3

def add_hypermedia(book_data, book_id):
    """Thêm các liên kết HATEOAS vào biểu diễn của sách."""
    book_data['_links'] = {
        "self": {
            "href": url_for('get_book', book_id=book_id, _external=True),
            "method": "GET"
        },
        "collection": {
            "href": url_for('get_books', _external=True),
            "method": "GET"
        },
        "update": {
            "href": url_for('get_book', book_id=book_id, _external=True),
            "method": "PUT"
        }
    }
    return book_data

@app.route('/api/books', methods=['GET'])
def get_books():
    """1. URI để định danh bộ sưu tập tài nguyên."""
    """3. Phản hồi tự mô tả (Content-Type)."""
    book_list = [add_hypermedia(book, book_id) for book_id, book in books.items()]
    return jsonify({"books": book_list})

@app.route('/api/books/<int:book_id>', methods=['GET'])
def get_book(book_id):
    """1. URI để định danh một tài nguyên cụ thể."""
    book = books.get(book_id)
    if not book:
        return jsonify({"error": "Không tìm thấy sách"}), 404
    
    # 4. HATEOAS: Phản hồi chứa các link hành động liên quan
    return jsonify(add_hypermedia(book.copy(), book_id))

@app.route('/api/books', methods=['POST'])
def create_book():
    """2. Thao tác trên tài nguyên qua biểu diễn (JSON)."""
    """3. Thông điệp tự mô tả (phương thức POST)."""
    if not request.json or 'title' not in request.json:
        return jsonify({"error": "Thiếu 'title'"}), 400
    
    global next_book_id
    new_book = {
        "title": request.json['title'],
        "author": request.json.get('author', 'Chưa rõ')
    }
    books[next_book_id] = new_book
    created_book_representation = add_hypermedia(new_book.copy(), next_book_id)
    next_book_id += 1
    
    return jsonify(created_book_representation), 201

if __name__ == '__main__':
    app.run(port=5003, debug=True)