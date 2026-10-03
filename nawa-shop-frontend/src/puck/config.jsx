/**
 * config.jsx — Configuration Puck
 * Bibliothèque complète des widgets NAWA Commerce.
 *
 * Architecture :
 *   - Imports groupés par phase / série
 *   - Widgets inline (Phase 7) pour les basiques
 *   - Widgets importés pour les modules avancés
 */
import React from "react";

// ============================================================
//  IMPORTS — Groupés par module
// ============================================================

/* === PHASE 7 : Widgets de base (inline plus bas) === */

/* === PHASE 8 : Média & Interactifs === */
import {
  CarouselLoop, CarouselMedia, CarouselNested, Slides, VideoPlaylist,
} from "./widgets/mediaWidgets";
import {
  TestimonialCarousel, LottieWidget, Hotspot, TableOfContents,
  Counter, ProgressReview, CodeHighlight, Portfolio, Review,
} from "./widgets/interactiveWidgets";

/* === PHASE 9 : Marketing & Social === */
import {
  FacebookPage, FacebookButton, FacebookEmbed, FacebookComments,
  PayPalButton, StripeButton,
} from "./widgets/marketingWidgets";
import {
  MegaMenu, OffCanvas, MenuCart, SocialShareExtended,
  WhatsAppFloat, NewsletterPopup, CookieBanner,
} from "./widgets/socialWidgets";

/* === PHASE 10 : Post & Archive dynamiques === */
import {
  PostTitle, PostContent, PostExcerpt, PostInfo,
  PostNavigation, PostComments, AuthorBox,
} from "./widgets/postWidgets";
import {
  ArchiveTitle, ArchivePosts, Breadcrumbs, LoopGrid, LoopCarousel,
  Taxonomy, SiteLogo, SiteTitle, SitelinkSearch, PostPortfolio,
} from "./widgets/archiveWidgets";

/* === PHASE 11 : E-commerce === */
import {
  ProductTitle, ProductImages, ProductPrice, AddToCart,
  ProductRating, ProductStock, ProductMeta, ShortDescription,
  ProductContent, ProductDataTabs, ProductGrid, Upsells,
  RelatedProducts, ProductCategories,
} from "./widgets/productWidgets";
import {
  Cart, Checkout, PurchaseSummary, MyAccount,
  WcBreadcrumbs, MenuCartExtended,
} from "./widgets/commerceWidgets";

/* === LAYOUT de base (Box, ColumnsPreset uniquement — Flex et Grid viennent de Série 6) === */
import {
  Box, ColumnsPreset,
} from "./widgets/layoutWidgets";

/* === LAYOUT responsive (Container vient de Série 6) === */
import {
  Stack, Cluster, Sidebar, Split,
  SectionOverlay, Card, StickyContainer, TabsVertical, AccordionContainer,
} from "./widgets/responsiveWidgets";

/* === WIDGETS AVANCÉS === */
import {
  Masonry, Marquee, Cascade, Repeater,
  Modal, Drawer, Portal, Mask,
} from "./widgets/advancedWidgets";

/* === MÉDIA PRO (SliderPro vient de Série 6) === */
import {
  GalleryLightbox, VideoPlayerCustom,
} from "./widgets/mediaProWidgets";

/* === SÉRIE 2 === */
import {
  PricingPro, CountdownPro, TestimonialWall, StatsSection,
  StepsProcess, TeamGrid, LogoCloud, FeatureList,
} from "./widgets/widgetsSeries2";

/* === SÉRIE 3 === */
import {
  FaqPro, TimelinePro, ComparisonPro, BeforeAfterPro,
  ProgressRingPro, RatingBreakdownPro, NotificationBannerPro, TrustBadgesPro,
} from "./widgets/widgetsSeries3";

/* === SÉRIE 4 === */
import {
  ChatWidgetPro, CookieConsentPro, NewsletterInlinePro, ExitIntentPopupPro,
  SocialProofPro, BackToTopPro, ScrollProgressPro, StickyCtaPro,
} from "./widgets/widgetsSeries4";

