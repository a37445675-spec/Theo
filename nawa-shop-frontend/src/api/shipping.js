import { client } from "./client.js";

export async function getShippingMethods(country) {
  const { data } = await client.get("/api/v1/shipping/methods/", { params: country ? { country } : {} });
  return data.results ?? data;
}
