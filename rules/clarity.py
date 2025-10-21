from flask import Blueprint, jsonify, request
from data import users_db

good_clarity_bp = Blueprint('good_clarity_bp', __name__)

# Dùng GET để lấy
@good_clarity_bp.route('/users/<int:user_id>', methods=['GET'])
def get_user_good(user_id):
    return jsonify(users_db.get(user_id, {}))

# Dùng DELETE để xóa
@good_clarity_bp.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user_good(user_id):
    if user_id in users_db:
        del users_db[user_id] # Xóa user khỏi database
        return jsonify({"message": f"User {user_id} deleted"}), 200
    return jsonify({"error": "User not found"}), 404


bad_clarity_bp = Blueprint('bad_clarity_bp', __name__)

# Dùng POST để xóa (sai ngữ nghĩa)
@bad_clarity_bp.route('/delete-user-action', methods=['POST'])
def delete_user_bad():
    user_id = request.get_json().get('user_id')
    if user_id and user_id in users_db:
        del users_db[user_id] # Xóa user khỏi database
        return jsonify({"message": f"User {user_id} deleted via POST"})
    return jsonify({"error": "User not found or missing user_id"}), 404