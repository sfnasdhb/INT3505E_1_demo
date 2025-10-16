from flask import Blueprint, jsonify, url_for
from data import USERS

bp = Blueprint("extensibility", __name__)

# ====== GOOD: Có versioning — v1 và v2 cùng tồn tại an toàn ======
@bp.get("/good/v1/users/<int:user_id>")
def v1_get_user(user_id: int):
    """
    v1 schema: giữ 'name' (client cũ vẫn chạy ổn)
    """
    user = next((u for u in USERS if u["id"] == user_id), None)
    if not user:
        return jsonify({"detail": "User not found"}), 404
    return jsonify({"id": user["id"], "name": user["full_name"], "email": user["email"]})

@bp.get("/good/v2/users/<int:user_id>")
def v2_get_user(user_id: int):
    """
    v2 schema: tách firstName/lastName (breaking change) nhưng an toàn nhờ version.
    """
    user = next((u for u in USERS if u["id"] == user_id), None)
    if not user:
        return jsonify({"detail": "User not found"}), 404
    first, *last = user["full_name"].split(" ")
    return jsonify({
        "id": user["id"],
        "firstName": first,
        "lastName": " ".join(last) if last else "",
        "email": user["email"],
    })

# ====== BAD: Thay đổi phá vỡ schema mà không version ======
@bp.get("/bad/users/<int:user_id>")
def bad_breaking_change(user_id: int):
    """
    Ví dụ SAI:
    - Ban đầu trả {"id","name"}; sau đó sửa thành {"id","firstName","lastName"} => client cũ lỗi.
    """
    user = next((u for u in USERS if u["id"] == user_id), None)
    if not user:
        return jsonify({"msg": "not found"}), 404  # lỗi format không nhất quán
    first, *last = user["full_name"].split(" ")
    return jsonify({"id": user["id"], "firstName": first, "lastName": " ".join(last)})
