const Controller = require('./Controller');
const service = require('../services/DefaultService');

const listProducts = async (req, res) => {
  await Controller.handleRequest(req, res, service.listProducts);
};

const getProduct = async (req, res) => {
  await Controller.handleRequest(req, res, service.getProduct);
};

const createProduct = async (req, res) => {
  await Controller.handleRequest(req, res, service.createProduct);
};

const updateProduct = async (req, res) => {
  await Controller.handleRequest(req, res, service.updateProduct);
};

const deleteProduct = async (req, res) => {
  await Controller.handleRequest(req, res, service.deleteProduct);
};

module.exports = {
  listProducts,
  getProduct,
  createProduct,
  updateProduct,
  deleteProduct,
};
