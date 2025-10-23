# rules/extensibility.py
from flask import Blueprint, jsonify
from data import users_db

good_extensibility_bp = Blueprint('good_extensibility_bp', __name__)

@good_extensibility_bp.route('/v1/users/<int:user_id>', methods=['GET'])
def get_user_v1(user_id):
    user = users_db.get(user_id, {})
    # V1 chỉ trả về các trường cơ bản
    return jsonify({"id": user.get("id"), "name": user.get("name")})

@good_extensibility_bp.route('/v2/users/<int:user_id>', methods=['GET'])
def get_user_v2(user_id):
    user = users_db.get(user_id, {})
    # V2 mở rộng thêm dữ liệu mà không làm hỏng V1
    return jsonify({
        "id": user.get("id"),
        "name": user.get("name"),
        "email": user.get("email"), # Thêm trường mới
        "status": "active"        # Thêm trường mới
    })

bad_extensibility_bp = Blueprint('bad_extensibility_bp', __name__)

@bad_extensibility_bp.route('/users/<int:user_id>', methods=['GET'])
def get_user_no_version(user_id):
    user = users_db.get(user_id, {})
    # Ban đầu api trả về chỉ id và name
    # return jsonify({"id": user.get("id"), "name": user.get("name")})
    
    # Muốn thêm trường email, ta thêm trực tiếp vào API hiện tại
    # -> Tất cả ứng dụng client cũ đang dùng API này có thể bị lỗi vì ban đầu không có email
    return jsonify({
        "id": user.get("id"),
        "name": user.get("name"),
        "email": user.get("email") 
    })