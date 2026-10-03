import { useFetch } from "../hooks/useFetch.js";
import { getInvoices } from "../api/billing.js";
import { formatDate, formatPrice } from "../utils.js";
import { EmptyState, ErrorState } from "../components/StateBlocks.jsx";
import { SkeletonGrid } from "../components/Skeleton.jsx";
import SEO from "../components/SEO.jsx";

export default function AccountInvoices() {
  const { data: invoices, loading, error, refetch } = useFetch(getInvoices, []);

  return (
    <>
      <SEO title="Mes factures — NAWA" description="Vos factures NAWA." />
      <section className="page-header"><div className="container"><h1>Mes factures</h1></div></section>

      <section className="section">
        <div className="container">
          {loading && <SkeletonGrid count={2} />}
          {error && <ErrorState onRetry={refetch} />}
          {!loading && !error && (!invoices || invoices.length === 0) && <EmptyState icon="🧾" title="Aucune facture pour le moment" />}
          {!loading && invoices?.length > 0 && (
            <ul className="order-list" style={{ background: "var(--color-white)", borderRadius: 16, padding: 20, boxShadow: "var(--shadow-sm)" }}>
              {invoices.map((inv) => (
                <li key={inv.id}>
                  <span>{inv.invoiceNumber}</span>
                  <span className="muted">{formatDate(inv.issuedAt)}</span>
                  <span className="muted">{inv.status}</span>
                  <span>{formatPrice(inv.total)}</span>
                  {inv.pdfFile ? <a href={inv.pdfFile} target="_blank" rel="noreferrer" className="link-arrow">PDF</a> : <span className="muted">PDF non généré</span>}
                </li>
              ))}
            </ul>
          )}
        </div>
      </section>
    </>
  );
}
