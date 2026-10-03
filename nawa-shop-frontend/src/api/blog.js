import { client } from "./client.js";

export async function getPosts(params = {}) {
  const { data } = await client.get("/api/v1/blog/posts/", { params });
  return data.results ?? data;
}

export async function getPost(slug) {
  const { data } = await client.get(`/api/v1/blog/posts/${slug}/`);
  return data;
}

export async function getBlogCategories() {
  const { data } = await client.get("/api/v1/blog/categories/");
  return data.results ?? data;
}

export async function createComment(payload) {
  const { data } = await client.post("/api/v1/blog/comments/", payload);
  return data;
}
