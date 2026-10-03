"""
Injection du Widget Builder - Frontend React.
Installe Puck et crée la config + l'éditeur + le renderer.

Usage : python inject_widget_builder_frontend.py
"""
import os
import shutil
import subprocess

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(BASE_DIR, "src")


# ============================================================
#                  PUCK CONFIG (25 widgets)
# ============================================================

PUCK_CONFIG = '''/**
 * Configuration Puck - Widgets NAWA
 * Bibliothèque de composants éditables.
 */
import React from "react";

// ============================================================
//  STRUCTURE
// ============================================================

const Section = {
  fields: {
    background: { type: "text", label: "Couleur de fond" },
    padding: { type: "text", label: "Padding", defaultValue: "60px 0" },
    maxWidth: { type: "text", label: "Largeur max", defaultValue: "1200px" },
  },
  defaultProps: { background: "transparent", padding: "60px 0", maxWidth: "1200px" },
  render: ({ background, padding, maxWidth, puck }) => (
    <section style={{ background, padding }}>
      <div style={{ maxWidth, margin: "0 auto", padding: "0 1rem" }}>
        {puck.renderDropZone()}
      </div>
    </section>
  ),
};

const Columns = {
  fields: {
    layout: {
      type: "select",
      label: "Disposition",
      options: [
        { label: "2 colonnes", value: "2" },
        { label: "3 colonnes", value: "3" },
        { label: "4 colonnes", value: "4" },
        { label: "1/3 + 2/3", value: "1-2" },
        { label: "2/3 + 1/3", value: "2-1" },
      ],
    },
    gap: { type: "text", label: "Espacement", defaultValue: "24px" },
  },
  defaultProps: { layout: "2", gap: "24px" },
  render: ({ layout, gap, puck }) => {
    const cols = layout.includes("-") ? layout.split("-").length : parseInt(layout);
    const template = layout.includes("-")
      ? layout.split("-").map((n) => `${n}fr`).join(" ")
      : `repeat(${cols}, 1fr)`;
    return (
      <div style={{ display: "grid", gridTemplateColumns: template, gap }}>
        {Array.from({ length: cols }).map((_, i) => (
          <div key={i}>{puck.renderDropZone({ zone: `col-${i}` })}</div>
        ))}
      </div>
    );
  },
};

// ============================================================
//  BASIQUES
// ============================================================

const Heading = {
  fields: {
    text: { type: "text", label: "Texte" },
    level: {
      type: "select", label: "Niveau",
      options: [
        { label: "H1", value: "h1" }, { label: "H2", value: "h2" },
        { label: "H3", value: "h3" }, { label: "H4", value: "h4" },
      ],
    },
    align: {
      type: "radio", label: "Alignement",
      options: [
        { label: "Gauche", value: "left" },
        { label: "Centre", value: "center" },
        { label: "Droite", value: "right" },
      ],
    },
  },
  defaultProps: { text: "Mon titre", level: "h2", align: "left" },
  render: ({ text, level, align }) => {
    const Tag = level;
    return <Tag style={{ textAlign: align }}>{text}</Tag>;
  },
};

const Text = {
  fields: {
    text: { type: "textarea", label: "Texte" },
    align: {
      type: "radio", label: "Alignement",
      options: [
        { label: "Gauche", value: "left" },
        { label: "Centre", value: "center" },
      ],
    },
  },
  defaultProps: { text: "Votre paragraphe ici...", align: "left" },
  render: ({ text, align }) => <p style={{ textAlign: align }}>{text}</p>,
};

const Image = {
  fields: {
    src: { type: "text", label: "URL de l'image" },
    alt: { type: "text", label: "Texte alternatif" },
    ratio: {
      type: "select", label: "Ratio",
      options: [
        { label: "Libre", value: "auto" },
        { label: "Carré", value: "1/1" },
        { label: "Paysage", value: "16/9" },
        { label: "Portrait", value: "4/5" },
      ],
    },
    radius: { type: "text", label: "Arrondi", defaultValue: "12px" },
  },
  defaultProps: { src: "/fallbacks/product-fallback.jpg", alt: "", ratio: "auto", radius: "12px" },
  render: ({ src, alt, ratio, radius }) => (
    <img
      src={src}
      alt={alt}
      style={{ width: "100%", aspectRatio: ratio === "auto" ? undefined : ratio, objectFit: "cover", borderRadius: radius }}
    />
  ),
};

const Button = {
  fields: {
    label: { type: "text", label: "Libellé" },
    url: { type: "text", label: "Lien" },
    variant: {
      type: "radio", label: "Style",
      options: [
        { label: "Primaire", value: "primary" },
        { label: "Ghost", value: "ghost" },
      ],
    },
  },
  defaultProps: { label: "Cliquez ici", url: "#", variant: "primary" },
  render: ({ label, url, variant }) => (
    <a href={url} className={`btn btn-${variant}`}>{label}</a>
  ),
};

const Divider = {
  fields: {
    color: { type: "text", label: "Couleur", defaultValue: "#e5e5e5" },
    thickness: { type: "text", label: "Épaisseur", defaultValue: "1px" },
    margin: { type: "text", label: "Marge", defaultValue: "24px 0" },
  },
  defaultProps: { color: "#e5e5e5", thickness: "1px", margin: "24px 0" },
  render: ({ color, thickness, margin }) => (
    <hr style={{ border: "none", borderTop: `${thickness} solid ${color}`, margin }} />
  ),
};

const Spacer = {
  fields: {
    height: { type: "text", label: "Hauteur", defaultValue: "40px" },
  },
  defaultProps: { height: "40px" },
  render: ({ height }) => <div style={{ height }} />,
};

const IconBox = {
  fields: {
    icon: { type: "text", label: "Emoji / Icône" },
    title: { type: "text", label: "Titre" },
    description: { type: "textarea", label: "Description" },
  },
  defaultProps: { icon: "✨", title: "Titre", description: "Description du bloc icône." },
  render: ({ icon, title, description }) => (
    <div style={{ textAlign: "center", padding: "24px" }}>
      <div style={{ fontSize: "42px", marginBottom: "12px" }}>{icon}</div>
      <h3 style={{ marginBottom: "8px" }}>{title}</h3>
      <p style={{ color: "#6B6259" }}>{description}</p>
    </div>
  ),
};

// ============================================================
//  MARKETING
// ============================================================

const CTA = {
  fields: {
    title: { type: "text", label: "Titre" },
    subtitle: { type: "text", label: "Sous-titre" },
    buttonLabel: { type: "text", label: "Bouton" },
    buttonUrl: { type: "text", label: "Lien" },
    background: { type: "text", label: "Couleur de fond", defaultValue: "#C1652F" },
    textColor: { type: "text", label: "Couleur du texte", defaultValue: "#FFFFFF" },
  },
  defaultProps: {
    title: "Prêt à découvrir ?",
    subtitle: "Rejoignez NAWA dès aujourd'hui.",
    buttonLabel: "Commencer",
    buttonUrl: "/boutique",
    background: "#C1652F",
    textColor: "#FFFFFF",
  },
  render: ({ title, subtitle, buttonLabel, buttonUrl, background, textColor }) => (
    <div style={{ background, color: textColor, padding: "60px 40px", borderRadius: "24px", textAlign: "center" }}>
      <h2 style={{ marginBottom: "12px", color: textColor }}>{title}</h2>
      <p style={{ marginBottom: "24px", opacity: 0.9 }}>{subtitle}</p>
      <a href={buttonUrl} className="btn btn-lg" style={{ background: textColor, color: background }}>
        {buttonLabel}
      </a>
    </div>
  ),
};

const Testimonial = {
  fields: {
    quote: { type: "textarea", label: "Citation" },
    author: { type: "text", label: "Auteur" },
    role: { type: "text", label: "Rôle" },
    avatar: { type: "text", label: "URL Avatar" },
  },
  defaultProps: {
    quote: "Un service exceptionnel et des produits de qualité !",
    author: "Fatou D.", role: "Cliente fidèle", avatar: "",
  },
  render: ({ quote, author, role, avatar }) => (
    <div style={{ padding: "32px", background: "#fff", borderRadius: "16px", boxShadow: "0 4px 12px rgba(0,0,0,0.06)" }}>
      <p style={{ fontStyle: "italic", marginBottom: "16px" }}>"{quote}"</p>
      <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
        {avatar && <img src={avatar} alt={author} style={{ width: "40px", height: "40px", borderRadius: "50%" }} />}
        <div>
          <div style={{ fontWeight: 600 }}>{author}</div>
          <div style={{ fontSize: "0.85rem", color: "#6B6259" }}>{role}</div>
        </div>
      </div>
    </div>
  ),
};

const PricingTable = {
  fields: {
    title: { type: "text", label: "Titre" },
    price: { type: "text", label: "Prix" },
    period: { type: "text", label: "Période" },
    features: { type: "textarea", label: "Caractéristiques (1 par ligne)" },
    ctaLabel: { type: "text", label: "Bouton" },
    ctaUrl: { type: "text", label: "Lien" },
    highlighted: { type: "radio", label: "Mis en avant", options: [{ label: "Oui", value: true }, { label: "Non", value: false }] },
  },
  defaultProps: {
    title: "Premium", price: "29€", period: "/mois",
    features: "Livraison offerte\\nSupport prioritaire\\n-10% permanent",
    ctaLabel: "Choisir", ctaUrl: "#", highlighted: false,
  },
  render: ({ title, price, period, features, ctaLabel, ctaUrl, highlighted }) => (
    <div style={{
      padding: "32px", background: highlighted ? "#2F4A3C" : "#fff",
      color: highlighted ? "#F7F0E4" : "#221B15",
      borderRadius: "16px", boxShadow: "0 4px 12px rgba(0,0,0,0.08)",
      transform: highlighted ? "scale(1.05)" : "none",
    }}>
      <h3>{title}</h3>
      <div style={{ fontSize: "2.5rem", fontWeight: 700, margin: "12px 0" }}>
        {price}<span style={{ fontSize: "1rem", fontWeight: 400 }}>{period}</span>
      </div>
      <ul style={{ listStyle: "none", padding: 0, margin: "16px 0" }}>
        {features.split("\\n").map((f, i) => <li key={i} style={{ padding: "4px 0" }}>✓ {f}</li>)}
      </ul>
      <a href={ctaUrl} className="btn btn-primary" style={{ width: "100%", display: "block", textAlign: "center" }}>
        {ctaLabel}
      </a>
    </div>
  ),
};

const Countdown = {
  fields: {
    targetDate: { type: "text", label: "Date cible (ISO)" },
    label: { type: "text", label: "Libellé" },
    background: { type: "text", label: "Fond", defaultValue: "#221B15" },
    textColor: { type: "text", label: "Texte", defaultValue: "#D4A843" },
  },
  defaultProps: {
    targetDate: new Date(Date.now() + 7 * 24 * 3600 * 1000).toISOString(),
    label: "Offre limitée !", background: "#221B15", textColor: "#D4A843",
  },
  render: ({ targetDate, label, background, textColor }) => {
    const [time, setTime] = React.useState(calc(targetDate));
    React.useEffect(() => {
      const i = setInterval(() => setTime(calc(targetDate)), 1000);
      return () => clearInterval(i);
    }, [targetDate]);
    return (
      <div style={{ background, color: textColor, padding: "32px", borderRadius: "16px", textAlign: "center" }}>
        <div style={{ marginBottom: "12px", fontWeight: 600 }}>{label}</div>
        <div style={{ display: "flex", gap: "16px", justifyContent: "center" }}>
          {[["J", time.d], ["H", time.h], ["M", time.m], ["S", time.s]].map(([u, v]) => (
            <div key={u}><div style={{ fontSize: "2rem", fontWeight: 700 }}>{String(v).padStart(2, "0")}</div><div style={{ fontSize: "0.75rem" }}>{u}</div></div>
          ))}
        </div>
      </div>
    );
  },
};

function calc(target) {
  const diff = Math.max(0, new Date(target) - new Date());
  return {
    d: Math.floor(diff / 86400000),
    h: Math.floor((diff % 86400000) / 3600000),
    m: Math.floor((diff % 3600000) / 60000),
    s: Math.floor((diff % 60000) / 1000),
  };
}

const ProgressBar = {
  fields: {
    label: { type: "text", label: "Libellé" },
    value: { type: "number", label: "Valeur (0-100)" },
    color: { type: "text", label: "Couleur", defaultValue: "#C1652F" },
  },
  defaultProps: { label: "Satisfaction client", value: 92, color: "#C1652F" },
  render: ({ label, value, color }) => (
    <div>
      <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "6px" }}>
        <span>{label}</span><span style={{ fontWeight: 600 }}>{value}%</span>
      </div>
      <div style={{ background: "#eee", height: "8px", borderRadius: "999px", overflow: "hidden" }}>
        <div style={{ background: color, width: `${value}%`, height: "100%" }} />
      </div>
    </div>
  ),
};

const FlipBox = {
  fields: {
    frontTitle: { type: "text", label: "Titre face avant" },
    frontColor: { type: "text", label: "Fond avant", defaultValue: "#C1652F" },
    backTitle: { type: "text", label: "Titre face arrière" },
    backText: { type: "textarea", label: "Texte face arrière" },
    backColor: { type: "text", label: "Fond arrière", defaultValue: "#2F4A3C" },
  },
  defaultProps: {
    frontTitle: "Survolez-moi", frontColor: "#C1652F",
    backTitle: "Découvrez", backText: "Une surprise vous attend !", backColor: "#2F4A3C",
  },
  render: ({ frontTitle, frontColor, backTitle, backText, backColor }) => {
    const [flipped, setFlipped] = React.useState(false);
    return (
      <div
        onMouseEnter={() => setFlipped(true)}
        onMouseLeave={() => setFlipped(false)}
        style={{ perspective: "1000px", height: "220px", cursor: "pointer" }}
      >
        <div style={{
          position: "relative", width: "100%", height: "100%",
          transformStyle: "preserve-3d", transition: "transform 0.6s",
          transform: flipped ? "rotateY(180deg)" : "none",
        }}>
          <div style={{
            position: "absolute", inset: 0, backfaceVisibility: "hidden",
            background: frontColor, color: "#fff", borderRadius: "16px",
            display: "flex", alignItems: "center", justifyContent: "center", fontSize: "1.5rem", fontWeight: 600,
          }}>{frontTitle}</div>
          <div style={{
            position: "absolute", inset: 0, backfaceVisibility: "hidden",
            background: backColor, color: "#fff", borderRadius: "16px",
            display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center",
            padding: "24px", transform: "rotateY(180deg)", textAlign: "center",
          }}>
            <h3 style={{ color: "#fff" }}>{backTitle}</h3>
            <p>{backText}</p>
          </div>
        </div>
      </div>
    );
  },
};

const Accordion = {
  fields: {
    items: { type: "textarea", label: "Éléments (titre|contenu, un par ligne)" },
  },
  defaultProps: { items: "Question 1|Réponse 1\\nQuestion 2|Réponse 2\\nQuestion 3|Réponse 3" },
  render: ({ items }) => {
    const [open, setOpen] = React.useState(0);
    const list = items.split("\\n").map((l) => l.split("|"));
    return (
      <div>
        {list.map(([q, a], i) => (
          <div key={i} style={{ borderBottom: "1px solid #eee" }}>
            <button
              onClick={() => setOpen(open === i ? -1 : i)}
              style={{ width: "100%", textAlign: "left", padding: "16px 0", background: "none", border: "none", cursor: "pointer", fontWeight: 600, fontSize: "1rem" }}
            >
              {open === i ? "−" : "+"} {q}
            </button>
            {open === i && <div style={{ padding: "0 0 16px", color: "#6B6259" }}>{a}</div>}
          </div>
        ))}
      </div>
    );
  },
};

const Tabs = {
  fields: {
    tabs: { type: "textarea", label: "Onglets (titre|contenu, un par ligne)" },
  },
  defaultProps: { tabs: "Description|Contenu de la description\\nLivraison|Info livraison\\nRetours|Info retours" },
  render: ({ tabs }) => {
    const [active, setActive] = React.useState(0);
    const list = tabs.split("\\n").map((l) => l.split("|"));
    return (
      <div>
        <div style={{ display: "flex", gap: "8px", borderBottom: "1px solid #eee", marginBottom: "16px" }}>
          {list.map(([t], i) => (
            <button
              key={i}
              onClick={() => setActive(i)}
              style={{
                padding: "12px 20px", background: "none", border: "none",
                cursor: "pointer", fontWeight: active === i ? 600 : 400,
                borderBottom: active === i ? "2px solid #C1652F" : "2px solid transparent",
                color: active === i ? "#C1652F" : "#6B6259",
              }}
            >
              {t}
            </button>
          ))}
        </div>
        <div>{list[active][1]}</div>
      </div>
    );
  },
};

const Gallery = {
  fields: {
    images: { type: "textarea", label: "URLs (1 par ligne)" },
    columns: { type: "number", label: "Colonnes", defaultValue: 3 },
    gap: { type: "text", label: "Espacement", defaultValue: "12px" },
  },
  defaultProps: {
    images: "/fallbacks/product-fallback.jpg\\n/fallbacks/blog-fallback.jpg\\n/fallbacks/hero-fallback.jpg",
    columns: 3, gap: "12px",
  },
  render: ({ images, columns, gap }) => (
    <div style={{ display: "grid", gridTemplateColumns: `repeat(${columns}, 1fr)`, gap }}>
      {images.split("\\n").map((url, i) => (
        <img key={i} src={url} alt="" style={{ width: "100%", aspectRatio: "1/1", objectFit: "cover", borderRadius: "8px" }} />
      ))}
    </div>
  ),
};

const Carousel = {
  fields: {
    images: { type: "textarea", label: "URLs (1 par ligne)" },
    height: { type: "text", label: "Hauteur", defaultValue: "300px" },
    autoPlay: { type: "radio", label: "Auto", options: [{ label: "Oui", value: true }, { label: "Non", value: false }] },
  },
  defaultProps: {
    images: "/fallbacks/hero-fallback.jpg\\n/fallbacks/blog-fallback.jpg\\n/fallbacks/product-fallback.jpg",
    height: "300px", autoPlay: true,
  },
  render: ({ images, height, autoPlay }) => {
    const list = images.split("\\n").filter(Boolean);
    const [i, setI] = React.useState(0);
    React.useEffect(() => {
      if (!autoPlay) return;
      const id = setInterval(() => setI((v) => (v + 1) % list.length), 3500);
      return () => clearInterval(id);
    }, [autoPlay, list.length]);
    if (!list.length) return null;
    return (
      <div style={{ position: "relative", height, overflow: "hidden", borderRadius: "16px" }}>
        <img src={list[i]} alt="" style={{ width: "100%", height: "100%", objectFit: "cover", transition: "opacity 0.4s" }} />
        <button onClick={() => setI((v) => (v - 1 + list.length) % list.length)}
          style={{ position: "absolute", top: "50%", left: 12, transform: "translateY(-50%)", background: "rgba(0,0,0,0.5)", color: "#fff", border: "none", borderRadius: "50%", width: 40, height: 40, cursor: "pointer" }}>‹</button>
        <button onClick={() => setI((v) => (v + 1) % list.length)}
          style={{ position: "absolute", top: "50%", right: 12, transform: "translateY(-50%)", background: "rgba(0,0,0,0.5)", color: "#fff", border: "none", borderRadius: "50%", width: 40, height: 40, cursor: "pointer" }}>›</button>
      </div>
    );
  },
};

const Video = {
  fields: {
    url: { type: "text", label: "URL (YouTube / Vimeo / MP4)" },
    ratio: { type: "text", label: "Ratio", defaultValue: "16/9" },
  },
  defaultProps: { url: "", ratio: "16/9" },
  render: ({ url, ratio }) => {
    if (!url) return <div style={{ aspectRatio: ratio, background: "#eee", borderRadius: "12px" }} />;
    let embed = url;
    if (url.includes("youtube.com/watch?v=")) embed = url.replace("watch?v=", "embed/");
    if (url.includes("youtu.be/")) embed = `https://www.youtube.com/embed/${url.split("youtu.be/")[1]}`;
    if (url.includes("vimeo.com/")) embed = `https://player.vimeo.com/video/${url.split("vimeo.com/")[1]}`;
    return (
      <iframe
        src={embed} title="Vidéo" allowFullScreen
        style={{ width: "100%", aspectRatio: ratio, border: "none", borderRadius: "12px" }}
      />
    );
  },
};

const SocialShare = {
  fields: {
    title: { type: "text", label: "Titre", defaultValue: "Partager" },
    url: { type: "text", label: "URL à partager", defaultValue: "" },
  },
  defaultProps: { title: "Partager", url: "" },
  render: ({ title, url }) => {
    const shareUrl = url || (typeof window !== "undefined" ? window.location.href : "");
    const encoded = encodeURIComponent(shareUrl);
    const links = [
      { name: "Facebook", href: `https://www.facebook.com/sharer/sharer.php?u=${encoded}`, emoji: "📘" },
      { name: "Twitter", href: `https://twitter.com/intent/tweet?url=${encoded}`, emoji: "🐦" },
      { name: "WhatsApp", href: `https://wa.me/?text=${encoded}`, emoji: "💬" },
      { name: "LinkedIn", href: `https://www.linkedin.com/sharing/share-offsite/?url=${encoded}`, emoji: "💼" },
    ];
    return (
      <div>
        <div style={{ fontWeight: 600, marginBottom: "12px" }}>{title}</div>
        <div style={{ display: "flex", gap: "8px" }}>
          {links.map((l) => (
            <a key={l.name} href={l.href} target="_blank" rel="noopener noreferrer" title={l.name}
              style={{ width: 40, height: 40, display: "flex", alignItems: "center", justifyContent: "center", background: "#fff", borderRadius: "50%", boxShadow: "0 2px 8px rgba(0,0,0,0.1)", textDecoration: "none", fontSize: "1.2rem" }}>
              {l.emoji}
            </a>
          ))}
        </div>
      </div>
    );
  },
};

const ProductGrid = {
  fields: {
    source: {
      type: "select", label: "Source",
      options: [
        { label: "Mis en avant", value: "featured" },
        { label: "Nouveautés", value: "new_products" },
        { label: "Promotions", value: "on_sale" },
      ],
    },
    columns: { type: "number", label: "Colonnes", defaultValue: 4 },
    limit: { type: "number", label: "Nombre de produits", defaultValue: 4 },
  },
  defaultProps: { source: "featured", columns: 4, limit: 4 },
  render: ({ source, columns, limit }) => (
    <div style={{ padding: "20px", background: "#f9f9f9", borderRadius: "12px", textAlign: "center", color: "#6B6259" }}>
      <div style={{ fontSize: "1.5rem", marginBottom: "8px" }}>🛍</div>
      <div><strong>Grille produits</strong> — source : {source} · {columns} col · {limit} produits</div>
    </div>
  ),
};

const BlogList = {
  fields: {
    limit: { type: "number", label: "Nombre d'articles", defaultValue: 3 },
    columns: { type: "number", label: "Colonnes", defaultValue: 3 },
  },
  defaultProps: { limit: 3, columns: 3 },
  render: ({ limit, columns }) => (
    <div style={{ padding: "20px", background: "#f9f9f9", borderRadius: "12px", textAlign: "center", color: "#6B6259" }}>
      <div style={{ fontSize: "1.5rem", marginBottom: "8px" }}>📰</div>
      <div><strong>Liste articles</strong> — {limit} articles · {columns} col</div>
    </div>
  ),
};

// ============================================================
//  EXPORT
// ============================================================

export const puckConfig = {
  components: {
    Section,
    Columns,
    Heading,
    Text,
    Image,
    Button,
    Divider,
    Spacer,
    IconBox,
    CTA,
    Testimonial,
    PricingTable,
    Countdown,
    ProgressBar,
    FlipBox,
    Accordion,
    Tabs,
    Gallery,
    Carousel,
    Video,
    SocialShare,
    ProductGrid,
    BlogList,
  },
  categories: {
    structure: { components: ["Section", "Columns", "Divider", "Spacer"], title: "Structure" },
    basics: { components: ["Heading", "Text", "Image", "Button", "IconBox"], title: "Basiques" },
    marketing: { components: ["CTA", "Testimonial", "PricingTable", "Countdown", "ProgressBar"], title: "Marketing" },
    media: { components: ["Gallery", "Carousel", "Video"], title: "Média" },
    interactive: { components: ["Accordion", "Tabs", "FlipBox", "SocialShare"], title: "Interactif" },
    commerce: { components: ["ProductGrid", "BlogList"], title: "Boutique" },
  },
};
'''


