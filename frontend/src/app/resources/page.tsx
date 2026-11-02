"use client";

import { FormEvent, useState } from "react";
import { AppShell, API_URL } from "@/components/AppShell";
import { useI18n } from "@/lib/i18n";
import {
  AlertTriangle,
  Droplets,
  ExternalLink,
  Info,
  LocateFixed,
  Navigation,
  Search,
  Trees,
} from "lucide-react";

type Resource = {
  osm_id: string;
  name: string;
  category: string;
  category_label: string;
  osm_tags?: Record<string, string>;
  latitude: number;
  longitude: number;
  distance_km: number;
  source: string;
  source_url: string;
};

type CoolingResult = {
  location: { latitude: number; longitude: number };
  radius_m: number;
  categories: string[];
  resource_count: number;
  counts_by_category: Record<string, number>;
  resources: Resource[];
  source: string;
  limitations: string[];
};

type CoolingResponse = {
  success: boolean;
  result?: CoolingResult;
  detail?: string | { message?: string };
};

const CATEGORY_ICONS: Record<string, typeof Droplets> = {
  water: Droplets,
  shelter: Navigation,
  refuge: Info,
  shade: Trees,
};

export default function ResourcesPage() {
  const { t } = useI18n();
  const [form, setForm] = useState({ lat: "22.3073", lng: "73.1814", radius: "1500" });
  const [categories, setCategories] = useState<string[]>(["water", "shelter", "refuge", "shade"]);
  const [result, setResult] = useState<CoolingResult | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  function toggleCategory(category: string) {
    setCategories((current) =>
      current.includes(category)
        ? current.length > 1
          ? current.filter((item) => item !== category)
          : current
        : [...current, category],
    );
  }

  async function findResources(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    setError("");
    setResult(null);

    try {
      const response = await fetch(`${API_URL}/api/v1/cooling-resources`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          latitude: Number(form.lat),
          longitude: Number(form.lng),
          radius_m: Number(form.radius),
          categories,
        }),
      });
      const data = (await response.json()) as CoolingResponse;
      if (!response.ok || !data.success || !data.result) {
        const detail = typeof data.detail === "string" ? data.detail : data.detail?.message;
        throw new Error(detail || t.resources.loadError);
      }
      setResult(data.result);
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : t.resources.loadError);
    } finally {
      setLoading(false);
    }
  }

  function useBrowserLocation() {
    if (!("geolocation" in navigator)) return;
    navigator.geolocation.getCurrentPosition(
      (position) =>
        setForm((current) => ({
          ...current,
          lat: position.coords.latitude.toFixed(6),
          lng: position.coords.longitude.toFixed(6),
        })),
      () => setError(t.resources.loadError),
    );
  }

  const categoryLabels: Record<string, string> = {
    water: t.resources.catWater,
    shelter: t.resources.catShelter,
    refuge: t.resources.catRefuge,
    shade: t.resources.catShade,
  };

  return (
    <AppShell>
      <div className="content-wrap">
        <section className="page-heading">
          <div>
            <p className="overline">{t.resources.overline}</p>
            <h1>{t.resources.title}</h1>
            <p>{t.resources.subtitle}</p>
          </div>
        </section>

        <section className="assessment-layout">
          <form className="assessment-form panel" onSubmit={findResources}>
            <div className="section-heading">
              <div><p className="overline">{t.resources.overline}</p><h2>{t.resources.title}</h2></div>
            </div>
            <fieldset style={{ borderTop: "none", marginTop: 0 }}>
              <legend><span>01</span> {t.resources.findBtn}</legend>
              <div className="form-grid">
                <label>{t.resources.lat}<input required type="number" min="-90" max="90" step="0.000001" value={form.lat} onChange={(event) => setForm((c) => ({ ...c, lat: event.target.value }))} /></label>
                <label>{t.resources.lng}<input required type="number" min="-180" max="180" step="0.000001" value={form.lng} onChange={(event) => setForm((c) => ({ ...c, lng: event.target.value }))} /></label>
                <label>{t.resources.radius} ({t.resources.radiusUnit})<input required type="number" min="100" max="5000" step="100" value={form.radius} onChange={(event) => setForm((c) => ({ ...c, radius: event.target.value }))} /></label>
                <label>{t.resources.categories}
                  <div className="category-chips">
                    {Object.keys(categoryLabels).map((category) => (
                      <button
                        key={category}
                        type="button"
                        className={`chip ${categories.includes(category) ? "chip-active" : ""}`}
                        onClick={() => toggleCategory(category)}
                      >
                        {categoryLabels[category]}
                      </button>
                    ))}
                  </div>
                </label>
              </div>
              <button type="button" className="link-button geo-button" onClick={useBrowserLocation}>
                <LocateFixed size={14} /> {t.resources.useLocation}
              </button>
            </fieldset>
            <button className="primary-button submit-button" type="submit" disabled={loading}>
              {loading ? <><span className="spinner" /> {t.resources.searching}</> : <><Search size={16} /> {t.resources.findBtn}</>}
            </button>
            {error && <p className="error" role="alert"><AlertTriangle size={16} />{error}</p>}
            <p className="data-note" style={{ marginTop: 16 }}><Info size={15} />{t.resources.osmNote}</p>
          </form>

          <aside className="assessment-context panel">
            {result ? (
              <>
                <div className="section-heading"><div><p className="overline">{t.resources.overline}</p><h2>{t.resources.found.replace("{count}", String(result.resource_count))}</h2></div></div>
                <div className="worker-facts" style={{ marginTop: 18 }}>
                  {Object.entries(result.counts_by_category).map(([category, count]) => {
                    const Icon = CATEGORY_ICONS[category] ?? Info;
                    return (
                      <span key={category}><strong>{count}</strong><Icon size={12} style={{ verticalAlign: -2, marginRight: 5 }} />{categoryLabels[category] ?? category}</span>
                    );
                  })}
                </div>
              </>
            ) : (
              <div className="section-heading"><div><p className="overline">{t.resources.overline}</p><h2>{t.resources.findBtn}</h2></div></div>
            )}
          </aside>
        </section>

        {result && (
          result.resource_count === 0 ? (
            <section className="notice warning" style={{ marginTop: 24, fontSize: 13 }}>
              <AlertTriangle size={16} /><div><strong>{t.resources.noneFound}</strong></div>
            </section>
          ) : (
            <section className="alerts-grid" style={{ marginTop: 24 }}>
              {result.resources.map((resource) => {
                const Icon = CATEGORY_ICONS[resource.category] ?? Info;
                return (
                  <article className={`alert-card alert-advisory resource-card`} key={resource.osm_id}>
                    <div className="alert-head">
                      <span className="alert-icon advisory"><Icon size={16} /></span>
                      <h3>{resource.name}</h3>
                      <span className="alert-priority-tag priority-none">{t.resources.distance}: {resource.distance_km} km</span>
                    </div>
                    <div className="topic-card-meta">
                      <span>{categoryLabels[resource.category] ?? resource.category_label}</span>
                      {resource.osm_tags?.opening_hours && <span>{resource.osm_tags.opening_hours}</span>}
                    </div>
                    <div className="source-list" style={{ marginTop: 12 }}>
                      <li><ExternalLink size={13} /><a href={resource.source_url} target="_blank" rel="noopener noreferrer">{t.resources.sourceLink}</a></li>
                    </div>
                  </article>
                );
              })}
            </section>
          )
        )}

        <footer><strong>{t.footer.label}</strong> {t.footer.note}</footer>
      </div>
    </AppShell>
  );
}
