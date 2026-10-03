import { useState } from "react";
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
