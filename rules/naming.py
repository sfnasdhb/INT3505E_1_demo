from flask import Blueprint, jsonify

bp = Blueprint("naming", __name__)

# ====== GOOD: Danh từ số nhiều, chữ thường, dùng hyphen ======
@bp.get("/good/user-profiles/<int:profile_id>")
def good_user_profile(profile_id: int):
    return jsonify({"id": profile_id, "resource": "user-profiles"})

@bp.get("/good/shopping-cart/items")
def good_cart_items():
    return jsonify({"collection": "shopping-cart/items"})

@bp.post("/good/users")
def good_create_user():
    # POST /good/users — hành động do HTTP method quyết định, URL là danh từ số nhiều
    return jsonify({"detail": "Created"}), 201

# ====== BAD: Động từ trong URL, hoa/thường lẫn lộn, dùng underscore ======
@bp.get("/bad/Users/1/Orders")
def bad_mixed_case():
    return jsonify({"Status": "OK"})  # field viết hoa lung tung

@bp.post("/bad/create-user")
def bad_verb_in_url():
    return jsonify({"message": "User created"}), 201

@bp.get("/bad/user_profiles/1")
def bad_underscore():
    return jsonify({"id": 1, "resource": "user_profiles"})
