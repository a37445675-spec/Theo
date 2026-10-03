import { client } from "./client.js";

/** Résout le meilleur PageTemplate pour un contexte (ex. {context: "home"} ou {context: "single_product", category: "electromenager"}). */
export async function getTemplate(context, extraContext = {}) {
  const { data } = await client.get("/api/v1/cms/templates/", { params: { context, ...extraContext } });
  return data;
}

export async function getDesignSystem() {
  const { data } = await client.get("/api/v1/design-system/");
  return data;
}
