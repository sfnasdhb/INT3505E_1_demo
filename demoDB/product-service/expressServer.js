// expressServer.js
const http = require('http');
const fs = require('fs');
const path = require('path');
const swaggerUI = require('swagger-ui-express');
const jsYaml = require('js-yaml'); // dùng .load
const express = require('express');
const cors = require('cors');
const cookieParser = require('cookie-parser');
// const bodyParser = require('body-parser'); // ❌ không cần nếu đã dùng express.json()
const OpenApiValidator = require('express-openapi-validator');
const logger = require('./logger');
const config = require('./config');

class ExpressServer {
  constructor(port, openApiYaml) {
    this.port = port || 8081;
    this.app = express();
    this.openApiPath = openApiYaml;

    try {
      // ✅ dùng jsYaml.load
      this.schema = jsYaml.load(fs.readFileSync(this.openApiPath, 'utf8'));
    } catch (e) {
      logger.error('Failed to load OpenAPI spec', e.message);
    }

    // đảm bảo thư mục upload tồn tại nếu có cấu hình
    if (config.FILE_UPLOAD_PATH) {
      fs.mkdirSync(config.FILE_UPLOAD_PATH, { recursive: true });
    }

    this.setupMiddleware();
  }

  setupMiddleware() {
    this.app.use(cors());
    this.app.use(express.json({ limit: '14mb' }));      // ✅ đủ dùng
    this.app.use(express.urlencoded({ extended: false }));
    this.app.use(cookieParser());

    // Healthcheck đơn giản
    this.app.get('/health', (req, res) => res.status(200).send('OK'));

    // Simple test
    this.app.get('/hello', (req, res) => res.send(`Hello World. path: ${this.openApiPath}`));

    // Serve OpenAPI yaml (bản bạn đang dùng)
    this.app.get('/openapi', (req, res) => res.sendFile(path.resolve(this.openApiPath)));

    // Swagger UI
    this.app.use('/api-docs', swaggerUI.serve, swaggerUI.setup(this.schema));

    // OIDC demo redirect (nếu cần cho Swagger OAuth2)
    this.app.get('/login-redirect', (req, res) => res.status(200).json(req.query));
    this.app.get('/oauth2-redirect.html', (req, res) => res.status(200).json(req.query));

    // OpenAPI Validator
    this.app.use(
      OpenApiValidator.middleware({
        apiSpec: this.openApiPath,
        operationHandlers: path.join(__dirname), // map tới thư mục có controllers/
        fileUploader: config.FILE_UPLOAD_PATH ? { dest: config.FILE_UPLOAD_PATH } : undefined,
        // (tùy chọn) validateResponses: true,
      }),
    );
  }

  launch() {
    // ================== BẮT ĐẦU THAY THẾ TỪ ĐÂY ==================
    // Error handler - PHIÊN BẢN CẢI TIẾN
    // eslint-disable-next-line no-unused-vars
    this.app.use((err, req, res, next) => {
      // Lấy status code từ đối tượng lỗi, nếu không có thì mặc định là 500
      const statusCode = err.status || 500;
      // Lấy message từ đối tượng lỗi, nếu không có thì đặt một message mặc định
      const message = err.message || 'Internal Server Error';

      // Dòng này rất quan trọng để gỡ lỗi, nó sẽ in lỗi đầy đủ ra console
      console.error('[Error Handler] Caught an error:', err);

      // Trả về response lỗi
      res.status(statusCode).json({
        message: message,
        errors: err.errors || [], // Dùng mảng rỗng thay vì chuỗi rỗng cho an toàn
      });
    });
    // ================== KẾT THÚC THAY THẾ TẠI ĐÂY ==================

    // ✅ lưu handle server để close() được
    this.server = http.createServer(this.app).listen(this.port, () => {
      console.log(`Listening on port ${this.port}`);
    });
  }

  async close() {
    if (this.server) {
      await new Promise((resolve, reject) =>
        this.server.close((err) => (err ? reject(err) : resolve())),
      );
      console.log(`Server on port ${this.port} shut down`);
    }
  }
}

module.exports = ExpressServer;
