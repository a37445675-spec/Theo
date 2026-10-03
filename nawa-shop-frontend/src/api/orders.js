import { client } from "./client.js";

export async function getOrders() {
  const { data } = await client.get("/api/v1/orders/");
  return data.results ?? data;
}

export async function getOrder(id) {
  const { data } = await client.get(`/api/v1/orders/${id}/`);
  return data;
}
