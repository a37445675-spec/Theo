export function formatPrice(value, currency = "EUR") {
  const amount = typeof value === "string" ? parseFloat(value) : value;
  if (Number.isNaN(amount)) return "—";
  return new Intl.NumberFormat("fr-FR", { style: "currency", currency }).format(amount);
}

export function formatDate(value) {
  if (!value) return "";
  return new Intl.DateTimeFormat("fr-FR", { day: "numeric", month: "long", year: "numeric" }).format(new Date(value));
}

export function truncate(text, length = 140) {
  if (!text) return "";
  return text.length > length ? `${text.slice(0, length).trim()}…` : text;
}

export function attributeLabel(code) {
  const map = {
    taille: "Taille", couleur: "Couleur", matiere: "Matière", genre: "Genre",
    pointure: "Pointure", largeur_chaussure: "Largeur", matiere_chaussure: "Matière",
    puissance_w: "Puissance", voltage: "Voltage", garantie: "Garantie", classe_energetique: "Classe énergétique",
    dimensions: "Dimensions", type_peau: "Type de peau", texture_cheveux: "Texture cheveux",
    objectifs: "Objectifs", sensibilites: "Sensibilités", contenance_ml: "Contenance",
  };
  return map[code] || code;
}
