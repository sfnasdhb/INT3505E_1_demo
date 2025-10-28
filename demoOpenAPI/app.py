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

db_authors = {
    101: {"id": 101, "name": "Nam Cao"},
    102: {"id": 102, "name": "Vũ Trọng Phụng"},
    103: {"id": 103, "name": "Ngô Tất Tố"}
}

db_books = {
    1: {"id": 1, "title": "Lão Hạc", "author_id": 101},
    2: {"id": 2, "title": "Số Đỏ", "author_id": 102},
    3: {"id": 3, "title": "Chí Phèo", "author_id": 101},
    4: {"id": 4, "title": "Tắt Đèn", "author_id": 103},
    5: {"id": 5, "title": "Giông Tố", "author_id": 102},
    6: {"id": 6, "title": "Đời Thừa", "author_id": 101},
}

initial_db_books = dict(db_books)

def reset_db():
    """Khôi phục db_books về trạng thái ban đầu."""
    global db_books, book_id_counter
    db_books = dict(initial_db_books)
    book_id_counter = len(db_books)
    print("--- DATABASE RESET ---")
    return {"message": "Database has been reset to its initial state."}, 200

book_id_counter = len(db_books)

def find_all_books():
    # In ra log NGAY KHI được gọi
    print("[DB-ACCESS] EXECUTING: SELECT * FROM books;")
    return list(db_books.values())

def find_author_by_id(author_id):
    # In ra log NGAY KHI được gọi
    print(f"[DB-ACCESS] EXECUTING: SELECT * FROM authors WHERE id = {author_id};")
    return db_authors.get(author_id)
    
def find_authors_by_ids(author_ids):
    unique_ids = set(author_ids)
    # In ra log NGAY KHI được gọi
    print(f"[DB-ACCESS] EXECUTING: SELECT * FROM authors WHERE id IN {tuple(unique_ids)};")
    return {id: db_authors[id] for id in unique_ids if id in db_authors}

def get_books_with_author_n1():
    """
    HÀM NÀY BỊ LỖI N+1 QUERY. DÙNG ĐỂ DEMO.
    """
    print("\n=== BẮT ĐẦU KỊCH BẢN LỖI N+1 QUERY ===")
    
    # 1. Lấy tất cả sách (THỰC HIỆN 1 CÂU QUERY ĐẦU TIÊN)
    all_books = find_all_books()
    
    results = []
    # 2. Lặp qua từng cuốn sách
    for book in all_books:
        # Với MỖI cuốn sách, lại thực hiện 1 CÂU QUERY để lấy tác giả
        # Đây chính là N CÂU QUERY TIẾP THEO
        author = find_author_by_id(book['author_id'])
        
        # Ghép kết quả
        book_with_author = {
            "id": book['id'],
            "title": book['title'],
            "author": author # Lồng đối tượng tác giả vào
        }
        results.append(book_with_author)
        
    print(f"=== KẾT THÚC KỊCH BẢN LỖI: TỔNG CỘNG {1 + len(all_books)} QUERIES ĐÃ ĐƯỢC THỰC THI! ===")
    return results, 200

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

def get_all_books(limit=10, offset=0, author=None, title_contains=None):
    books = list(db_books.values())
    
    if author:
        books = [book for book in books if book['author'].lower() == author.lower()]

    if title_contains:
        books = [book for book in books if title_contains.lower() in book['title'].lower()]
        
    total_items = len(books)

    paginated_books = books[offset : offset + limit]

    response = {
        "metadata": {
            "total_items": total_items,
            "offset": offset,
            "limit": limit,
            "item_count": len(paginated_books) 
        },
        "data": paginated_books
    }
    
    return response, 200
    #tuy nhiên sẽ xảy ra lỗi offset nếu offset > total_items
    #lỗi không đồng bộ, tức ví dụ:
    #A,B,C,D,E,F,G,H,I,J
    #limit=5,offset=0 -> A,B,C,D,E
    #xóa E -> limit=5,offset=5 -> G,H,I,J (thiếu F) (A,B,C,D,F,G,H,I,J)
    #đang xem trang 1 có A, B, C, D, F
    #chèn V vào giữa D và F -> A,B,C,D,V,F,G,H,I,J
    #limit=5,offset=5 -> F,G,H,I,J -> nhìn thấy F hai lần