# ============================================================
#              PAGE BUILDER COMPONENT
# ============================================================

PAGE_BUILDER = '''import { Puck } from "@measured/puck";
import "@measured/puck/puck.css";
import { useEffect, useState } from "react";
import { puckConfig } from "../puck/config";
import { api } from "../utils/api";

/**
 * Éditeur visuel drag-and-drop.
 * Route : /admin/pages/:pageId/builder
 */
export default function PageBuilder({ pageId }) {
  const [data, setData] = useState({ content: [], root: { props: {} } });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get(`/cms/widgets/?page=${pageId}`)
      .then((res) => {
        const widgets = Array.isArray(res) ? res : res.results || [];
        setData({
          content: widgets.map(widgetToPuck),
          root: { props: {} },
        });
      })
      .catch(() => setData({ content: [], root: { props: {} } }))
      .finally(() => setLoading(false));
  }, [pageId]);

  const handlePublish = async (newData) => {
    try {
      await api.post("/cms/widgets/save-tree/", {
        page: pageId,
        tree: newData.content.map(puckToWidget),
      });
      alert("✅ Page sauvegardée avec succès !");
    } catch (err) {
      alert("❌ Erreur de sauvegarde : " + err.message);
    }
  };

  if (loading) return <div style={{ padding: "2rem" }}>Chargement de l'éditeur...</div>;

  return (
    <Puck
      config={puckConfig}
      data={data}
      onPublish={handlePublish}
      onChange={setData}
    />
  );
}


// ============================================================
//  Conversions API <-> Puck
// ============================================================

function widgetToPuck(w) {
  return {
    type: w.widget_type || w.type,
    props: {
      id: `widget-${w.id}`,
      ...(w.content || {}),
      ...(w.style || {}),
      ...(w.children ? { _children: w.children.map(widgetToPuck) } : {}),
    },
  };
}

function puckToWidget(node) {
  const { id, _children, ...props } = node.props || {};
  return {
    widget_type: node.type,
    content: props,
    style: {},
    children: (_children || []).map(puckToWidget),
  };
}
'''


