export default function HaloDivider({ flip = false }) {
  return (
    <div className={`halo-divider ${flip ? "flip" : ""}`}>
      <svg viewBox="0 0 1440 60" preserveAspectRatio="none"><path fill="currentColor" d="M0,32 C240,64 480,0 720,16 C960,32 1200,64 1440,32 L1440,60 L0,60 Z" /></svg>
    </div>
  );
}
