import { useEffect, useRef, useState } from "react";

export default function Reveal({ as: Component = "div", children, className = "", ...props }) {
  const ref = useRef(null);
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    const node = ref.current;
    if (!node) return;
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setVisible(true);
          observer.disconnect();
        }
      },
      { threshold: 0.12 }
    );
    observer.observe(node);
    return () => observer.disconnect();
  }, []);

  return (
    <Component ref={ref} className={`reveal ${visible ? "is-visible" : ""} ${className}`} {...props}>
      {children}
    </Component>
  );
}
