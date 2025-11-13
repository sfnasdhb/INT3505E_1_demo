const Product = require('../models/Product');

function pickBody(args) {
  // Dùng cho mọi trường hợp body có thể là "body" hoặc "product"
  return args.product ?? args.body ?? {};
}

function notFound() {
  const e = new Error('Not found');
  e.status = 404;
  return e;
}

const listProducts = async () => {
  const items = await Product.find().lean();
  return items.map(p => ({
    id: String(p._id),
    name: p.name,
    price: p.price,
    stock: p.stock,
  }));
};

const createProduct = async (args) => {
  const data = pickBody(args);
  const doc = await Product.create(data);
  return {
    id: String(doc._id),
    name: doc.name,
    price: doc.price,
    stock: doc.stock,
  };
};

const getProduct = async ({ id }) => {
  const doc = await Product.findById(id).lean();
  if (!doc) throw notFound();
  return {
    id: String(doc._id),
    name: doc.name,
    price: doc.price,
    stock: doc.stock,
  };
};

const updateProduct = async (args) => {
  const { id } = args;
  const data = pickBody(args);
  const updated = await Product.findByIdAndUpdate(id, data, { new: true }).lean();

  if (!updated) throw notFound();

  return {
    id: String(updated._id),
    name: updated.name,
    price: updated.price,
    stock: updated.stock,
  };
};

const deleteProduct = async ({ id }) => {
  const doc = await Product.findByIdAndDelete(id).lean();
  if (!doc) throw notFound();
  return { message: 'Deleted' };
};

module.exports = {
  listProducts,
  createProduct,
  getProduct,
  updateProduct,
  deleteProduct,
};
