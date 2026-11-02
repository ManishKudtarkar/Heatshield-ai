"use client";

import { FormEvent, useState } from "react";
import { AppShell, API_URL } from "@/components/AppShell";
import { useI18n } from "@/lib/i18n";
import {
  Activity,
  AlertTriangle,
  ArrowRight,
  CheckCircle2,
  ClipboardList,
  CloudSun,
  Droplets,
  Gauge,
  HeartPulse,
  Home as HomeIcon,
  Info,
  MapPin,
  Menu,
  ShieldCheck,
  Sun,
  Thermometer,
  Wind,
  X,
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

function label(value: string) {
  return value.replaceAll("_", " ").replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function display(value: unknown) {
  if (typeof value === "boolean") return value ? "Yes" : "No";
  if (value === null || value === undefined || value === "") return "Not provided";
  if (Array.isArray(value)) return value.join(", ") || "None reported";
  return String(value);
}

function Metric({ icon: Icon, name, value, unit, context }: { icon: typeof Thermometer; name: string; value: unknown; unit?: string; context: string }) {
  return <article className="metric-card"><div className="metric-label"><Icon size={16} aria-hidden="true" />{name}</div><div className="metric-value">{display(value)}<small>{unit}</small></div><p>{context}</p></article>;
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
        <span className={`alert-priority-tag priority-${priority}`}>{label(priority)}</span>
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

export default function Home() {
  const [form, setForm] = useState(initialForm);
  const [assessment, setAssessment] = useState<AssessmentResult | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [mobileNav, setMobileNav] = useState(false);

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
        body: JSON.stringify({ location: form.location, worker }),
      });
      const data = (await response.json()) as AssessmentResponse;
      if (!response.ok || !data.success || !data.result) {
        const detail = typeof data.detail === "string" ? data.detail : data.detail?.message;
        throw new Error(detail || "The assessment could not be completed.");
      }
      setAssessment(data.result);
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Unable to connect to the HeatShield API.");
    } finally {
      setLoading(false);
    }
  }

  const deterministic = assessment?.deterministic_assessment;
  const weather = deterministic?.weather_summary;
  const missing = deterministic?.missing_information ?? [];
  const alerts = assessment?.safety_alerts;

  return (
    <div className="app-shell">
      {mobileNav && <button className="nav-scrim" aria-label="Close navigation" onClick={() => setMobileNav(false)} />}
      <aside className={`sidebar ${mobileNav ? "sidebar-open" : ""}`}>
        <div className="brand"><div className="brand-mark"><Sun size={18} /></div><div><strong>HeatShield</strong><span>AI</span></div>{mobileNav && <button className="close-nav" onClick={() => setMobileNav(false)} aria-label="Close navigation"><X size={20} /></button>}</div>
        <div className="workspace-label">WORKSPACE</div>
        <nav aria-label="Primary navigation">
          <a className="nav-item active" href="#overview" onClick={() => setMobileNav(false)}><HomeIcon size={17} />Overview</a>
          <a className="nav-item" href="#new-assessment" onClick={() => setMobileNav(false)}><ClipboardList size={17} />New assessment</a>
          <span className="nav-item planned"><Activity size={17} />Assessments <em>Planned</em></span>
          <span className="nav-item planned"><ShieldCheck size={17} />Safety guidance <em>Planned</em></span>
          <span className="nav-item planned"><Droplets size={17} />Resources <em>Planned</em></span>
        </nav>
        <div className="sidebar-bottom"><div className="source-note"><CloudSun size={16} /><div><strong>Data source</strong><span>Open-Meteo</span></div></div><p>Environmental observations are not worksite measurements.</p></div>
      </aside>

      <main className="main-content">
        <header className="topbar"><button className="mobile-menu" onClick={() => setMobileNav(true)} aria-label="Open navigation"><Menu size={21} /></button><div className="location-context"><MapPin size={16} /><strong>{weather?.location ?? form.location}</strong><span>•</span><span>{weather?.country ?? "India"}</span></div><div className="topbar-right"><span className="observation-status"><span /> Observations available</span><div className="avatar">HS</div></div></header>

        <div className="content-wrap" id="overview">
          <section className="page-heading"><div><p className="overline">CLIMATE OPERATIONS / OVERVIEW</p><h1>Worker heat safety</h1><p>Understand current conditions, reported exposure, and the next practical action.</p></div><a className="primary-button heading-action" href="#new-assessment"><ClipboardList size={17} /> New assessment</a></section>

          <section className="section-block"><div className="section-heading"><div><p className="overline">ENVIRONMENTAL CONDITIONS</p><h2>Current observations</h2></div>{weather?.timestamp && <span className="timestamp">Observed {weather.timestamp.replace("T", " ")}</span>}</div>
            <div className="metrics-grid">
              <Metric icon={Thermometer} name="Air temperature" value={weather?.temperature_c} unit="°C" context="Current observation" />
              <Metric icon={Gauge} name="Relative humidity" value={weather?.humidity_percent} unit="%" context="Current observation" />
              <Metric icon={Sun} name="Apparent temperature" value={weather?.apparent_temperature_c} unit="°C" context="Not measured WBGT" />
              <Metric icon={Wind} name="Wind speed" value={weather?.wind_speed_kmh} unit="km/h" context="Current observation" />
            </div>
            {weather?.data_note && <p className="data-note"><Info size={15} />{weather.data_note}</p>}
          </section>

          <section className="overview-grid">
            <article className="panel status-panel"><div className="panel-title"><span className="icon-box teal"><CheckCircle2 size={17} /></span><div><p className="overline">ASSESSMENT STATUS</p><h3>{deterministic ? label(deterministic.assessment_status ?? "screening_only") : "Ready to assess"}</h3></div></div><p className="panel-copy">{deterministic ? "Screening completed from environmental observations and the reported worker profile." : "Complete a worker profile to generate a transparent heat-exposure screening assessment."}</p>{deterministic && missing.length > 0 ? <div className="notice warning"><AlertTriangle size={16} /><div><strong>Information to collect</strong><span>{missing.map(label).join(" • ")}</span></div></div> : <div className="notice success"><CheckCircle2 size={16} /><div><strong>Ready for input</strong><span>No assessment has been submitted yet.</span></div></div>}</article>
            <article className="panel context-panel"><div className="panel-title"><span className="icon-box amber"><HeartPulse size={17} /></span><div><p className="overline">LATEST WORKER ASSESSMENT</p><h3>{deterministic ? (deterministic.worker_summary?.occupation as string) : "No assessment yet"}</h3></div></div>{deterministic?.worker_summary ? <div className="worker-facts"><span><strong>{display(deterministic.worker_summary.workload)}</strong> Workload</span><span><strong>{display(deterministic.worker_summary.direct_sunlight)}</strong> Direct sunlight</span><span><strong>{display(deterministic.worker_summary.shade_availability)}</strong> Shade</span><span><strong>{display(deterministic.worker_summary.water_access)}</strong> Water access</span></div> : <p className="panel-copy">Reported work conditions will be summarized here after an assessment.</p>}</article>
          </section>

          <section className="assessment-layout" id="new-assessment">
            <form className="assessment-form panel" onSubmit={submitAssessment}>
              <div className="section-heading"><div><p className="overline">NEW ASSESSMENT</p><h2>Worker and worksite information</h2></div><span className="required-note">* Required</span></div>
              <fieldset><legend><span>01</span> Worksite</legend><div className="form-grid"><label>Location *<input required value={form.location} onChange={(event) => updateField("location", event.target.value)} placeholder="City or worksite" /></label><label>Work area<input value={form.work_area} onChange={(event) => updateField("work_area", event.target.value)} placeholder="Describe the worksite" /></label></div></fieldset>
              <fieldset><legend><span>02</span> Worker profile</legend><div className="form-grid"><label>Occupation *<input required value={form.occupation} onChange={(event) => updateField("occupation", event.target.value)} /></label><label>Shift duration (hours) *<input required type="number" min="0.1" max="24" step="0.1" value={form.shift_hours} onChange={(event) => updateField("shift_hours", event.target.value)} /></label><label>Workload *<select value={form.workload} onChange={(event) => updateField("workload", event.target.value)}><option value="light">Light</option><option value="moderate">Moderate</option><option value="heavy">Heavy</option><option value="very_heavy">Very heavy</option><option value="unknown">Unknown</option></select></label><label>Acclimatization *<select value={form.acclimatization} onChange={(event) => updateField("acclimatization", event.target.value)}><option value="acclimatized">Acclimatized</option><option value="not_acclimatized">Not acclimatized</option><option value="unknown">Unknown</option></select></label></div></fieldset>
              <fieldset><legend><span>03</span> Environmental exposure</legend><div className="form-grid"><label>Direct sunlight *<select value={String(form.direct_sunlight)} onChange={(event) => updateField("direct_sunlight", event.target.value === "true")}><option value="true">Yes — direct exposure</option><option value="false">No direct exposure</option></select></label><label>Shade availability *<select value={form.shade_availability} onChange={(event) => updateField("shade_availability", event.target.value)}><option value="full">Full</option><option value="partial">Partial</option><option value="none">None</option><option value="unknown">Unknown</option></select></label></div></fieldset>
              <fieldset><legend><span>04</span> Safety provisions</legend><div className="form-grid"><label>Drinking water access *<select value={String(form.water_access)} onChange={(event) => updateField("water_access", event.target.value === "true")}><option value="true">Available</option><option value="false">Not available</option></select></label><label>PPE items<input value={form.ppe_items} onChange={(event) => updateField("ppe_items", event.target.value)} placeholder="Separate items with commas" /></label></div></fieldset>
              <fieldset><legend><span>05</span> Exposure and recovery</legend><div className="form-grid"><label>Continuous exposure (minutes)<input type="number" min="0" max="1440" value={form.continuous_exposure_minutes} onChange={(event) => updateField("continuous_exposure_minutes", event.target.value)} /></label><label>Break frequency (minutes)<input type="number" min="1" max="1440" value={form.break_frequency_minutes} onChange={(event) => updateField("break_frequency_minutes", event.target.value)} placeholder="Optional" /></label></div></fieldset>
              <button className="primary-button submit-button" type="submit" disabled={loading}>{loading ? <><span className="spinner" /> Analyzing conditions...</> : <>Run heat assessment <ArrowRight size={17} /></>}</button>{error && <p className="error" role="alert"><AlertTriangle size={16} />{error}</p>}
            </form>

            <aside className="assessment-context panel"><div className="section-heading"><div><p className="overline">ASSESSMENT CONTEXT</p><h2>What you&apos;ll receive</h2></div></div><ul className="context-list"><li><CloudSun size={17} /><div><strong>Environmental observations</strong><span>Current temperature, humidity, apparent temperature, and wind from Open-Meteo.</span></div></li><li><ClipboardList size={17} /><div><strong>Exposure factors</strong><span>A transparent summary of the reported work conditions and what is missing.</span></div></li><li><ShieldCheck size={17} /><div><strong>Practical controls</strong><span>Safety guidance grounded in the assessment, with its limitations clearly stated.</span></div></li></ul><div className="context-disclaimer"><Info size={16} /><p>Apparent temperature is not WBGT. This tool provides screening support, not a medical diagnosis or a worksite measurement.</p></div></aside>
          </section>

          {assessment && (
            <>
              {alerts && alerts.alert_count ? (
                <section className="alerts-section">
                  <div className="section-heading">
                    <div>
                      <p className="overline">PROACTIVE SAFETY ALERTS</p>
                      <h2>Safety alerts</h2>
                    </div>
                    <span className={`alert-priority-tag priority-${alerts.highest_priority}`}>{label(alerts.highest_priority ?? "none")}</span>
                  </div>
                  {alerts.has_critical_precaution ? (
                    <div className="emergency-banner" role="alert">
                      <AlertTriangle size={20} aria-hidden="true" />
                      <div>
                        <strong>Seek emergency medical assistance if needed</strong>
                        <span>{alerts.emergency_guidance}</span>
                      </div>
                    </div>
                  ) : null}
                  <div className="alerts-grid">
                    {(alerts.alerts ?? []).map((alert) => <AlertCard key={alert.id ?? alert.title} alert={alert} />)}
                  </div>
                  <p className="alerts-summary">{alerts.summary}</p>
                  <details>
                    <summary>View alert limitations</summary>
                    <ul className="limitation-list">{(alerts.limitations ?? []).map((item) => <li key={item}>{item}</li>)}</ul>
                  </details>
                </section>
              ) : null}
              <section className="results-section"><div className="section-heading"><div><p className="overline">ASSESSMENT OUTPUT</p><h2>What to do next</h2></div><span className="status-tag">Screening only</span></div><div className="results-grid"><article className="panel advisory-panel"><div className="panel-title"><span className="icon-box amber"><AlertTriangle size={17} /></span><div><p className="overline">SAFETY ADVISORY</p><h3>Recommended guidance</h3></div></div><div className="narrative">{assessment.safety_advisory || "No advisory was returned."}</div></article><article className="panel details-panel"><p className="overline">MISSING INFORMATION</p><h3>{missing.length ? `${missing.length} item${missing.length === 1 ? "" : "s"} to collect` : "Profile complete"}</h3>{missing.length ? <ul className="missing-list">{missing.map((item) => <li key={item}><AlertTriangle size={14} />{label(item)}</li>)}</ul> : <p className="panel-copy">All tracked worker profile fields were supplied.</p>}<details><summary>View assessment limitations</summary><ul className="limitation-list">{(deterministic?.limitations ?? []).map((item) => <li key={item}>{item}</li>)}</ul></details></article></div></section>
            </>
          )}
          <footer><strong>Safety note:</strong> If someone shows confusion, seizures, collapse, or loss of consciousness, seek immediate emergency medical assistance. Do not delay for an AI assessment.</footer>
        </div>
      </main>
    </div>
  );
}
