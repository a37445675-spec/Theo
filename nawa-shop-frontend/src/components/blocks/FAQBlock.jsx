import { useState } from "react";

export default function FAQBlock({ config }) {
  const [openIndex, setOpenIndex] = useState(null);
  const items = config?.items || [];
  if (items.length === 0) return null;

  return (
    <section className="section">
      <div className="container faq-container">
        <h2>Questions fréquentes</h2>
        {items.map((item, i) => (
          <div className="faq-item" key={i}>
            <button className="faq-question" onClick={() => setOpenIndex(openIndex === i ? null : i)}>
              {item.question}
              <span>{openIndex === i ? "−" : "+"}</span>
            </button>
            {openIndex === i && <p className="faq-answer">{item.answer}</p>}
          </div>
        ))}
      </div>
    </section>
  );
}
