import { client } from "./client.js";

export async function validateCoupon(code, subtotal) {
  const { data } = await client.post("/api/v1/promotions/coupons/validate/", { code, subtotal });
  return data;
}
