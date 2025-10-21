# rules/consistency.py
from flask import Blueprint, jsonify
from data import users_db, order_items_db

good_consistency_bp = Blueprint('good_consistency_bp', __name__)

def create_success_response(data):
    return jsonify({"status": "success", "data": data})

@good_consistency_bp.route('/users', methods=['GET'])
def get_users_consistent():
    return create_success_response(list(users_db.values()))

@good_consistency_bp.route('/order-items', methods=['GET'])
def get_order_items_consistent():
    # Cả hai đều trả về cùng cấu trúc
    return create_success_response(list(order_items_db.values()))

bad_consistency_bp = Blueprint('bad_consistency_bp', __name__)

@bad_consistency_bp.route('/users', methods=['GET'])
def get_users_inconsistent():
    # Trả về một object với key là "users"
    return jsonify({"users": list(users_db.values())})

@bad_consistency_bp.route('/order-items', methods=['GET'])
def get_order_items_inconsistent():
    # Lại trả về một list trần, không có key bao bọc
    return jsonify(list(order_items_db.values()))