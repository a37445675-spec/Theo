import { client } from "./client.js";

export async function getInvoices() {
  const { data } = await client.get("/api/v1/billing/invoices/");
  return data.results ?? data;
}
