import { useLocation } from "react-router-dom";

/** Rejoue l'animation d'entrée (page-transition, voir index.css) à chaque changement de route grâce à la key sur pathname. */
export default function PageTransition({ children }) {
  const location = useLocation();
  return (
    <div className="page-transition" key={location.pathname}>
      {children}
    </div>
  );
}
