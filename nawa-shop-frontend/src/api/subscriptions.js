import { client } from "./client.js";

export async function getSubscriptions() {
  const { data } = await client.get("/api/v1/subscriptions/");
  return data.results ?? data;
}

export async function createSubscription({ product, frequencyDays }) {
  const { data } = await client.post("/api/v1/subscriptions/", { product, frequencyDays });
  return data;
}

export async function updateSubscription(id, payload) {
  const { data } = await client.patch(`/api/v1/subscriptions/${id}/`, payload);
  return data;
}

export async function deleteSubscription(id) {
  await client.delete(`/api/v1/subscriptions/${id}/`);
}
