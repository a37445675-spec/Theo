import { client } from "./client.js";

export async function getCategories() {
  const { data } = await client.get("/api/v1/catalog/categories/");
  return data.results ?? data;
}

export async function getCategory(slug) {
  const { data } = await client.get(`/api/v1/catalog/categories/${slug}/`);
  return data;
}

export async function getCategoryAttributes(slug) {
  const { data } = await client.get(`/api/v1/catalog/categories/${slug}/attributes/`);
  return data;
}

export async function getBrands() {
  const { data } = await client.get("/api/v1/catalog/brands/");
  return data.results ?? data;
}

/** params: { category, brand, search, ordering, priceMin, priceMax, isFeatured, page, ...attributs dynamiques } */
export async function getProducts(params = {}) {
  const { priceMin, priceMax, isFeatured, ...rest } = params;
  const query = { ...rest };
  if (priceMin !== undefined) query.price_min = priceMin;
  if (priceMax !== undefined) query.price_max = priceMax;
  if (isFeatured !== undefined) query.is_featured = isFeatured;
  const { data } = await client.get("/api/v1/catalog/products/", { params: query });
  return data;
}

export async function getProduct(slug) {
  const { data } = await client.get(`/api/v1/catalog/products/${slug}/`);
  return data;
}
