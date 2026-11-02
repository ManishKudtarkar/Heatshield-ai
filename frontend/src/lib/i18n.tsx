"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";
import { translations, type Lang, type Strings } from "./translations";

export { LANGUAGES } from "./translations";
export type { Lang, Strings } from "./translations";

const STORAGE_KEY = "heatshield-lang";

interface I18nContextValue {
  lang: Lang;
  setLang: (lang: Lang) => void;
  t: Strings;
}

const I18nContext = createContext<I18nContextValue | undefined>(undefined);

function isValidLang(value: unknown): value is Lang {
  return value === "en" || value === "hi" || value === "gu";
}

export function LanguageProvider({ children }: { children: ReactNode }) {
  const [lang, setLangState] = useState<Lang>("en");

  // Restore the worker's preferred language on mount (client only).
  useEffect(() => {
    try {
      const stored = window.localStorage.getItem(STORAGE_KEY);
      if (isValidLang(stored)) {
        setLangState(stored);
      }
    } catch {
      // localStorage unavailable; keep the default language.
    }
  }, []);

  // Keep the <html lang> attribute in sync for accessibility.
  useEffect(() => {
    document.documentElement.lang = lang;
  }, [lang]);

  const setLang = useCallback((next: Lang) => {
    setLangState(next);
    try {
      window.localStorage.setItem(STORAGE_KEY, next);
    } catch {
      // Ignore write failure (e.g. private mode).
    }
  }, []);

  const value = useMemo<I18nContextValue>(
    () => ({ lang, setLang, t: translations[lang] }),
    [lang, setLang],
  );

  return <I18nContext.Provider value={value}>{children}</I18nContext.Provider>;
}

export function useI18n(): I18nContextValue {
  const ctx = useContext(I18nContext);
  if (!ctx) {
    throw new Error("useI18n must be used within a LanguageProvider");
  }
  return ctx;
}
