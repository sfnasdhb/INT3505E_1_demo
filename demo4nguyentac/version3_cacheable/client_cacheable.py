# version3_cacheable/client_cacheable.py
import requests
import time

BASE_URL = 'http://127.0.0.1:5002'
product_url = f"{BASE_URL}/api/product/101"

# Biến toàn cục để lưu cache của client
client_cache = {
    "etag": None,
    "data": None
}

def fetch_product():
    """Gọi API sản phẩm, sử dụng ETag nếu có trong cache."""
    headers = {}
    if client_cache["etag"]:
        headers['If-None-Match'] = client_cache["etag"]
        print(f"CLIENT: Đã có cache. Gửi yêu cầu với ETag: {client_cache['etag']}")
    else:
        print("CLIENT: Chưa có cache. Gửi yêu cầu thông thường.")

    try:
        response = requests.get(product_url, headers=headers)
        print(f"CLIENT: Server phản hồi với status code: {response.status_code}")

        if response.status_code == 200: # OK - Nhận dữ liệu mới
            print("CLIENT: Nhận được dữ liệu mới từ server.")
            client_cache["data"] = response.json()
            client_cache["etag"] = response.headers.get('ETag')
            print(f"CLIENT: Đã lưu dữ liệu vào cache. ETag mới: {client_cache['etag']}")
            print("Dữ liệu:", client_cache["data"])
        elif response.status_code == 304: # Not Modified
            print("CLIENT: Dữ liệu trong cache vẫn còn hợp lệ. Sử dụng dữ liệu cũ.")
            print("Dữ liệu từ cache:", client_cache["data"])
        else:
            print(f"CLIENT: Lỗi: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"CLIENT: Lỗi khi gọi API: {e}")

if __name__ == '__main__':
    print("--- Demo Nguyên tắc Cacheable ---")
    
    print("\n[Lần 1]: Client yêu cầu dữ liệu lần đầu tiên.")
    fetch_product()
    
    print("\n-------------------------------------------")
    print("[Lần 2]: Client yêu cầu lại cùng tài nguyên ngay sau đó.")
    fetch_product()