# ============================================================
#              PUBLIC RENDERER
# ============================================================

PUBLIC_RENDERER = '''import { Render } from "@measured/puck";
import { useEffect, useState } from "react";
import { puckConfig } from "../puck/config";

/**
 * Rendu public d'une page sauvegardée.
 * Usage : <PublicPageRenderer pageId={1} />
 */
export default function PublicPageRenderer({ pageId }) {
  const [data, setData] = useState(null);

  useEffect(() => {
    fetch(`/api/v1/cms/widgets/?page=${pageId}`)
      .then((res) => res.json())
      .then((widgets) => {
        const list = Array.isArray(widgets) ? widgets : widgets.results || [];
        setData({
          content: list.map(widgetToPuck),
          root: { props: {} },
        });
      });
  }, [pageId]);

  if (!data) return <div className="page-loading">Chargement...</div>;

  return <Render config={puckConfig} data={data} />;
}

function widgetToPuck(w) {
  return {
    type: w.widget_type || w.type,
    props: {
      id: `widget-${w.id}`,
      ...(w.content || {}),
      ...(w.style || {}),
      ...(w.children ? { _children: w.children.map(widgetToPuck) } : {}),
    },
  };
}
'''


# ============================================================
#                  FONCTIONS UTILITAIRES
# ============================================================

