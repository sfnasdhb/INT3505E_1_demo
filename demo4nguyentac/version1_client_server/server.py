# version1_client_server/server.py
from flask import Flask, jsonify, request

app = Flask(__name__)

tasks = [
    {"id": 1, "title": "Học về REST API", "done": True},
    {"id": 2, "title": "Xây dựng demo Flask", "done": False}
]
next_task_id = 3

@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    """Endpoint để lấy danh sách tất cả công việc."""
    return jsonify({'tasks': tasks})

@app.route('/api/tasks', methods=['POST'])
def create_task():
    """Endpoint để tạo một công việc mới."""
    global next_task_id
    if not request.json or 'title' not in request.json:
        return jsonify({'error': 'Dữ liệu không hợp lệ'}), 400
    
    new_task = {
        'id': next_task_id,
        'title': request.json['title'],
        'done': False
    }
    tasks.append(new_task)
    next_task_id += 1
    return jsonify({'task': new_task}), 201

if __name__ == '__main__':
    # Chạy server trên cổng 5000
    app.run(port=5000, debug=True)