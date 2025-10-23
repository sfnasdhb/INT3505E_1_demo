# version1_client_server/client.py
import requests
import json

BASE_URL = 'http://127.0.0.1:5000'

def get_all_tasks():
    """Gửi yêu cầu GET để lấy danh sách công việc."""
    try:
        response = requests.get(f"{BASE_URL}/api/tasks")
        response.raise_for_status() 
        print("CLIENT: Lấy danh sách công việc thành công!")
        tasks = response.json()['tasks']
        print(json.dumps(tasks, indent=2, ensure_ascii=False))
    except requests.exceptions.RequestException as e:
        print(f"CLIENT: Lỗi khi gọi API: {e}")

def add_new_task(title):
    """Gửi yêu cầu POST để thêm công việc mới."""
    try:
        headers = {'Content-Type': 'application/json'}
        payload = {'title': title}
        response = requests.post(f"{BASE_URL}/api/tasks", headers=headers, json=payload)
        response.raise_for_status()
        print(f"\nCLIENT: Thêm công việc '{title}' thành công!")
        new_task = response.json()['task']
        print(json.dumps(new_task, indent=2, ensure_ascii=False))
    except requests.exceptions.RequestException as e:
        print(f"CLIENT: Lỗi khi tạo công việc mới: {e}")

if __name__ == '__main__':
    print("--- Demo Nguyên tắc Client-Server ---")
    print("1. Client yêu cầu danh sách công việc từ Server:")
    get_all_tasks()
    
    print("\n2. Client yêu cầu Server tạo một công việc mới:")
    add_new_task("Trình bày kết quả demo")
    
    print("\n3. Client yêu cầu lại danh sách để xác nhận công việc đã được thêm:")
    get_all_tasks()