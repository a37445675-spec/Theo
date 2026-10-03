"""
Injection du composant DynamicForm - Frontend React.

Usage : python inject_week6_frontend.py
"""
import os
import shutil

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(BASE_DIR, "src")


DYNAMIC_FORM_JSX = '''import { useState } from "react";
import { useApi } from "../hooks/useApi";

/**
 * Formulaire dynamique piloté par le CMS.
 *
 * Usage :
 *   <DynamicForm slug="contact" />
 *   <DynamicForm slug="newsletter" onSuccess={(data) => navigate(data.redirect_url)} />
 */
export default function DynamicForm({ slug, onSuccess, className = "" }) {
  const { data: form, loading } = useApi(`/api/v1/forms/definitions/${slug}/`);
  const [values, setValues] = useState({});
  const [errors, setErrors] = useState({});
  const [submitting, setSubmitting] = useState(false);
  const [success, setSuccess] = useState(null);

  if (loading) return <div className="form-loading">Chargement du formulaire...</div>;
  if (!form) return <div className="form-error">Formulaire introuvable.</div>;

  const handleChange = (key, value) => {
    setValues((v) => ({ ...v, [key]: value }));
    setErrors((e) => ({ ...e, [key]: undefined }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    setErrors({});

    try {
      const res = await fetch("/api/v1/forms/submissions/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ form: form.id, data: values }),
      });

      const result = await res.json();

      if (!res.ok) {
        setErrors(result.errors || { _global: "Une erreur est survenue." });
        setSubmitting(false);
        return;
      }

      setSuccess(result);

      if (onSuccess) onSuccess(result);
    } catch (err) {
      setErrors({ _global: "Erreur réseau. Veuillez réessayer." });
    } finally {
      setSubmitting(false);
    }
  };

  if (success) {
    return (
      <div className="form-success">
        <p>{success.success_message}</p>
        {success.redirect_url && (
          <a href={success.redirect_url} className="btn btn-primary">
            Continuer
          </a>
        )}
      </div>
    );
  }

  return (
    <form className={`dynamic-form ${className}`} onSubmit={handleSubmit} noValidate>
      {form.description && <p className="form-description">{form.description}</p>}

      {form.fields.map((field) => (
        <div key={field.id} className={`form-group ${errors[field.field_key] ? "has-error" : ""}`}>
          <label htmlFor={`field-${field.field_key}`}>
            {field.label}
            {field.is_required && <span className="required">*</span>}
          </label>

          {renderField(field, values[field.field_key] || "", (v) => handleChange(field.field_key, v))}

          {field.help_text && <small className="form-help">{field.help_text}</small>}
          {errors[field.field_key] && <span className="form-error-msg">{errors[field.field_key]}</span>}
        </div>
      ))}

      {errors._global && <div className="form-error-global">{errors._global}</div>}

      <button type="submit" className="btn btn-primary" disabled={submitting}>
        {submitting ? "Envoi en cours..." : "Envoyer"}
      </button>
    </form>
  );
}


function renderField(field, value, onChange) {
  const commonProps = {
    id: `field-${field.field_key}`,
    name: field.field_key,
    required: field.is_required,
    placeholder: field.placeholder,
    value,
    onChange: (e) => onChange(e.target.value),
  };

  switch (field.field_type) {
    case "textarea":
      return <textarea {...commonProps} rows={5} />;

    case "select":
      return (
        <select {...commonProps}>
          <option value="">— Sélectionnez —</option>
          {(field.options || []).map((opt) => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>
      );

    case "radio":
      return (
        <div className="radio-group">
          {(field.options || []).map((opt) => (
            <label key={opt.value} className="radio-option">
              <input
                type="radio"
                name={field.field_key}
                value={opt.value}
                checked={value === opt.value}
                onChange={(e) => onChange(e.target.value)}
                required={field.is_required}
              />
              <span>{opt.label}</span>
            </label>
          ))}
        </div>
      );

    case "checkbox":
      return (
        <label className="checkbox-option">
          <input
            type="checkbox"
            id={`field-${field.field_key}`}
            name={field.field_key}
            checked={!!value}
            onChange={(e) => onChange(e.target.checked)}
          />
          <span>{field.placeholder || field.label}</span>
        </label>
      );

    case "number":
      return <input type="number" {...commonProps} />;
    case "email":
      return <input type="email" {...commonProps} />;
    case "phone":
      return <input type="tel" {...commonProps} />;
    case "date":
      return <input type="date" {...commonProps} />;

    default:
      return <input type="text" {...commonProps} />;
  }
}
'''


