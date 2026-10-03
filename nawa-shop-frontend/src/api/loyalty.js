import { client } from "./client.js";

export async function getMyLoyalty() {
  const { data } = await client.get("/api/v1/loyalty/mine/");
  return data;
}
