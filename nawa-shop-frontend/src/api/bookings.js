import { client } from "./client.js";

export async function getSlots(productId) {
  const { data } = await client.get("/api/v1/bookings/slots/", { params: { product: productId } });
  return data.results ?? data;
}

export async function bookSlot(slotId) {
  const { data } = await client.post(`/api/v1/bookings/slots/${slotId}/book/`);
  return data;
}
