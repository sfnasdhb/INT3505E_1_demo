# rules/naming.py
from flask import Blueprint, jsonify, request
from data import users_db, order_items_db, next_user_id

# Blueprint cho các quy tắc ĐÚNG
good_bp = Blueprint('good_naming_bp', __name__)

# Dùng danh từ số nhiều
@good_bp.route('/v1/users', methods=['GET'])
def get_users():
    return jsonify(list(users_db.values()))

@good_bp.route('/v1/users/<int:user_id>', methods=['GET'])
def get_user_by_id(user_id):
    return jsonify(users_db.get(user_id, {}))
# Dùng post để tạo, tuy nhưng không được dùng động từ trong URI
@good_bp.route('/v1/users', methods=['POST'])
def create_user():
    req_data = request.get_json()
    new_user = {
        "id": next_user_id,
        "name": req_data.get('name'),
        "email": req_data.get('email', '')
    }
    users_db[next_user_id] = new_user
    next_user_id += 1
    return jsonify(new_user), 201

# Dùng dấu gạch ngang
@good_bp.route('/v1/order-items', methods=['GET'])
def get_order_items():
    return jsonify(list(order_items_db.values()))

# TỐT: Dùng query parameter để lọc, sắp xếp
# /v1/users/search?status=active
@good_bp.route('/v1/users/search', methods=['GET'])
def search_users():
    status = request.args.get('status')
    return jsonify({"message": f"Searching for users with status: {status}"})

# Blueprint cho các quy tắc SAI
bad_bp = Blueprint('bad_naming_bp', __name__)

# Dùng danh từ số ít
@bad_bp.route('/v1/user/<int:user_id>', methods=['GET'])
def get_single_user(user_id):
    return jsonify(users_db.get(user_id, {}))

# Dùng động từ trong URI
@bad_bp.route('/v1/getAllUsers', methods=['GET'])
def get_all_users():
    return jsonify(list(users_db.values()))

@bad_bp.route('/v1/createNewUser', methods=['POST'])
def create_a_new_user():
    return jsonify({"message": "User created via a bad endpoint"}), 201

# KHÔNG TỐT: Dùng camelCase hoặc snake_case
@bad_bp.route('/v1/orderItems', methods=['GET']) # camelCase
def getOrderItems():
    return jsonify({"message": "Endpoint with camelCase is not recommended"})

@bad_bp.route('/v1/product_categories', methods=['GET']) # snake_case
def get_product_categories():
    return jsonify({"message": "Endpoint with snake_case is not recommended"})
    
# KHÔNG TỐT: Đưa tham số lọc vào path thay vì query parameter
@bad_bp.route('/v1/users/status/<string:status>', methods=['GET'])
def get_users_by_status_in_path(status):
    return jsonify({"message": f"Filtering users by status '{status}' in path is inflexible"})