/* === SÉRIE 5 === */
import {
  SearchBarAdvanced, ProductComparator, MultiStepFormPro, PriceSimulatorPro,
  BookingCalendarPro, QuizPro, WishlistPro, RecentlyViewedPro,
} from "./widgets/widgetsSeries5";

/* === SÉRIE 6 : UPGRADE CORE (remplace SliderPro, Container, FlexContainer, GridContainer) === */
import {
  SliderPro, GridContainer, Container, FlexContainer,
} from "./widgets/widgetsCoreUpgrade";


// ============================================================
//  WIDGETS INLINE (Phase 7 — Base)
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
        {puck.renderDropZone ? puck.renderDropZone() : null}
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
    const cols = layout.includes("-")
      ? layout.split("-").length
      : parseInt(layout, 10);
    const template = layout.includes("-")
      ? layout.split("-").map((n) => `${n}fr`).join(" ")
      : `repeat(${cols}, 1fr)`;
    return (
      <div style={{ display: "grid", gridTemplateColumns: template, gap }}>
        {Array.from({ length: cols }).map((_, i) => (
          <div key={i}>
            {puck.renderDropZone ? puck.renderDropZone({ zone: `col-${i}` }) : null}
          </div>
        ))}
      </div>
    );
  },
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
  fields: { height: { type: "text", label: "Hauteur", defaultValue: "40px" } },
  defaultProps: { height: "40px" },
  render: ({ height }) => <div style={{ height }} />,
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
        { label: "H1", value: "h1" },
        { label: "H2", value: "h2" },
        { label: "H3", value: "h3" },
        { label: "H4", value: "h4" },
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
  defaultProps: {
    src: "/fallbacks/product-fallback.jpg", alt: "",
    ratio: "auto", radius: "12px",
  },
  render: ({ src, alt, ratio, radius }) => (
    <img
      src={src} alt={alt}
      style={{
        width: "100%",
        aspectRatio: ratio === "auto" ? undefined : ratio,
        objectFit: "cover", borderRadius: radius,
      }}
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
    background: { type: "text", label: "Fond", defaultValue: "#C1652F" },
    textColor: { type: "text", label: "Texte", defaultValue: "#FFFFFF" },
  },
  defaultProps: {
    title: "Prêt à découvrir ?",
    subtitle: "Rejoignez NAWA dès aujourd'hui.",
    buttonLabel: "Commencer", buttonUrl: "/boutique",
    background: "#C1652F", textColor: "#FFFFFF",
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
    highlighted: {
      type: "radio", label: "Mis en avant",
      options: [{ label: "Oui", value: "true" }, { label: "Non", value: "false" }],
    },
  },
  defaultProps: {
    title: "Premium", price: "29€", period: "/mois",
    features: "Livraison offerte\nSupport prioritaire\n-10% permanent",
    ctaLabel: "Choisir", ctaUrl: "#", highlighted: "false",
  },
  render: ({ title, price, period, features, ctaLabel, ctaUrl, highlighted }) => {
    const isHighlighted = highlighted === "true" || highlighted === true;
    return (
      <div style={{
        padding: "32px",
        background: isHighlighted ? "#2F4A3C" : "#fff",
        color: isHighlighted ? "#F7F0E4" : "#221B15",
        borderRadius: "16px", boxShadow: "0 4px 12px rgba(0,0,0,0.08)",
        transform: isHighlighted ? "scale(1.05)" : "none",
      }}>
        <h3>{title}</h3>
        <div style={{ fontSize: "2.5rem", fontWeight: 700, margin: "12px 0" }}>
          {price}<span style={{ fontSize: "1rem", fontWeight: 400 }}>{period}</span>
        </div>
        <ul style={{ listStyle: "none", padding: 0, margin: "16px 0" }}>
          {features.split("\n").map((f, i) => (
            <li key={i} style={{ padding: "4px 0" }}>✓ {f}</li>
          ))}
        </ul>
        <a href={ctaUrl} className="btn btn-primary" style={{ width: "100%", display: "block", textAlign: "center" }}>
          {ctaLabel}
        </a>
      </div>
    );
  },
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
            <div key={u}>
              <div style={{ fontSize: "2rem", fontWeight: 700 }}>
                {String(v).padStart(2, "0")}
              </div>
              <div style={{ fontSize: "0.75rem" }}>{u}</div>
            </div>
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
    frontTitle: { type: "text", label: "Titre avant" },
    frontColor: { type: "text", label: "Fond avant", defaultValue: "#C1652F" },
    backTitle: { type: "text", label: "Titre arrière" },
    backText: { type: "textarea", label: "Texte arrière" },
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
            display: "flex", alignItems: "center", justifyContent: "center",
            fontSize: "1.5rem", fontWeight: 600,
          }}>{frontTitle}</div>
          <div style={{
            position: "absolute", inset: 0, backfaceVisibility: "hidden",
            background: backColor, color: "#fff", borderRadius: "16px",
            display: "flex", flexDirection: "column", alignItems: "center",
            justifyContent: "center", padding: "24px",
            transform: "rotateY(180deg)", textAlign: "center",
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
  defaultProps: { items: "Question 1|Réponse 1\nQuestion 2|Réponse 2\nQuestion 3|Réponse 3" },
  render: ({ items }) => {
    const [open, setOpen] = React.useState(0);
    const list = items.split("\n").map((l) => l.split("|"));
    return (
      <div>
        {list.map(([q, a], i) => (
          <div key={i} style={{ borderBottom: "1px solid #eee" }}>
            <button
              onClick={() => setOpen(open === i ? -1 : i)}
              style={{
                width: "100%", textAlign: "left", padding: "16px 0",
                background: "none", border: "none", cursor: "pointer",
                fontWeight: 600, fontSize: "1rem",
              }}
            >
              {open === i ? "−" : "+"} {q}
            </button>
            {open === i && (
              <div style={{ padding: "0 0 16px", color: "#6B6259" }}>{a}</div>
            )}
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
  defaultProps: {
    tabs: "Description|Contenu de la description\nLivraison|Info livraison\nRetours|Info retours",
  },
  render: ({ tabs }) => {
    const [active, setActive] = React.useState(0);
    const list = tabs.split("\n").map((l) => l.split("|"));
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
    images: "/fallbacks/product-fallback.jpg\n/fallbacks/blog-fallback.jpg\n/fallbacks/hero-fallback.jpg",
    columns: 3, gap: "12px",
  },
  render: ({ images, columns, gap }) => (
    <div style={{ display: "grid", gridTemplateColumns: `repeat(${columns}, 1fr)`, gap }}>
      {images.split("\n").map((url, i) => (
        <img key={i} src={url} alt="" style={{ width: "100%", aspectRatio: "1/1", objectFit: "cover", borderRadius: "8px" }} />
      ))}
    </div>
  ),
};

const Carousel = {
  fields: {
    images: { type: "textarea", label: "URLs (1 par ligne)" },
    height: { type: "text", label: "Hauteur", defaultValue: "300px" },
    autoPlay: {
      type: "radio", label: "Auto",
      options: [{ label: "Oui", value: "true" }, { label: "Non", value: "false" }],
    },
  },
  defaultProps: {
    images: "/fallbacks/hero-fallback.jpg\n/fallbacks/blog-fallback.jpg\n/fallbacks/product-fallback.jpg",
    height: "300px", autoPlay: "true",
  },
  render: ({ images, height, autoPlay }) => {
    const list = images.split("\n").filter(Boolean);
    const [i, setI] = React.useState(0);
    const shouldAuto = autoPlay === "true" || autoPlay === true;
    React.useEffect(() => {
      if (!shouldAuto) return;
      const id = setInterval(() => setI((v) => (v + 1) % list.length), 3500);
      return () => clearInterval(id);
    }, [shouldAuto, list.length]);
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
    title: { type: "text", label: "Titre" },
    url: { type: "text", label: "URL à partager" },
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
              style={{
                width: 40, height: 40, display: "flex", alignItems: "center",
                justifyContent: "center", background: "#fff", borderRadius: "50%",
                boxShadow: "0 2px 8px rgba(0,0,0,0.1)", textDecoration: "none", fontSize: "1.2rem",
              }}>
              {l.emoji}
            </a>
          ))}
        </div>
      </div>
    );
  },
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
    // === Structure & Layout ===
    Section, Columns, Divider, Spacer,
    Box, FlexContainer, GridContainer, ColumnsPreset,
    Container, Stack, Cluster, Sidebar, Split,
    SectionOverlay, Card, StickyContainer, TabsVertical, AccordionContainer,

    // === Basiques ===
    Heading, Text, Image, Button, IconBox,

    // === Marketing ===
    CTA, Testimonial, PricingTable, Countdown, ProgressBar,

    // === Média ===
    Gallery, Carousel, Video, SocialShare,
    CarouselLoop, CarouselMedia, CarouselNested, Slides, VideoPlaylist,
    SliderPro, GalleryLightbox, VideoPlayerCustom,

    // === Interactif ===
    Accordion, Tabs, FlipBox,
    TestimonialCarousel, LottieWidget, Hotspot, TableOfContents,
    Counter, ProgressReview, CodeHighlight, Portfolio, Review,

    // === Avancé ===
    Masonry, Marquee, Cascade, Repeater,
    Modal, Drawer, Portal, Mask,

    // === Marketing & Social ===
    FacebookPage, FacebookButton, FacebookEmbed, FacebookComments,
    PayPalButton, StripeButton,
    MegaMenu, OffCanvas, MenuCart, SocialShareExtended,
    WhatsAppFloat, NewsletterPopup, CookieBanner,

    // === Séries 2-5 ===
    PricingPro, CountdownPro, TestimonialWall, StatsSection,
    StepsProcess, TeamGrid, LogoCloud, FeatureList,
    FaqPro, TimelinePro, ComparisonPro, BeforeAfterPro,
    ProgressRingPro, RatingBreakdownPro, NotificationBannerPro, TrustBadgesPro,
    ChatWidgetPro, CookieConsentPro, NewsletterInlinePro, ExitIntentPopupPro,
    SocialProofPro, BackToTopPro, ScrollProgressPro, StickyCtaPro,
    SearchBarAdvanced, ProductComparator, MultiStepFormPro, PriceSimulatorPro,
    BookingCalendarPro, QuizPro, WishlistPro, RecentlyViewedPro,

    // === E-commerce ===
    ProductTitle, ProductImages, ProductPrice, AddToCart,
    ProductRating, ProductStock, ProductMeta, ShortDescription,
    ProductContent, ProductDataTabs, ProductGrid, Upsells,
    RelatedProducts, ProductCategories,
    Cart, Checkout, PurchaseSummary, MyAccount,
    WcBreadcrumbs, MenuCartExtended,

    // === Post & Archive ===
    PostTitle, PostContent, PostExcerpt, PostInfo,
    PostNavigation, PostComments, AuthorBox,
    ArchiveTitle, ArchivePosts, Breadcrumbs, LoopGrid, LoopCarousel,
    Taxonomy, SiteLogo, SiteTitle, SitelinkSearch, PostPortfolio,
  },

  categories: {
    structure: {
      title: "Structure",
      components: ["Section", "Columns", "Divider", "Spacer"],
    },
    layout: {
      title: "Layout avancé",
      components: ["Box", "FlexContainer", "GridContainer", "ColumnsPreset"],
    },
    responsiveLayout: {
      title: "Layout responsive",
      components: [
        "Container", "Stack", "Cluster", "Sidebar", "Split",
        "SectionOverlay", "Card", "StickyContainer",
        "TabsVertical", "AccordionContainer",
      ],
    },
    basics: {
      title: "Basiques",
      components: ["Heading", "Text", "Image", "Button", "IconBox"],
    },
    marketing: {
      title: "Marketing",
      components: ["CTA", "Testimonial", "PricingTable", "Countdown", "ProgressBar"],
    },
    media: {
      title: "Média",
      components: ["Gallery", "Carousel", "Video"],
    },
    mediaAdvanced: {
      title: "Média avancé",
      components: [
        "CarouselLoop", "CarouselMedia", "CarouselNested", "Slides",
        "VideoPlaylist", "LottieWidget", "Hotspot", "Portfolio",
      ],
    },
    mediaPro: {
      title: "Média Pro",
      components: ["SliderPro", "GalleryLightbox", "VideoPlayerCustom"],
    },
    interactive: {
      title: "Interactif",
      components: ["Accordion", "Tabs", "FlipBox", "SocialShare"],
    },
    interactiveAdvanced: {
      title: "Interactif avancé",
      components: [
        "TestimonialCarousel", "TableOfContents", "Counter",
        "ProgressReview", "CodeHighlight", "Review",
      ],
    },
    advancedLayout: {
      title: "Avancé",
      components: [
        "Masonry", "Marquee", "Cascade", "Repeater",
        "Modal", "Drawer", "Portal", "Mask",
      ],
    },
    facebook: {
      title: "Facebook",
      components: ["FacebookPage", "FacebookButton", "FacebookEmbed", "FacebookComments"],
    },
    payments: {
      title: "Paiement",
      components: ["PayPalButton", "StripeButton"],
    },
    navigationAdvanced: {
      title: "Navigation avancée",
      components: ["MegaMenu", "OffCanvas", "MenuCart"],
    },
    socialAdvanced: {
      title: "Social avancé",
      components: ["SocialShareExtended", "WhatsAppFloat"],
    },
    popups: {
      title: "Popups & RGPD",
      components: ["NewsletterPopup", "CookieBanner"],
    },
    series2: {
      title: "Série 2",
      components: [
        "PricingPro", "CountdownPro", "TestimonialWall", "StatsSection",
        "StepsProcess", "TeamGrid", "LogoCloud", "FeatureList",
      ],
    },
    series3: {
      title: "Série 3",
      components: [
        "FaqPro", "TimelinePro", "ComparisonPro", "BeforeAfterPro",
        "ProgressRingPro", "RatingBreakdownPro", "NotificationBannerPro", "TrustBadgesPro",
      ],
    },
    series4: {
      title: "Série 4 — Engagement",
      components: [
        "ChatWidgetPro", "CookieConsentPro", "NewsletterInlinePro", "ExitIntentPopupPro",
        "SocialProofPro", "BackToTopPro", "ScrollProgressPro", "StickyCtaPro",
      ],
    },
    series5: {
      title: "Série 5 — Interactions",
      components: [
        "SearchBarAdvanced", "ProductComparator", "MultiStepFormPro", "PriceSimulatorPro",
        "BookingCalendarPro", "QuizPro", "WishlistPro", "RecentlyViewedPro",
      ],
    },
    productEcommerce: {
      title: "Produit",
      components: [
        "ProductTitle", "ProductImages", "ProductPrice", "AddToCart",
        "ProductRating", "ProductStock", "ProductMeta", "ShortDescription",
        "ProductContent", "ProductDataTabs",
      ],
    },
    shopEcommerce: {
      title: "Boutique",
      components: ["ProductGrid", "Upsells", "RelatedProducts", "ProductCategories"],
    },
    cartEcommerce: {
      title: "Panier & Commande",
      components: ["Cart", "Checkout", "PurchaseSummary", "MenuCartExtended"],
    },
    accountEcommerce: {
      title: "Compte & Navigation",
      components: ["MyAccount", "WcBreadcrumbs"],
    },
    postDynamic: {
      title: "Article (dynamique)",
      components: [
        "PostTitle", "PostContent", "PostExcerpt", "PostInfo",
        "PostNavigation", "PostComments", "AuthorBox",
      ],
    },
    archiveDynamic: {
      title: "Archive & Liste",
      components: [
        "ArchiveTitle", "ArchivePosts", "Breadcrumbs",
        "LoopGrid", "LoopCarousel", "Taxonomy", "PostPortfolio",
      ],
    },
    siteIdentity: {
      title: "Identité du site",
      components: ["SiteLogo", "SiteTitle", "SitelinkSearch"],
    },
  },
};