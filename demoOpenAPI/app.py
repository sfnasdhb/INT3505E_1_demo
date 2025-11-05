import connexion
import jwt
import time
import uuid
from werkzeug.security import check_password_hash
from connexion.resolver import RestyResolver
from flask import redirect, request

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

db_clients = {
    "my-awesome-client": {
        "client_id": "my-awesome-client",
        "client_secret": "my-super-secret",
        "redirect_uri": "http://127.0.0.1:5000/callback" # Nơi Auth Server sẽ trả code về
    }
}

# "Bảng" lưu các authorization_code tạm thời
db_auth_codes = {}

# === CÁC HÀM TẠO TOKEN MỚI CHO OIDC/OAUTH ===

def _create_id_token(user, client_id):
    """Tạo một ID Token theo chuẩn OIDC."""
    payload = {
        'iss': 'http://localhost:8080', # Issuer - Ai đã cấp token
        'sub': user['username'],        # Subject - ID của người dùng
        'aud': client_id,               # Audience - Token này dành cho client nào
        'name': f"Mr. {user['username'].capitalize()}", # Thông tin hồ sơ
        'exp': time.time() + 3600,
        'iat': time.time()
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')

def _create_access_token(user, client_id, scope):
    """Tạo một Access Token chứa scope."""
    payload = {
        'iss': 'http://localhost:8080',
        'sub': user['username'],
        'aud': client_id,
        'scope': scope, # Các quyền được cấp
        'exp': time.time() + 3600,
        'iat': time.time()
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')


# === CÁC ENDPOINT MỚI CHO LUỒNG OAUTH/OIDC ===

def authorize():
    """Mô phỏng trang đăng nhập và đồng ý của người dùng."""
    client_id = request.args.get('client_id')
    redirect_uri = request.args.get('redirect_uri')
    scope = request.args.get('scope', '')
    
    # 1. Xác thực Client
    client = db_clients.get(client_id)
    if not client or client['redirect_uri'] != redirect_uri:
        return {"error": "invalid_client"}, 400

    # 2. (Mô phỏng) Giả sử người dùng "admin" đã đăng nhập và đồng ý
    # Trong thực tế, đây sẽ là một trang HTML yêu cầu username/password
    user = db_users['admin']

    # 3. Tạo và lưu authorization_code
    auth_code = str(uuid.uuid4())
    db_auth_codes[auth_code] = {
        "client_id": client_id,
        "user": user,
        "scope": scope,
        "exp": time.time() + 600 # Code chỉ hợp lệ trong 10 phút
    }
    
    # 4. Chuyển hướng người dùng trở lại Client với code
    return redirect(f"{redirect_uri}?code={auth_code}")

def token():
    """Endpoint để Client đổi authorization_code lấy token."""
    # 1. Đọc dữ liệu từ form
    data = request.form
    auth_code = data.get('code')
    client_id = data.get('client_id')
    client_secret = data.get('client_secret')

    # 2. Xác thực Client
    client = db_clients.get(client_id)
    if not client or client['client_secret'] != client_secret:
        return {"error": "invalid_client"}, 401

    # 3. Xác thực code
    code_data = db_auth_codes.get(auth_code)
    if not code_data or code_data['client_id'] != client_id or time.time() > code_data['exp']:
        return {"error": "invalid_grant"}, 400

    # Xóa code đã dùng
    del db_auth_codes[auth_code]

    # 4. Cấp token
    user = code_data['user']
    scope = code_data['scope']
    tokens = {
        "access_token": _create_access_token(user, client_id, scope),
        "token_type": "Bearer",
        "expires_in": 3600,
    }
    if 'openid' in scope:
        tokens["id_token"] = _create_id_token(user, client_id)

    return tokens, 200

def get_profile(token_info):
    """
    Một Resource được bảo vệ.
    token_info là payload của ACCESS TOKEN đã được xác thực.
    """
    # KIỂM TRA SCOPE (Authorization)
    required_scope = 'profile'
    if required_scope not in token_info.get('scope', ''):
        return {"error": "insufficient_scope", "message": f"'{required_scope}' scope is required"}, 403

    # Trả về tài nguyên
    username = token_info['sub']
    user_profile = {
        "username": username,
        "email": f"{username}@example.com",
        "motto": "I build great APIs!"
    }
    return user_profile, 200

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
    # trả về dictionary có key là author_id và value là đối tượng author

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

def get_books_with_authors_optimized():
    """
    HÀM NÀY ĐÃ ĐƯỢC TỐI ƯU, GIẢI QUYẾT VẤN ĐỀ N+1.
    """
    print("\n=== BẮT ĐẦU KỊCH BẢN TỐI ƯU (EAGER LOADING) ===")
    
    # 1. Lấy tất cả sách (1 QUERY)
    all_books = find_all_books()
    
    # 2. Thu thập tất cả các author_id cần thiết từ danh sách sách
    author_ids_needed = [book['author_id'] for book in all_books]
    
    # 3. Lấy TẤT CẢ các tác giả cần thiết chỉ trong 1 CÂU QUERY
    authors_map = find_authors_by_ids(author_ids_needed)
    # authors_map sẽ có dạng: {101: {author_obj_101}, 102: {author_obj_102}, ...}
    
    results = []
    # 4. Lặp qua từng cuốn sách (KHÔNG CÓ QUERY NÀO Ở ĐÂY)
    for book in all_books:
        # Lấy thông tin tác giả từ map đã có sẵn trong bộ nhớ
        author = authors_map.get(book['author_id'])
        
        book_with_author = {
            "id": book['id'],
            "title": book['title'],
            "author": author
        }
        results.append(book_with_author)
        
    print("=== KẾT THÚC KỊCH BẢN TỐI ƯU: TỔNG CỘNG CHỈ CÓ 2 QUERIES! ===")
    return results, 200
    
def decode_token(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'], options={"verify_aud": False})

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

# ---- BOOK CRUD + LIST (xuất ra author là string, lưu nội bộ author_id) ----

def get_all_books(limit=10, offset=0, author=None, title_contains=None):
    # Lấy danh sách và map author_id -> author name tại chỗ
    books_raw = list(db_books.values())

    # Map sang list có 'author' (string) cho đúng schema trả ra
    books_out = []
    for b in books_raw:
        a = db_authors.get(b['author_id'])
        books_out.append({
            "id": b["id"],
            "title": b["title"],
            "author": a["name"] if a else None
        })

    # Lọc theo author (string) / title
    if author:
        au = author.lower()
        books_out = [bk for bk in books_out if (bk["author"] or "").lower() == au]

    if title_contains:
        kw = title_contains.lower()
        books_out = [bk for bk in books_out if kw in bk["title"].lower()]

    # Phân trang an toàn
    total_items = len(books_out)
    if offset < 0:
        offset = 0
    limit = int(limit) if limit is not None else 10
    paginated = books_out[offset: offset + max(0, limit)]

    return {
        "metadata": {
            "total_items": total_items,
            "offset": offset,
            "limit": limit,
            "item_count": len(paginated)
        },
        "data": paginated
    }, 200


def get_all_books_by_cursor(limit=5, after_cursor=0):
    # Sắp xếp theo id, rồi map author_id -> author name khi trả ra
    all_books = sorted(list(db_books.values()), key=lambda x: x['id'])

    start_index = 0
    if after_cursor and after_cursor > 0:
        for i, b in enumerate(all_books):
            if b['id'] == after_cursor:
                start_index = i + 1
                break

    limit = int(limit) if limit is not None else 5
    slice_books = all_books[start_index: start_index + max(0, limit)]

    data = []
    for b in slice_books:
        a = db_authors.get(b['author_id'])
        data.append({
            "id": b["id"],
            "title": b["title"],
            "author": a["name"] if a else None
        })

    next_cursor = None
    if data:
        last_id = data[-1]['id']
        # còn phần tử phía sau không?
        for i, b in enumerate(all_books):
            if b['id'] == last_id and i < len(all_books) - 1:
                next_cursor = last_id
                break

    return {
        "metadata": {
            "item_count": len(data),
            "next_cursor": next_cursor,
            "has_next_page": next_cursor is not None
        },
        "data": data
    }, 200


def get_book_by_id(bookID, token_info):
    b = db_books.get(bookID)
    if not b:
        return {"message": "Book not found"}, 404
    a = db_authors.get(b['author_id'])
    return {"id": b["id"], "title": b["title"], "author": a["name"] if a else None}, 200


def create_book(body, token_info):
    # Lưu nội bộ theo author_id; đầu vào body['author'] là tên tác giả (string)
    print("Hành động được thực hiện bởi:", token_info['sub'])
    global book_id_counter
    book_id_counter += 1

    author_name = body['author']
    author_id = None
    low = author_name.lower()
    for aid, a in db_authors.items():
        if a['name'].lower() == low:
            author_id = aid
            break

    # nếu không match, vẫn cho tạo với author_id=None
    db_books[book_id_counter] = {
        "id": book_id_counter,
        "title": body['title'],
        "author_id": author_id
    }

    return {"id": book_id_counter, "title": body['title'], "author": author_name}, 201


def update_book_by_id(bookID, body, token_info):
    print("Hành động được thực hiện bởi:", token_info['sub'])
    b = db_books.get(bookID)
    if not b:
        return {"message": "Book not found"}, 404

    author_name = body['author']
    author_id = None
    low = author_name.lower()
    for aid, a in db_authors.items():
        if a['name'].lower() == low:
            author_id = aid
            break

    b['title'] = body['title']
    b['author_id'] = author_id

    return {"id": b["id"], "title": b["title"], "author": author_name}, 200


def delete_book_by_id(bookID, token_info):
    if bookID in db_books:
        del db_books[bookID]
        return "", 204  # khớp openapi.yaml: 204 No Content
    return {"message": "Book not found"}, 404


def simulate_insert_start(body):
    """Mô phỏng chèn sách vào đầu danh sách (vẫn lưu bằng author_id)."""
    global book_id_counter
    book_id_counter += 1

    author_name = body.get('author', 'Tác Giả Mới')
    author_id = None
    low = author_name.lower()
    for aid, a in db_authors.items():
        if a['name'].lower() == low:
            author_id = aid
            break

    new_book_internal = {
        "id": book_id_counter,
        "title": body.get('title', 'Sách Mới Chèn'),
        "author_id": author_id
    }

    # chèn vào "đầu" (mô phỏng)
    temp = {book_id_counter: new_book_internal}
    temp.update(db_books)
    db_books.clear()
    db_books.update(temp)

    print(f"--- SIMULATE INSERT: Book {book_id_counter} inserted ---")
    # trả về đúng schema: author là string (tên)
    return {
        "id": new_book_internal["id"],
        "title": new_book_internal["title"],
        "author": author_name
    }, 201

app = connexion.App(__name__, specification_dir='.')
app.add_api(
    'openapi.yaml',
    resolver=RestyResolver('app')
)

if __name__ == '__main__':
    app.run(port=8080)