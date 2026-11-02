"use client";

import { FormEvent, useState } from "react";
import Link from "next/link";
import { AppShell, API_URL } from "@/components/AppShell";
import { useI18n } from "@/lib/i18n";
import type { Strings } from "@/lib/translations";
import {
  AlertTriangle,
  ArrowRight,
  CheckCircle2,
  ClipboardList,
  CloudSun,
  Droplets,
  Gauge,
  HeartPulse,
  Info,
  MapPin,
  ShieldCheck,
  Sun,
  Thermometer,
  Wind,
} from "lucide-react";

type WeatherSummary = {
  location?: string;
  country?: string;
  temperature_c?: number | null;
  humidity_percent?: number | null;
  apparent_temperature_c?: number | null;
  wind_speed_kmh?: number | null;
  timestamp?: string;
  source?: string;
  data_note?: string;
};

type DeterministicAssessment = {
  assessment_status?: string;
  weather_summary?: WeatherSummary;
  worker_summary?: Record<string, unknown>;
  recommended_controls?: Array<{ control?: string; description?: string } | string>;
  missing_information?: string[];
  limitations?: string[];
  exposure_concerns?: Array<{ factor?: string; description?: string; observation?: unknown }>;
  assessment_metadata?: Record<string, unknown>;
};

type SafetyAlert = {
  id?: string;
  priority?: "advisory" | "heightened_precaution" | "critical_precaution";
  title?: string;
  basis?: string;
  triggers?: string[];
  guidance?: string[];
};

type SafetyAlerts = {
  success?: boolean;
  alerts?: SafetyAlert[];
  alert_count?: number;
  highest_priority?: string;
  has_critical_precaution?: boolean;
  emergency_guidance?: string;
  summary?: string;
  limitations?: string[];
};

type AssessmentResult = {
  location?: string;
  assessment_id?: string;
  climate_analysis?: string;
  worker_exposure_analysis?: string;
  safety_advisory?: string;
  deterministic_assessment?: DeterministicAssessment;
  safety_alerts?: SafetyAlerts;
  validated_exposure_data?: Record<string, unknown>;
};

type AssessmentResponse = { success: boolean; result?: AssessmentResult; detail?: string | { message?: string } };

const initialForm = {
  location: "Vadodara",
  worker_name: "",
  occupation: "Construction worker",
  workload: "heavy",
  shift_hours: "8",
  direct_sunlight: true,
  shade_availability: "partial",
  water_access: true,
  acclimatization: "unknown",
  ppe_items: "Safety helmet, Safety boots, Protective clothing",
  continuous_exposure_minutes: "120",
  break_frequency_minutes: "",
  work_area: "Outdoor construction site",
};

/** Translate snake_case enum / missing-field keys via the active language. */
function tr(t: Strings, key: string): string {
  return (
    t.enums.missingInfo[key] ??
    t.enums.workload[key] ??
    t.enums.shade[key] ??
    t.enums.acclimatization[key] ??
    t.enums.assessmentStatus[key] ??
    t.enums.priority[key] ??
    key.replaceAll("_", " ").replace(/\b\w/g, (letter) => letter.toUpperCase())
  );
}

