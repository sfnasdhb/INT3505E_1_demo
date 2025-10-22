import connexion
import jwt
import time
from werkzeug.security import check_password_hash
from connexion.resolver import RestyResolver

SECRET_KEY = 'mysecretkey'

db_users = {
    "admin": {
        'username': 'admin',
        'password_hash': 'pbkdf2:sha256:260000$DJ48YJoSVrjHhGOG$4457d774cc220942a7c72b791becfad1327b7ccc5f2c8e5ebba25d46964721b9'  
    }

}
db_books = {
    1: {"id": 1, "title": "Lão Hạc", "author": "Nam Cao"},
    2: {"id": 2, "title": "Số Đỏ", "author": "Vũ Trọng Phụng"},
    3: {"id": 1, "title": "Lão Hạc2", "author": "Nam Cao"},
    4: {"id": 2, "title": "Số Đỏ2", "author": "Vũ Trọng Phụng"},
    5: {"id": 1, "title": "Lão Hạc3", "author": "Nam Cao"},
    6: {"id": 2, "title": "Số Đỏ3", "author": "Vũ Trọng Phụng"},
}

book_id_counter = len(db_books)

def decode_token(token):
    try:
        payload=jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        # nếu thành công, payload sẽ có dạng:
        # {'sub': 'admin', 'iat': 1678886400, 'exp': 1678887300}
        return payload
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None
    
def login(body):
    username = body.get('username')
    password = body.get('password')
    user = db_users.get(username)
    if user and check_password_hash(user['password_hash'], password):
        payload = {
            'sub': username,
            'exp': time.time() + 3600  # token hết hạn sau 1 giờ
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
        return {'access_token': token}, 200
    return {'message': 'Invalid credentials'}, 401

def get_all_books():
    return list(db_books.values()), 200

def get_book_by_id(bookID, token_info): 
    book = db_books.get(bookID)
    if book:
        return book, 200
    return {"message": "Book not found"}, 404

def create_book(body, token_info): # tham số token_info: được sinh ra ở phía server khi gọi hàm decode_token (khi giải mã thành công)
                        # chính là payload được return
    print("Hành động được thực hiện bởi:", token_info['sub'])  
    global book_id_counter
    book_id_counter+=1
    new_book = {
        "id": book_id_counter,
        "title": body['title'],
        "author": body['author']
    }
    db_books[book_id_counter] = new_book
    return new_book, 201

def update_book_by_id(bookID, body, token_info):
    print("Hành động được thực hiện bởi:", token_info['sub'])
    existing_book = db_books.get(bookID)
    if existing_book:
        existing_book['title'] = body['title']
        existing_book['author'] = body['author']
        return existing_book, 200

def delete_book_by_id(bookID, token_info):
    
    if bookID in db_books:
        title = db_books[bookID]['title']
        del db_books[bookID]
        return {"message": f"Book deleted: {title}"}, 200
    return {"message": "Book not found"}, 404

app = connexion.App(__name__, specification_dir='.')
app.add_api(
    'openapi.yaml',
    resolver=RestyResolver('app')
)

if __name__ == '__main__':
    app.run(port=8080)