def get_all_books_by_cursor(limit=5, after_cursor=0):
    """
    Lấy danh sách sách sử dụng Cursor Pagination.
    Con trỏ ở đây chính là ID của cuốn sách.
    - limit: Số lượng sách cần lấy.
    - after_cursor: ID của cuốn sách cuối cùng đã thấy ở trang trước.
    """
    # Lấy toàn bộ sách và đảm bảo chúng được sắp xếp theo ID (con trỏ)
    all_books = sorted(list(db_books.values()), key=lambda x: x['id'])

    # Tìm vị trí bắt đầu để lấy dữ liệu
    start_index = 0
    if after_cursor > 0:
        # Tìm index của cuốn sách có ID là cursor
        found_index = -1
        for i, book in enumerate(all_books):
            if book['id'] == after_cursor:
                found_index = i
                break   
        
        # Nếu tìm thấy, vị trí bắt đầu sẽ là ngay sau nó
        if found_index != -1:
            start_index = found_index + 1

    # Lấy lát cắt dữ liệu cho trang hiện tại
    results = all_books[start_index : start_index + limit]

    # Xác định con trỏ cho trang tiếp theo
    next_cursor = None
    if len(results) > 0:
        # Lấy ID của cuốn sách cuối cùng trong kết quả
        last_book_id = results[-1]['id']
        
        # Kiểm tra xem có còn sách nào sau cuốn sách cuối cùng này không
        # (Bằng cách xem index của nó trong danh sách đầy đủ)
        last_book_index_in_all = -1
        for i, book in enumerate(all_books):
            if book['id'] == last_book_id:
                last_book_index_in_all = i
                break
        
        if last_book_index_in_all < len(all_books) - 1:
            next_cursor = last_book_id

    # Tạo cấu trúc response
    response = {
        "metadata": {
            "item_count": len(results),
            "next_cursor": next_cursor, # Con trỏ để client dùng cho lần gọi sau
            "has_next_page": next_cursor is not None
        },
        "data": results
    }
    
    return response, 200

def get_book_by_id(bookID, token_info): 
    book = db_books.get(bookID)
    if book:
        return book, 200
    return {"message": "Book not found"}, 404

def simulate_insert_start(body):
    """Mô phỏng việc chèn một cuốn sách mới vào đầu danh sách."""
    global book_id_counter
    book_id_counter += 1
    new_book = {
        "id": book_id_counter,
        "title": body.get('title', 'Sách Mới Chèn'),
        "author": body.get('author', 'Tác Giả Mới')
    }
    
    # Để chèn vào "đầu", chúng ta phải tạo một dict mới
    # Đây là cách mô phỏng, trong SQL thực tế nó sẽ tự sắp xếp
    temp_db = {book_id_counter: new_book}
    temp_db.update(db_books)
    db_books.clear()
    db_books.update(temp_db)
    
    print(f"--- SIMULATE INSERT: Book {book_id_counter} inserted ---")
    return new_book, 201

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

def find_all_books():
    # In ra log NGAY KHI được gọi
    print("[DB-ACCESS] EXECUTING: SELECT * FROM books;")
    return list(db_books.values())

def find_author_by_id(author_id):
    # In ra log NGAY KHI được gọi
    print(f"[DB-ACCESS] EXECUTING: SELECT * FROM authors WHERE id = {author_id};")
    return db_authors.get(author_id)
    
def find_authors_by_ids(author_ids):
    unique_ids = set(author_ids)
    # In ra log NGAY KHI được gọi
    print(f"[DB-ACCESS] EXECUTING: SELECT * FROM authors WHERE id IN {tuple(unique_ids)};")
    return {id: db_authors[id] for id in unique_ids if id in db_authors}

app = connexion.App(__name__, specification_dir='.')
app.add_api(
    'openapi.yaml',
    resolver=RestyResolver('app')
)

if __name__ == '__main__':
    app.run(port=8080)