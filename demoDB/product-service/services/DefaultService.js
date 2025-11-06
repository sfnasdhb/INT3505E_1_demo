import Product from '../models/Product.js';

export const listProducts = async () => {
  const items = await Product.find().lean();
  return items.map(p => ({ id: String(p._id), name: p.name, price: p.price, stock: p.stock }));
};

export const createProduct = async ({ body }) => {
  const doc = await Product.create(body);
  return { id: String(doc._id), name: doc.name, price: doc.price, stock: doc.stock };
};

export const getProduct = async ({ params }) => {
  const doc = await Product.findById(params.id).lean();
  if (!doc) { const e = new Error('Not found'); e.status = 404; throw e; }
  return { id: String(doc._id), name: doc.name, price: doc.price, stock: doc.stock };
};

export const updateProduct = async ({ params, body }) => {
  const doc = await Product.findByIdAndUpdate(params.id, body, { new: true }).lean();
  if (!doc) { const e = new Error('Not found'); e.status = 404; throw e; }
  return { id: String(doc._id), name: doc.name, price: doc.price, stock: doc.stock };
};

export const deleteProduct = async ({ params }) => {
  const doc = await Product.findByIdAndDelete(params.id).lean();
  if (!doc) { const e = new Error('Not found'); e.status = 404; throw e; }
  return { message: 'Deleted' };
};
