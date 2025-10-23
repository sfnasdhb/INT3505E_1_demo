# version4_uniform/client_uniform.py
import requests
import json

BASE_URL = 'http://127.0.0.1:5003'

def discover_api():
    """Client khám phá API bắt đầu từ endpoint books."""
    try:
        response = requests.get(f"{BASE_URL}/api/books")
        response.raise_for_status()
        
        books_collection = response.json()
        print(json.dumps(books_collection, indent=2, ensure_ascii=False))
        
        first_book = books_collection['books'][0]
        self_link = first_book['_links']['self']['href']
                
        book_response = requests.get(self_link)
        book_response.raise_for_status()
        
        detailed_book = book_response.json()
        print("CLIENT: Nhận được chi tiết sách:")
        print(json.dumps(detailed_book, indent=2, ensure_ascii=False))

    except requests.exceptions.RequestException as e:
        print(f"CLIENT: Lỗi khi khám phá API: {e}")

if __name__ == '__main__':
    print("--- Demo Nguyên tắc Uniform Interface ---")
    discover_api()