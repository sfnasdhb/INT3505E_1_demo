# version2_stateless/server_stateless.py
from flask import Flask, jsonify, request

app = Flask(__name__)

users_data = {
    "user1-token": {"username": "Alice", "email": "alice@example.com"},
    "user2-token": {"username": "Bob", "email": "bob@example.com"}
}

@app.route('/api/profile', methods=['GET'])
def get_profile():
    """
    Endpoint này yêu cầu xác thực.
    Nó không lưu session, mà kiểm tra token trong mỗi request.
    """    
    auth_header = request.headers.get('Authorization')
    
    if not auth_header:
        return jsonify({"error": "Yêu cầu cần xác thực"}), 401
    
    try:
        token = auth_header.split(" ")[1]
    except IndexError:
        return jsonify({"error": "Định dạng token không hợp lệ"}), 401
        
    user_profile = users_data.get(token)
    
    if not user_profile:
        return jsonify({"error": "Token không hợp lệ"}), 403 # Forbidden
        
    return jsonify(user_profile)

if __name__ == '__main__':
    app.run(port=5001, debug=True)