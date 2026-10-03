import { client, clearTokens, setTokens } from "./client.js";

export async function login(username, password) {
  const { data } = await client.post("/api/v1/auth/token/", { username, password });
  setTokens({ access: data.access, refresh: data.refresh });
  return fetchMe();
}

export async function register(payload) {
  await client.post("/api/v1/auth/register/", payload);
  return login(payload.username, payload.password);
}

export async function fetchMe() {
  const { data } = await client.get("/api/v1/auth/me/");
  return data;
}

export async function updateMe(payload) {
  const { data } = await client.patch("/api/v1/auth/me/", payload);
  return data;
}

export function logout() {
  clearTokens();
}

export async function getAddresses() {
  const { data } = await client.get("/api/v1/auth/addresses/");
  return data.results ?? data;
}

export async function createAddress(payload) {
  const { data } = await client.post("/api/v1/auth/addresses/", payload);
  return data;
}

export async function updateAddress(id, payload) {
  const { data } = await client.patch(`/api/v1/auth/addresses/${id}/`, payload);
  return data;
}

export async function deleteAddress(id) {
  await client.delete(`/api/v1/auth/addresses/${id}/`);
}
