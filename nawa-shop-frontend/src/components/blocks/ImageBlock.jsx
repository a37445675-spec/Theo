export default function ImageBlock({ config }) {
  if (!config?.src) return null;
  return (
    <div className="container">
      <img className="block-image" src={config.src} alt={config.alt || ""} loading="lazy" />
    </div>
  );
}
