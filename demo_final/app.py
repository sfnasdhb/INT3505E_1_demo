from flask import Flask, jsonify, request
from prometheus_flask_exporter import PrometheusMetrics
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import logging
from pythonjsonlogger import jsonlogger
import time

app = Flask(__name__)

# --- 1. CẤU HÌNH LOGGING JSON (Structured Logging) ---
logHandler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter('%(asctime)s %(levelname)s %(message)s')
logHandler.setFormatter(formatter)
logger = logging.getLogger()
logger.addHandler(logHandler)
logger.setLevel(logging.INFO)

# --- 2. CẤU HÌNH METRICS (Prometheus) ---
metrics = PrometheusMetrics(app)
metrics.info('app_info', 'Application info', version='1.0.0')

# --- 3. CẤU HÌNH RATE LIMIT (Security) ---
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["10000 per hour"], # Cho phép gọi thoải mái (để Prometheus sống)
    storage_uri="memory://"
)

# --- CÁC API ---

@app.route('/')
def home():
    # Giả lập xử lý nhanh
    logger.info("Truy cập trang chủ", extra={'path': '/'})
    return jsonify({"message": "Hệ thống hoạt động bình thường"})

@app.route('/slow')
def slow():
    # Giả lập xử lý chậm (để vẽ biểu đồ latency)
    time.sleep(1) 
    logger.info("Xử lý tác vụ nặng", extra={'path': '/slow'})
    return jsonify({"message": "Xử lý xong sau 1s"})

@app.route('/spam')
@limiter.limit("5 per minute") # Chỉ cho phép 5 lần/phút
def spam():
    return jsonify({"message": "Bạn chưa bị chặn. Thử lại đi!"})

@app.errorhandler(429)
def ratelimit_handler(e):
    logger.warning("Phát hiện spam!", extra={'ip': request.remote_addr})
    return jsonify({"error": "Bạn gửi quá nhiều request! Vui lòng đợi."}), 429

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)