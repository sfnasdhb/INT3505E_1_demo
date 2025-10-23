# version3_cacheable/server_cacheable.py
from flask import Flask, jsonify, request, Response
import hashlib

app = Flask(__name__)

# Giả lập dữ liệu sản phẩm không thay đổi thường xuyên
product_data = {
    "id": 101,
    "name": "Laptop Siêu Bền",
    "price": 25000000,
    "version": 1 
}

def get_data_etag(data):
    """Tạo một ETag từ dữ liệu bằng cách hash nó."""
    data_string = str(data)
    return hashlib.sha1(data_string.encode('utf-8')).hexdigest()

@app.route('/api/product/101', methods=['GET'])
def get_product():
    """Endpoint trả về thông tin sản phẩm và hỗ trợ cache."""
    print("\nSERVER: Nhận yêu cầu tới /api/product/101.")
    
    # 1. Tính toán ETag cho phiên bản dữ liệu hiện tại
    current_etag = get_data_etag(product_data)
    
    # 2. Kiểm tra header 'If-None-Match' từ client
    client_etag = request.headers.get('If-None-Match')
    
    if client_etag and client_etag == current_etag:
        # Dữ liệu của client vẫn còn mới
        print(f"SERVER: Dữ liệu không thay đổi (ETag khớp: {current_etag}). Trả về 304 Not Modified.")
        return Response(status=304)
    else:
        # Dữ liệu đã cũ hoặc client không có cache, trả về dữ liệu đầy đủ
        print(f"SERVER: Trả về dữ liệu đầy đủ với ETag mới: {current_etag}.")
        response_data = jsonify(product_data)
        
        # 3. Gắn các header cho phép cache
        response_data.headers['Cache-Control'] = 'public, max-age=60' # Cache trong 60s
        response_data.headers['ETag'] = current_etag
        
        return response_data

if __name__ == '__main__':
    app.run(port=5002, debug=True)