export default function Home() {
  const { t, lang } = useI18n();
  const [form, setForm] = useState(initialForm);
  const [assessment, setAssessment] = useState<AssessmentResult | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const display = (value: unknown): string => {
    if (typeof value === "boolean") return value ? t.display.yes : t.display.no;
    if (value === null || value === undefined || value === "") return t.display.notProvided;
    if (Array.isArray(value)) return value.join(", ") || t.display.noneReported;
    return String(value);
  };

  function updateField(field: keyof typeof initialForm, value: string | boolean) {
    setForm((current) => ({ ...current, [field]: value }));
  }

  async function submitAssessment(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    setError("");
    setAssessment(null);
    const worker = {
      occupation: form.occupation,
      workload: form.workload,
      shift_hours: Number(form.shift_hours),
      direct_sunlight: form.direct_sunlight,
      shade_availability: form.shade_availability,
      water_access: form.water_access,
      acclimatization: form.acclimatization,
      ppe_items: form.ppe_items.split(",").map((item) => item.trim()).filter(Boolean),
      continuous_exposure_minutes: form.continuous_exposure_minutes ? Number(form.continuous_exposure_minutes) : null,
      break_frequency_minutes: form.break_frequency_minutes ? Number(form.break_frequency_minutes) : null,
      work_area: form.work_area || null,
    };

    try {
      const response = await fetch(`${API_URL}/api/v1/assess`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          location: form.location,
          worker,
          language: lang,
          worker_name: form.worker_name || null,
        }),
      });
      const data = (await response.json()) as AssessmentResponse;
      if (!response.ok || !data.success || !data.result) {
        const detail = typeof data.detail === "string" ? data.detail : data.detail?.message;
        throw new Error(detail || t.form.errorDefault);
      }
      setAssessment(data.result);
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : t.form.errorConnect);
    } finally {
      setLoading(false);
    }
  }

  const deterministic = assessment?.deterministic_assessment;
  const weather = deterministic?.weather_summary;
  const missing = deterministic?.missing_information ?? [];
  const alerts = assessment?.safety_alerts;

  function Metric({ icon: Icon, name, value, unit, context }: { icon: typeof Thermometer; name: string; value: unknown; unit?: string; context: string }) {
    return (
      <article className="metric-card">
        <div className="metric-label"><Icon size={16} aria-hidden="true" />{name}</div>
        <div className="metric-value">{display(value)}<small>{unit}</small></div>
        <p>{context}</p>
      </article>
    );
  }

  function AlertCard({ alert }: { alert: SafetyAlert }) {
    const priority = alert.priority ?? "advisory";
    const Icon = priority === "advisory" ? Info : AlertTriangle;
    const tone = priority === "critical_precaution" ? "critical" : priority === "heightened_precaution" ? "heightened" : "advisory";
    return (
      <article className={`alert-card alert-${priority}`}>
        <div className="alert-head">
          <span className={`alert-icon ${tone}`}><Icon size={16} aria-hidden="true" /></span>
          <h3>{alert.title}</h3>
          <span className={`alert-priority-tag priority-${priority}`}>{tr(t, priority)}</span>
        </div>
        {alert.triggers && alert.triggers.length > 0 && (
          <ul className="alert-triggers">
            {alert.triggers.map((trigger, index) => <li key={index}>{trigger}</li>)}
          </ul>
        )}
        {alert.guidance && alert.guidance.length > 0 && (
          <ul className="alert-guidance">
            {alert.guidance.map((item, index) => <li key={index}>{item}</li>)}
          </ul>
        )}
      </article>
    );
  }

  return (
    <AppShell>
      <div className="content-wrap" id="overview">
        <section className="page-heading">
          <div>
            <p className="overline">{t.heading.overline}</p>
            <h1>{t.heading.title}</h1>
            <p>{t.heading.subtitle}</p>
          </div>
          <a className="primary-button heading-action" href="#new-assessment"><ClipboardList size={17} /> {t.heading.newAssessment}</a>
        </section>

        <section className="section-block">
          <div className="section-heading">
            <div><p className="overline">{t.env.overline}</p><h2>{t.env.title}</h2></div>
            {weather?.timestamp && <span className="timestamp">{t.env.observed} {weather.timestamp.replace("T", " ")}</span>}
          </div>
          <div className="metrics-grid">
            <Metric icon={Thermometer} name={t.metrics.airTemp} value={weather?.temperature_c} unit="°C" context={t.metrics.currentObs} />
            <Metric icon={Gauge} name={t.metrics.humidity} value={weather?.humidity_percent} unit="%" context={t.metrics.currentObs} />
            <Metric icon={Sun} name={t.metrics.apparentTemp} value={weather?.apparent_temperature_c} unit="°C" context={t.metrics.notWbgt} />
            <Metric icon={Wind} name={t.metrics.wind} value={weather?.wind_speed_kmh} unit="km/h" context={t.metrics.currentObs} />
          </div>
          {weather?.data_note && <p className="data-note"><Info size={15} />{weather.data_note}</p>}
        </section>

        <section className="overview-grid">
          <article className="panel status-panel">
            <div className="panel-title">
              <span className="icon-box teal"><CheckCircle2 size={17} /></span>
              <div><p className="overline">{t.status.overline}</p><h3>{deterministic ? tr(t, deterministic.assessment_status ?? "screening_only") : t.status.ready}</h3></div>
            </div>
            <p className="panel-copy">{deterministic ? t.status.completedCopy : t.status.readyCopy}</p>
            {deterministic && missing.length > 0 ? (
              <div className="notice warning"><AlertTriangle size={16} /><div><strong>{t.status.infoToCollect}</strong><span>{missing.map((item) => tr(t, item)).join(" • ")}</span></div></div>
            ) : (
              <div className="notice success"><CheckCircle2 size={16} /><div><strong>{t.status.readyForInput}</strong><span>{t.status.noAssessment}</span></div></div>
            )}
          </article>
          <article className="panel context-panel">
            <div className="panel-title">
              <span className="icon-box amber"><HeartPulse size={17} /></span>
              <div><p className="overline">{t.latest.overline}</p><h3>{deterministic ? display(deterministic.worker_summary?.occupation) : t.latest.noAssessment}</h3></div>
            </div>
            {deterministic?.worker_summary ? (
              <div className="worker-facts">
                <span><strong>{tr(t, String(deterministic.worker_summary.workload ?? ""))}</strong> {t.latest.workload}</span>
                <span><strong>{display(deterministic.worker_summary.direct_sunlight)}</strong> {t.latest.sunlight}</span>
                <span><strong>{tr(t, String(deterministic.worker_summary.shade_availability ?? ""))}</strong> {t.latest.shade}</span>
                <span><strong>{display(deterministic.worker_summary.water_access)}</strong> {t.latest.water}</span>
              </div>
            ) : (
              <p className="panel-copy">{t.latest.copy}</p>
            )}
          </article>
        </section>

        <section className="assessment-layout" id="new-assessment">
          <form className="assessment-form panel" onSubmit={submitAssessment}>
            <div className="section-heading">
              <div><p className="overline">{t.form.overline}</p><h2>{t.form.title}</h2></div>
              <span className="required-note">{t.form.required}</span>
            </div>
            <fieldset>
              <legend><span>01</span> {t.form.worksite}</legend>
              <div className="form-grid">
                <label>{t.form.location} *<input required value={form.location} onChange={(event) => updateField("location", event.target.value)} placeholder={t.form.locationPh} /></label>
                <label>{t.form.workArea}<input value={form.work_area} onChange={(event) => updateField("work_area", event.target.value)} placeholder={t.form.workAreaPh} /></label>
              </div>
            </fieldset>
            <fieldset>
              <legend><span>02</span> {t.form.workerProfile}</legend>
              <div className="form-grid">
                <label>{t.form.occupation} *<input required value={form.occupation} onChange={(event) => updateField("occupation", event.target.value)} /></label>
                <label>{t.form.workerName}<input value={form.worker_name} onChange={(event) => updateField("worker_name", event.target.value)} placeholder={t.form.workerNamePh} /></label>
                <label>{t.form.shiftHours} *<input required type="number" min="0.1" max="24" step="0.1" value={form.shift_hours} onChange={(event) => updateField("shift_hours", event.target.value)} /></label>
                <label>{t.form.workload} *
                  <select value={form.workload} onChange={(event) => updateField("workload", event.target.value)}>
                    {["light", "moderate", "heavy", "very_heavy", "unknown"].map((value) => <option key={value} value={value}>{t.enums.workload[value]}</option>)}
                  </select>
                </label>
                <label>{t.form.acclimatization} *
                  <select value={form.acclimatization} onChange={(event) => updateField("acclimatization", event.target.value)}>
                    {["acclimatized", "not_acclimatized", "unknown"].map((value) => <option key={value} value={value}>{t.enums.acclimatization[value]}</option>)}
                  </select>
                </label>
              </div>
            </fieldset>
            <fieldset>
              <legend><span>03</span> {t.form.envExposure}</legend>
              <div className="form-grid">
                <label>{t.form.directSunlight} *
                  <select value={String(form.direct_sunlight)} onChange={(event) => updateField("direct_sunlight", event.target.value === "true")}>
                    <option value="true">{t.form.sunlightYes}</option>
                    <option value="false">{t.form.sunlightNo}</option>
                  </select>
                </label>
                <label>{t.form.shadeAvailability} *
                  <select value={form.shade_availability} onChange={(event) => updateField("shade_availability", event.target.value)}>
                    {["full", "partial", "none", "unknown"].map((value) => <option key={value} value={value}>{t.enums.shade[value]}</option>)}
                  </select>
                </label>
              </div>
            </fieldset>
            <fieldset>
              <legend><span>04</span> {t.form.safetyProvisions}</legend>
              <div className="form-grid">
                <label>{t.form.waterAccess} *
                  <select value={String(form.water_access)} onChange={(event) => updateField("water_access", event.target.value === "true")}>
                    <option value="true">{t.form.waterYes}</option>
                    <option value="false">{t.form.waterNo}</option>
                  </select>
                </label>
                <label>{t.form.ppeItems}<input value={form.ppe_items} onChange={(event) => updateField("ppe_items", event.target.value)} placeholder={t.form.ppePh} /></label>
              </div>
            </fieldset>
            <fieldset>
              <legend><span>05</span> {t.form.exposureRecovery}</legend>
              <div className="form-grid">
                <label>{t.form.continuousExposure}<input type="number" min="0" max="1440" value={form.continuous_exposure_minutes} onChange={(event) => updateField("continuous_exposure_minutes", event.target.value)} /></label>
                <label>{t.form.breakFrequency}<input type="number" min="1" max="1440" value={form.break_frequency_minutes} onChange={(event) => updateField("break_frequency_minutes", event.target.value)} placeholder={t.form.optionalPh} /></label>
              </div>
            </fieldset>
            <button className="primary-button submit-button" type="submit" disabled={loading}>
              {loading ? <><span className="spinner" /> {t.form.analyzing}</> : <>{t.form.runAssessment} <ArrowRight size={17} /></>}
            </button>
            {error && <p className="error" role="alert"><AlertTriangle size={16} />{error}</p>}
          </form>

          <aside className="assessment-context panel">
            <div className="section-heading"><div><p className="overline">{t.context.overline}</p><h2>{t.context.title}</h2></div></div>
            <ul className="context-list">
              <li><CloudSun size={17} /><div><strong>{t.context.envObs}</strong><span>{t.context.envObsDesc}</span></div></li>
              <li><ClipboardList size={17} /><div><strong>{t.context.exposureFactors}</strong><span>{t.context.exposureFactorsDesc}</span></div></li>
              <li><ShieldCheck size={17} /><div><strong>{t.context.practicalControls}</strong><span>{t.context.practicalControlsDesc}</span></div></li>
              <li><Droplets size={17} /><div><strong>{t.nav.resources}</strong><span><Link href="/resources">{t.resources.findBtn}</Link></span></div></li>
            </ul>
            <div className="context-disclaimer"><Info size={16} /><p>{t.context.disclaimer}</p></div>
          </aside>
        </section>

        {assessment && (
          <>
            {alerts && alerts.alert_count ? (
              <section className="alerts-section">
                <div className="section-heading">
                  <div><p className="overline">{t.alerts.overline}</p><h2>{t.alerts.title}</h2></div>
                  <span className={`alert-priority-tag priority-${alerts.highest_priority}`}>{tr(t, alerts.highest_priority ?? "none")}</span>
                </div>
                {alerts.has_critical_precaution ? (
                  <div className="emergency-banner" role="alert">
                    <AlertTriangle size={20} aria-hidden="true" />
                    <div><strong>{t.alerts.emergencyHeading}</strong><span>{alerts.emergency_guidance}</span></div>
                  </div>
                ) : null}
                <div className="alerts-grid">
                  {(alerts.alerts ?? []).map((alert) => <AlertCard key={alert.id ?? alert.title} alert={alert} />)}
                </div>
                <p className="alerts-summary">{alerts.summary}</p>
                <details>
                  <summary>{t.alerts.viewLimitations}</summary>
                  <ul className="limitation-list">{(alerts.limitations ?? []).map((item) => <li key={item}>{item}</li>)}</ul>
                </details>
              </section>
            ) : null}
            <section className="results-section">
              <div className="section-heading">
                <div><p className="overline">{t.output.overline}</p><h2>{t.output.title}</h2></div>
                <span className="status-tag">{t.output.screeningOnly}</span>
              </div>
              <div className="results-grid">
                <article className="panel advisory-panel">
                  <div className="panel-title">
                    <span className="icon-box amber"><AlertTriangle size={17} /></span>
                    <div><p className="overline">{t.output.advisoryOverline}</p><h3>{t.output.advisoryTitle}</h3></div>
                  </div>
                  <div className="narrative">{assessment.safety_advisory || t.output.advisoryFallback}</div>
                </article>
                <article className="panel details-panel">
                  <p className="overline">{t.output.missingOverline}</p>
                  <h3>{missing.length ? t.output.itemsToCollect.replace("{count}", String(missing.length)) : t.output.profileComplete}</h3>
                  {missing.length ? (
                    <ul className="missing-list">{missing.map((item) => <li key={item}><AlertTriangle size={14} />{tr(t, item)}</li>)}</ul>
                  ) : (
                    <p className="panel-copy">{t.output.allFieldsSupplied}</p>
                  )}
                  <div className="notice success" style={{ marginTop: 16 }}><MapPin size={16} /><div><strong>{t.dashboard.overline}</strong><span><Link href="/dashboard">{t.dashboard.title}</Link></span></div></div>
                  <details><summary>{t.output.viewLimitations}</summary><ul className="limitation-list">{(deterministic?.limitations ?? []).map((item) => <li key={item}>{item}</li>)}</ul></details>
                </article>
              </div>
            </section>
          </>
        )}
        <footer><strong>{t.footer.label}</strong> {t.footer.note}</footer>
      </div>
    </AppShell>
  );
}
