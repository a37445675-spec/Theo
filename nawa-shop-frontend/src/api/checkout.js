import { client } from "./client.js";

export async function checkout({ shippingAddress, billingAddress, guestEmail, couponCode }) {
  const { data } = await client.post("/api/v1/checkout/", { shippingAddress, billingAddress, guestEmail, couponCode });
  return data;
}