CSS_STYLES = """
/* ===== Formulaires dynamiques (CMS) ===== */
.dynamic-form {
  display: flex; flex-direction: column; gap: 1rem;
  max-width: 600px;
}
.form-group { display: flex; flex-direction: column; gap: 0.35rem; }
.form-group label { font-weight: 500; font-size: 0.9rem; }
.form-group .required { color: #DC2626; margin-left: 3px; }
.form-group input,
.form-group textarea,
.form-group select {
  padding: 0.7rem 0.9rem;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-family: inherit;
  font-size: 0.95rem;
  transition: border-color 0.2s;
}
.form-group input:focus,
.form-group textarea:focus,
.form-group select:focus {
  outline: none;
  border-color: var(--color-primary, #C1652F);
  box-shadow: 0 0 0 3px rgba(193, 101, 47, 0.1);
}
.form-group.has-error input,
.form-group.has-error textarea,
.form-group.has-error select { border-color: #DC2626; }
.form-error-msg { color: #DC2626; font-size: 0.85rem; }
.form-error-global {
  background: #FEE2E2; color: #991B1B;
  padding: 0.75rem 1rem; border-radius: 8px;
  font-size: 0.9rem;
}
.form-help { color: #6B7280; font-size: 0.8rem; }
.form-description { color: #4B5563; margin-bottom: 0.5rem; }
.form-success {
  background: #DCFCE7; color: #166534;
  padding: 1.25rem; border-radius: 12px;
  text-align: center;
}
.form-success p { margin: 0 0 1rem; font-weight: 500; }
.form-loading, .form-error { padding: 1rem; color: #6B7280; }
.radio-group { display: flex; flex-direction: column; gap: 0.5rem; }
.radio-option, .checkbox-option {
  display: flex; align-items: center; gap: 0.5rem;
  cursor: pointer; font-size: 0.95rem;
}
"""


def write_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    label = os.path.relpath(path, BASE_DIR)

    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            if f.read().strip() == content.strip():
                print(f"  [SKIP] {label}")
                return
        shutil.copy2(path, path + ".bak")
        print(f"  [BACKUP] {label}.bak")

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  [OK] {label}")


def append_css():
    for candidate in [
        os.path.join(SRC_DIR, "index.css"),
        os.path.join(SRC_DIR, "App.css"),
    ]:
        if os.path.exists(candidate):
            with open(candidate, "r", encoding="utf-8") as f:
                if ".dynamic-form" in f.read():
                    print(f"  [SKIP] styles déjà dans {os.path.basename(candidate)}")
                    return
            shutil.copy2(candidate, candidate + ".bak")
            with open(candidate, "a", encoding="utf-8") as f:
                f.write(CSS_STYLES)
            print(f"  [OK] styles ajoutés à {os.path.basename(candidate)}")
            return


def main():
    print("=" * 60)
    print("  INJECTION SEMAINE 6 - FRONTEND")
    print("=" * 60)

    if not os.path.exists(SRC_DIR):
        print(f"  [ERREUR] src/ introuvable dans {BASE_DIR}")
        return

    print("\n1. Création du composant DynamicForm...")
    write_file(
        os.path.join(SRC_DIR, "components", "DynamicForm.jsx"),
        DYNAMIC_FORM_JSX,
    )

    print("\n2. Injection des styles CSS...")
    append_css()

    print("\n" + "=" * 60)
    print("  TERMINÉ !")
    print("=" * 60)
    print("\nUtilisation dans une page :")
    print('  import DynamicForm from "../components/DynamicForm";')
    print('  <DynamicForm slug="contact" />')
    print('  <DynamicForm slug="newsletter" />')


if __name__ == "__main__":
    main()