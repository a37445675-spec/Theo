import { Helmet } from "react-helmet-async";

/**
 * Composant SEO : injecte toutes les balises méta dans le <head>.
 *
 * Usage :
 *   <SeoHead
 *     title="Boutique Cosmétiques"
 *     description="Découvrez notre sélection..."
 *     image="/media/seo/og/cosmetiques.jpg"
 *     url="/boutique/cosmetiques"
 *     type="website"
 *   />
 *
 * Ou depuis une réponse API :
 *   <SeoHead {...mapSeoFromApi(seoData)} />
 */
export default function SeoHead({
  title,
  description,
  keywords,
  image,
  url,
  type = "website",
  robots = "index,follow",
  canonical,
  structuredData,
  siteName = "NAWA",
}) {
  const siteUrl = typeof window !== "undefined" ? window.location.origin : "";
  const fullUrl = url ? `${siteUrl}${url}` : (typeof window !== "undefined" ? window.location.href : "");
  const fullImage = image
    ? (image.startsWith("http") ? image : `${siteUrl}${image}`)
    : null;

  const finalTitle = title ? `${title} — ${siteName}` : siteName;
  const finalDesc = description || "La beauté d'Afrique, sublimée. Cosmétiques naturels, mode, chaussures et électroménager.";

  return (
    <Helmet>
      {/* Titre et description */}
      <title>{finalTitle}</title>
      <meta name="description" content={finalDesc} />
      {keywords && <meta name="keywords" content={keywords} />}

      {/* Robots */}
      <meta name="robots" content={robots} />

      {/* Canonique */}
      {canonical && <link rel="canonical" href={canonical} />}
      {!canonical && fullUrl && <link rel="canonical" href={fullUrl} />}

      {/* Open Graph (Facebook, LinkedIn, WhatsApp) */}
      <meta property="og:type" content={type} />
      <meta property="og:title" content={finalTitle} />
      <meta property="og:description" content={finalDesc} />
      {fullUrl && <meta property="og:url" content={fullUrl} />}
      {fullImage && <meta property="og:image" content={fullImage} />}
      <meta property="og:site_name" content={siteName} />
      <meta property="og:locale" content="fr_FR" />

      {/* Twitter / X */}
      <meta name="twitter:card" content="summary_large_image" />
      <meta name="twitter:title" content={finalTitle} />
      <meta name="twitter:description" content={finalDesc} />
      {fullImage && <meta name="twitter:image" content={fullImage} />}

      {/* JSON-LD (données structurées) */}
      {structuredData && Object.keys(structuredData).length > 0 && (
        <script type="application/ld+json">
          {JSON.stringify(structuredData)}
        </script>
      )}
    </Helmet>
  );
}

/**
 * Utilitaire : convertit une réponse API SEO en props pour <SeoHead />.
 */
export function mapSeoFromApi(seo) {
  if (!seo) return {};
  return {
    title: seo.meta_title || seo.og_title || undefined,
    description: seo.meta_description || seo.og_description || undefined,
    keywords: seo.meta_keywords || undefined,
    image: seo.og_image_url || undefined,
    type: seo.og_type || "website",
    robots: seo.robots || "index,follow",
    canonical: seo.canonical_url || undefined,
    structuredData: seo.structured_data || undefined,
  };
}
