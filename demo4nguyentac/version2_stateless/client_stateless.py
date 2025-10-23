# version2_stateless/client_stateless.py
import requests

BASE_URL = 'http://127.0.0.1:5001'

def fetch_profile(token=None):
    """Gọi API /profile với một token (hoặc không)."""
    headers = {}
    if token:
        headers['Authorization'] = f"Bearer {token}"
        print(f"CLIENT: Đang gọi API với token: {token}")
    else:
        print("CLIENT: Đang gọi API không có token.")
        
    try:
        response = requests.get(f"{BASE_URL}/api/profile", headers=headers)
        print(f"CLIENT: Server phản hồi với status code: {response.status_code}")
        print(f"CLIENT: Dữ liệu phản hồi: {response.json()}")
    except requests.exceptions.RequestException as e:
        print(f"CLIENT: Lỗi khi gọi API: {e}")

if __name__ == '__main__':
    print("--- Demo Nguyên tắc Stateless ---")
    
    print("\n[Lần 1]: Client gửi yêu cầu mà không có token xác thực.")
    fetch_profile()
    
    print("\n[Lần 2]: Client gửi yêu cầu với một token không hợp lệ.")
    fetch_profile(token="invalid-token-123")
    
    print("\n[Lần 3]: Client gửi yêu cầu với một token hợp lệ. Yêu cầu này chứa đủ thông tin để server xử lý.")
    fetch_profile(token="user1-token")
    
    print("\n[Lần 4]: Client khác (với token khác) gửi yêu cầu. Server vẫn xử lý được mà không bị ảnh hưởng bởi yêu cầu trước.")
    fetch_profile(token="user2-token")