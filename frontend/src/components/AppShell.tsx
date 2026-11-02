"use client";

import { useState, type ReactNode } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Activity,
  CloudSun,
  Droplets,
  Home as HomeIcon,
  LayoutDashboard,
  Menu,
  ShieldCheck,
  Sun,
  X,
} from "lucide-react";
import { LANGUAGES, useI18n, type Lang } from "@/lib/i18n";

export const API_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ??
  process.env.NEXT_PUBLIC_API_URL ??
  "http://127.0.0.1:8000";

/** Active-link path for each page (treated equivalently). */
function normalize(path: string) {
  return path === "/" ? "/home" : path;
}

export function LanguageSwitcher() {
  const { lang, setLang, t } = useI18n();

  return (
    <label className="lang-switch">
      <span className="lang-switch-label">{t.langSwitch.label}</span>
      <select
        aria-label={t.langSwitch.label}
        value={lang}
        onChange={(event) => setLang(event.target.value as Lang)}
      >
        {LANGUAGES.map((entry) => (
          <option key={entry.code} value={entry.code}>
            {entry.native}
          </option>
        ))}
      </select>
    </label>
  );
}

export function AppShell({ children }: { children: ReactNode }) {
  const { t } = useI18n();
  const pathname = usePathname();
  const [mobileNav, setMobileNav] = useState(false);
  const current = normalize(pathname);

  const links = [
    { href: "/home", icon: HomeIcon, label: t.nav.overview },
    { href: "/guidance", icon: ShieldCheck, label: t.nav.safetyGuidance },
    { href: "/resources", icon: Droplets, label: t.nav.resources },
    { href: "/dashboard", icon: LayoutDashboard, label: t.dashboard.overline },
  ];

  return (
    <div className="app-shell">
      {mobileNav && (
        <button
          className="nav-scrim"
          aria-label={t.nav.closeNav}
          onClick={() => setMobileNav(false)}
        />
      )}
      <aside className={`sidebar ${mobileNav ? "sidebar-open" : ""}`}>
        <div className="brand">
          <div className="brand-mark">
            <Sun size={18} />
          </div>
          <div>
            <strong>{t.brand.name}</strong>
            <span>{t.brand.suffix}</span>
          </div>
          {mobileNav && (
            <button
              className="close-nav"
              onClick={() => setMobileNav(false)}
              aria-label={t.nav.closeNav}
            >
              <X size={20} />
            </button>
          )}
        </div>
        <div className="workspace-label">{t.nav.workspace}</div>
        <nav aria-label={t.nav.primaryNav}>
          {links.map(({ href, icon: Icon, label }) => (
            <Link
              key={href}
              className={`nav-item ${current === href ? "active" : ""}`}
              href={href}
              onClick={() => setMobileNav(false)}
            >
              <Icon size={17} />
              {label}
            </Link>
          ))}
          <span className="nav-item planned">
            <Activity size={17} />
            {t.nav.assessments}
            <em>{t.nav.planned}</em>
          </span>
        </nav>
        <div className="sidebar-bottom">
          <div className="source-note">
            <CloudSun size={16} />
            <div>
              <strong>{t.source.label}</strong>
              <span>{t.source.name}</span>
            </div>
          </div>
          <p>{t.source.note}</p>
        </div>
      </aside>

      <main className="main-content">
        <header className="topbar">
          <button
            className="mobile-menu"
            onClick={() => setMobileNav(true)}
            aria-label={t.nav.openNav}
          >
            <Menu size={21} />
          </button>
          <div className="location-context">
            <Sun size={16} />
            <strong>
              {t.brand.name} {t.brand.suffix}
            </strong>
          </div>
          <div className="topbar-right">
            <LanguageSwitcher />
            <div className="avatar">HS</div>
          </div>
        </header>
        {children}
      </main>
    </div>
  );
}
