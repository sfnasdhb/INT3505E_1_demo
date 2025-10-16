from flask import Blueprint, jsonify, request
from data import USERS, POSTS

bp = Blueprint("consistency", __name__)

# ====== GOOD: Nhất quán path param, field style, và error format ======
@bp.get("/good/users")
def good_list_users():
    return jsonify([
        {"id": u["id"], "full_name": u["full_name"], "email": u["email"]} 
        for u in USERS
    ])  #các field có cùng kiểu viết: full_name, id,...

@bp.get("/good/users/<int:user_id>")
def good_get_user(user_id: int):
    user = next((u for u in USERS if u["id"] == user_id), None)
    if not user:
        return jsonify({"detail": "User not found"}), 404
    return jsonify({"id": user["id"], "full_name": user["full_name"], "email": user["email"]})
    # field có cùng kiểu viết, truyền vào path param 

@bp.get("/good/posts/<int:post_id>")
def good_get_post(post_id: int):
    post = next((p for p in POSTS if p["id"] == post_id), None)
    if not post:
        return jsonify({"detail": "Post not found"}), 404
    return jsonify(post)
#có dữ liệu trả về theo dạng {...}, lỗi thì trả về {"detail":...}

# ====== BAD: Không nhất quán (query vs path, error key lẫn lộn, case style lộn xộn) ======
@bp.get("/bad/api/posts")
def bad_posts_get():
    """
    - Dùng query param cho id (post_id) thay vì path param.
    - Error key khi thì 'message', khi thì 'error'.
    - Trộn camelCase & snake_case.
    """
    pid = request.args.get("post_id", type=int)
    if pid is None:
        return jsonify({"message": "post_id query is required"}), 400
    post = next((p for p in POSTS if p["id"] == pid), None)
    if not post:
        return jsonify({"error": "This post does not exist"}), 404
    return jsonify({"postId": post["id"], "post_title": post["title"], "authorId": post["author_id"]})
