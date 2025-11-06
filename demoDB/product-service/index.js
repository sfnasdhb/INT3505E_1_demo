const config = require('./config');
const logger = require('./logger');
const ExpressServer = require('./expressServer');

require('dotenv').config();
const mongoose = require('mongoose');

const launchServer = async () => {
  try {
    // Kết nối DB trước
    await mongoose.connect(process.env.MONGODB_URI);
    console.log('[DB] Connected to MongoDB Atlas');

    // Khởi tạo và launch server (ExpressServer sẽ tự listen)
    const server = new ExpressServer(process.env.PORT || 8081, config.OPENAPI_YAML);
    server.launch();
    logger.info('Express server running');
  } catch (error) {
    logger.error('Startup failure', error.message);
    process.exit(1);
  }
};

launchServer().catch((e) => logger.error(e));
