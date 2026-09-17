import i18n from "i18next";
import { initReactI18next } from "react-i18next";
import en from "./locales/en.json";
import es from "./locales/es.json";
import it from "./locales/it.json";

export const LANGS = ["es", "en", "it"] as const;
export type Lang = (typeof LANGS)[number];
export const LANG_KEY = "stocks.lang";

export function isLang(value: string): value is Lang {
  return (LANGS as readonly string[]).includes(value);
}

function initialLang(): Lang {
  const stored = localStorage.getItem(LANG_KEY) ?? localStorage.getItem("acciones.lang");
  if (stored && isLang(stored)) return stored;
  const nav = navigator.language.toLowerCase();
  if (nav.startsWith("en")) return "en";
  if (nav.startsWith("it")) return "it";
  return "es";
}

function applyDocumentLang(lng: string): void {
  const lang: Lang = isLang(lng) ? lng : "es";
  document.documentElement.lang = lang;
  document.title = i18n.t("app.documentTitle");
}

void i18n.use(initReactI18next).init({
  resources: {
    es: { translation: es },
    en: { translation: en },
    it: { translation: it },
  },
  lng: initialLang(),
  fallbackLng: "es",
  interpolation: { escapeValue: false },
}).then(() => {
  applyDocumentLang(i18n.language);
});

i18n.on("languageChanged", applyDocumentLang);

export function setLanguage(lng: Lang): void {
  void i18n.changeLanguage(lng);
  localStorage.setItem(LANG_KEY, lng);
}

export default i18n;
