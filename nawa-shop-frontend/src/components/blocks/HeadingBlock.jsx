export default function HeadingBlock({ config }) {
  const Tag = config?.level || "h2";
  return (
    <div className="container">
      <Tag className="block-heading">{config?.text || ""}</Tag>
    </div>
  );
}
