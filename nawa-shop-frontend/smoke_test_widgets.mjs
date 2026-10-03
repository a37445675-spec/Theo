/**
 * Smoke test pur Node.js — analyse statique des widgets.
 * Aucune dépendance à installer.
 *
 * Usage : node smoke_test_widgets.mjs
 */
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const WIDGETS_DIR = path.join(__dirname, "src", "puck", "widgets");

// Couleurs terminal
const RESET = "\x1b[0m";
const RED = "\x1b[31m";
const GREEN = "\x1b[32m";
const YELLOW = "\x1b[33m";
const CYAN = "\x1b[36m";
const BOLD = "\x1b[1m";

// Statistiques
const stats = {
  files: 0,
  widgets: 0,
  validWidgets: 0,
  brokenWidgets: 0,
  errors: [],
  warnings: [],
  widgetsByFile: {},
};

// Regex pour détecter un widget exporté
const WIDGET_EXPORT = /export\s+const\s+(\w+)\s*=\s*\{/g;
const FIELD_PATTERN = /fields\s*:\s*\{/;
const DEFAULT_PROPS_PATTERN = /defaultProps\s*:\s*\{/;
const RENDER_PATTERN = /render\s*:\s*\(/;

/**
 * Vérifie qu'un fichier a une syntaxe équilibrée.
 */
function checkBalanced(content, filename) {
  const checks = [
    { name: "{}", open: "{", close: "}" },
    { name: "()", open: "(", close: ")" },
    { name: "[]", open: "[", close: "]" },
  ];

  for (const check of checks) {
    // Compter en ignorant les strings/commentaires (approximation)
    const opens = (content.match(new RegExp(`\\${check.open}`, "g")) || []).length;
    const closes = (content.match(new RegExp(`\\${check.close}`, "g")) || []).length;

    // Tolérer un décalage de ±2 (strings, regex, etc.)
    const diff = opens - closes;
    if (Math.abs(diff) > 5) {
      stats.warnings.push(
        `${filename} : déséquilibre ${check.name} (${diff > 0 ? "+" : ""}${diff})`
      );
    }
  }
}

/**
 * Analyse un fichier de widgets.
 */
function analyzeFile(filepath) {
  const filename = path.basename(filepath);
  const content = fs.readFileSync(filepath, "utf-8");

  stats.files++;

  // Vérifier la syntaxe
  checkBalanced(content, filename);

  // Trouver les widgets exportés
  const widgets = [];
  let match;
  WIDGET_EXPORT.lastIndex = 0;

  while ((match = WIDGET_EXPORT.exec(content)) !== null) {
    const widgetName = match[1];
    const startPos = match.index;

    // Trouver la fin approximative du widget (prochain export ou fin)
    WIDGET_EXPORT.lastIndex = startPos + match[0].length;
    const nextMatch = WIDGET_EXPORT.exec(content);
    const endPos = nextMatch ? nextMatch.index : content.length;
    WIDGET_EXPORT.lastIndex = startPos + match[0].length;

    const widgetCode = content.slice(startPos, endPos);

    const hasFields = FIELD_PATTERN.test(widgetCode);
    const hasDefaultProps = DEFAULT_PROPS_PATTERN.test(widgetCode);
    const hasRender = RENDER_PATTERN.test(widgetCode);

    const widget = {
      name: widgetName,
      file: filename,
      hasFields,
      hasDefaultProps,
      hasRender,
      isValid: hasFields && hasDefaultProps && hasRender,
    };

    widgets.push(widget);
    stats.widgets++;

    if (widget.isValid) {
      stats.validWidgets++;
    } else {
      stats.brokenWidgets++;
      const missing = [];
      if (!hasFields) missing.push("fields");
      if (!hasDefaultProps) missing.push("defaultProps");
      if (!hasRender) missing.push("render");
      stats.errors.push(`${widgetName} (${filename}) — manque : ${missing.join(", ")}`);
    }
  }

  stats.widgetsByFile[filename] = widgets;
  return widgets;
}

/**
 * Vérifie les backticks manquants dans les template literals.
 */
function checkBackticks(filepath) {
  const filename = path.basename(filepath);
  const content = fs.readFileSync(filepath, "utf-8");
  const lines = content.split("\n");

  lines.forEach((line, index) => {
    // Détecter ${...} sans backtick autour
    if (/\$\{[^}]+\}/.test(line)) {
      // Vérifier s'il y a un backtick sur la ligne
      const hasBacktick = line.includes("`");
      // Ignorer les commentaires
      const isComment = line.trim().startsWith("//") || line.trim().startsWith("*");

      if (!hasBacktick && !isComment) {
        stats.warnings.push(
          `${filename}:${index + 1} — \${} sans backtick : ${line.trim().slice(0, 80)}`
        );
      }
    }
  });
}

/**
 * Fonction principale.
 */
function main() {
  console.log(`\n${BOLD}${CYAN}══════════════════════════════════════════════════════════════${RESET}`);
  console.log(`${BOLD}${CYAN}  SMOKE TEST — NAWA Commerce Widgets${RESET}`);
  console.log(`${BOLD}${CYAN}══════════════════════════════════════════════════════════════${RESET}\n`);

  if (!fs.existsSync(WIDGETS_DIR)) {
    console.log(`${RED}❌ Dossier introuvable : ${WIDGETS_DIR}${RESET}\n`);
    process.exit(1);
  }

  const files = fs.readdirSync(WIDGETS_DIR).filter((f) => f.endsWith(".jsx") && !f.endsWith(".bak"));

  console.log(`${CYAN}📁 ${files.length} fichiers de widgets trouvés${RESET}\n`);

  // Analyser chaque fichier
  files.forEach((file) => {
    analyzeFile(path.join(WIDGETS_DIR, file));
    checkBackticks(path.join(WIDGETS_DIR, file));
  });

  // Afficher les résultats par fichier
  console.log(`${BOLD}📊 Résultats par fichier :${RESET}`);
  console.log(`${"─".repeat(70)}`);

  Object.entries(stats.widgetsByFile).forEach(([filename, widgets]) => {
    const valid = widgets.filter((w) => w.isValid).length;
    const broken = widgets.length - valid;
    const icon = broken === 0 ? "✅" : "⚠️ ";
    console.log(`  ${icon} ${filename.padEnd(40)} ${valid}/${widgets.length} widgets valides`);
  });

  // Résumé global
  console.log(`\n${BOLD}══════════════════════════════════════════════════════════════${RESET}`);
  console.log(`${BOLD}  RÉSUMÉ${RESET}`);
  console.log(`${BOLD}══════════════════════════════════════════════════════════════${RESET}`);
  console.log(`  Fichiers analysés    : ${stats.files}`);
  console.log(`  Widgets trouvés      : ${stats.widgets}`);
  console.log(`  ${GREEN}Widgets valides      : ${stats.validWidgets}${RESET}`);
  console.log(`  ${stats.brokenWidgets > 0 ? RED : GREEN}Widgets défaillants  : ${stats.brokenWidgets}${RESET}`);

  // Erreurs
  if (stats.errors.length > 0) {
    console.log(`\n${RED}${BOLD}❌ Widgets défaillants :${RESET}`);
    stats.errors.forEach((e) => console.log(`  ${RED}•${RESET} ${e}`));
  }

  // Avertissements
  if (stats.warnings.length > 0) {
    console.log(`\n${YELLOW}${BOLD}⚠️  Avertissements (${stats.warnings.length}) :${RESET}`);
    stats.warnings.slice(0, 30).forEach((w) => console.log(`  ${YELLOW}•${RESET} ${w}`));
    if (stats.warnings.length > 30) {
      console.log(`  ${YELLOW}... et ${stats.warnings.length - 30} autres${RESET}`);
    }
  }

  // Verdict
  console.log(`\n${BOLD}══════════════════════════════════════════════════════════════${RESET}`);
  if (stats.brokenWidgets === 0) {
    console.log(`${GREEN}${BOLD}  🎉 TOUS LES WIDGETS SONT VALIDES${RESET}`);
  } else {
    console.log(`${RED}${BOLD}  ⚠️  ${stats.brokenWidgets} widget(s) à corriger${RESET}`);
  }
  console.log(`${BOLD}══════════════════════════════════════════════════════════════${RESET}\n`);

  process.exit(stats.brokenWidgets > 0 ? 1 : 0);
}

main();