def write_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    label = os.path.relpath(path, BASE_DIR)

    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            if f.read().strip() == content.strip():
                print(f"  [SKIP] {label}")
                return
        shutil.copy2(path, path + ".bak")

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  [OK] {label}")


def install_puck():
    pkg = os.path.join(BASE_DIR, "package.json")
    if not os.path.exists(pkg):
        print("  [ATTENTION] package.json introuvable.")
        return
    with open(pkg, "r", encoding="utf-8") as f:
        if "@measured/puck" in f.read():
            print("  [SKIP] @measured/puck déjà installé")
            return
    print("  → Installation de @measured/puck...")
    try:
        subprocess.run(["npm", "install", "@measured/puck"], cwd=BASE_DIR, check=True, shell=True)
        print("  [OK] @measured/puck installé")
    except subprocess.CalledProcessError:
        print("  [ATTENTION] Lancez manuellement : npm install @measured/puck")


def main():
    print("=" * 60)
    print("  INJECTION WIDGET BUILDER - FRONTEND")
    print("=" * 60)

    if not os.path.exists(SRC_DIR):
        print(f"  [ERREUR] src/ introuvable dans {BASE_DIR}")
        return

    print("\n1. Installation de Puck...")
    install_puck()

    print("\n2. Création de la config Puck (25 widgets)...")
    write_file(os.path.join(SRC_DIR, "puck", "config.jsx"), PUCK_CONFIG)

    print("\n3. Création du Page Builder...")
    write_file(os.path.join(SRC_DIR, "pages", "admin", "PageBuilder.jsx"), PAGE_BUILDER)

    print("\n4. Création du renderer public...")
    write_file(os.path.join(SRC_DIR, "components", "PublicPageRenderer.jsx"), PUBLIC_RENDERER)

    print("\n" + "=" * 60)
    print("  TERMINÉ !")
    print("=" * 60)
    print("\nUtilisation :")
    print("  Éditeur   : <Route path='/admin/pages/:pageId/builder' element={<PageBuilder />} />")
    print("  Rendu     : <PublicPageRenderer pageId={1} />")
    print("\n25 widgets disponibles :")
    print("  Structure   : Section, Columns, Divider, Spacer")
    print("  Basiques    : Heading, Text, Image, Button, IconBox")
    print("  Marketing   : CTA, Testimonial, PricingTable, Countdown, ProgressBar")
    print("  Média       : Gallery, Carousel, Video")
    print("  Interactif  : Accordion, Tabs, FlipBox, SocialShare")
    print("  Boutique    : ProductGrid, BlogList")


if __name__ == "__main__":
    main()