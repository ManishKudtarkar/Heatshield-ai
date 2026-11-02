"use client";

import { useCallback, useEffect, useState } from "react";
import { AppShell, API_URL } from "@/components/AppShell";
import { useI18n } from "@/lib/i18n";
import type { Strings } from "@/lib/translations";
import {
  AlertTriangle,
  BarChart3,
  CheckCircle2,
  RefreshCw,
  Siren,
  Trash2,
} from "lucide-react";

type RiskCounts = { critical: number; heightened: number; advisory: number; none: number };

type RecentAssessment = {
  assessment_id: string;
  worker_name: string;
  location: string;
  work_area: string;
  occupation: string;
  risk_level: string;
  highest_priority: string;
  alert_count: number;
  temperature_c: number | null;
  submitted_at: string;
  missing_information_count: number;
};

type LocationGroup = {
  location: string;
  assessment_count: number;
  worst_risk_level: string;
  max_temperature_c: number | null;
  workers_with_incomplete_profiles: number;
};

type Overview = {
  total_assessments: number;
  unusable_records: number;
  risk_counts: RiskCounts;
  critical_share: number;
  urgent_cases: RecentAssessment[];
  locations: LocationGroup[];
  profile_completeness: { assessments_with_missing_information: number; complete_profile_share: number | null };
  recent_assessments: RecentAssessment[];
  limitations: string[];
};

function tr(t: Strings, key: string): string {
  return t.enums.priority[key] ?? t.enums.assessmentStatus[key] ?? key.replaceAll("_", " ");
}

export default function DashboardPage() {
  const { t } = useI18n();
  const [overview, setOverview] = useState<Overview | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const [cleared, setCleared] = useState(false);

  const load = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const response = await fetch(`${API_URL}/api/v1/supervisor/overview`);
      if (!response.ok) throw new Error(t.dashboard.loadError);
      const data = (await response.json()) as { success: boolean; overview: Overview };
      setOverview(data.overview);
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : t.dashboard.loadError);
    } finally {
      setLoading(false);
    }
  }, [t.dashboard.loadError]);

  useEffect(() => {
    void load();
  }, [load]);

  async function clearRecords() {
    if (!window.confirm(t.dashboard.clearConfirm)) return;
    try {
      const response = await fetch(`${API_URL}/api/v1/supervisor/records`, { method: "DELETE" });
      if (response.ok) {
        setCleared(true);
        await load();
      } else {
        setError(t.dashboard.loadError);
      }
    } catch {
      setError(t.dashboard.loadError);
    }
  }

  const stats = [
    { label: t.dashboard.total, value: overview?.total_assessments ?? 0, tone: "" },
    { label: t.dashboard.critical, value: overview?.risk_counts.critical ?? 0, tone: "stat-critical" },
    { label: t.dashboard.heightened, value: overview?.risk_counts.heightened ?? 0, tone: "stat-heightened" },
    { label: t.dashboard.advisory, value: overview?.risk_counts.advisory ?? 0, tone: "stat-advisory" },
    { label: t.dashboard.noneRisk, value: overview?.risk_counts.none ?? 0, tone: "" },
  ];

  return (
    <AppShell>
      <div className="content-wrap">
        <section className="page-heading">
          <div>
            <p className="overline">{t.dashboard.overline}</p>
            <h1>{t.dashboard.title}</h1>
            <p>{t.dashboard.subtitle}</p>
          </div>
          <div className="heading-actions">
            <button className="primary-button" onClick={() => void load()} disabled={loading}>
              <RefreshCw size={15} /> {t.dashboard.refresh}
            </button>
            <button className="danger-button" onClick={() => void clearRecords()}>
              <Trash2 size={15} /> {t.dashboard.clear}
            </button>
          </div>
        </section>

        {cleared && !error && (
          <div className="notice success" style={{ marginBottom: 20 }}><CheckCircle2 size={16} /><div><span>{t.dashboard.cleared}</span></div></div>
        )}
        {error && <p className="error" role="alert"><AlertTriangle size={16} />{error}</p>}

        {overview && (
          <>
            <section className="metrics-grid stats-grid">
              {stats.map((stat) => (
                <article key={stat.label} className={`metric-card ${stat.tone}`}>
                  <div className="metric-label"><BarChart3 size={16} aria-hidden="true" />{stat.label}</div>
                  <div className="metric-value">{stat.value}</div>
                </article>
              ))}
            </section>

            {(overview.unusable_records > 0 || overview.profile_completeness.complete_profile_share !== null) && (
              <section className="kb-meta" style={{ margin: "14px 0 26px" }}>
                {overview.unusable_records > 0 && <span>{t.dashboard.unusable}: {overview.unusable_records}</span>}
                {overview.profile_completeness.complete_profile_share !== null && (
                  <span>{t.dashboard.completeShare}: {Math.round(overview.profile_completeness.complete_profile_share * 100)}%</span>
                )}
                <span>{t.dashboard.incomplete}: {overview.profile_completeness.assessments_with_missing_information}</span>
              </section>
            )}

            <section className="section-block">
              <div className="section-heading"><div><h2><Siren size={17} style={{ verticalAlign: -3, marginRight: 8, color: "var(--danger)" }} />{t.dashboard.urgentHeading}</h2></div></div>
              {overview.urgent_cases.length === 0 ? (
                <p className="panel-copy">{t.dashboard.noUrgent}</p>
              ) : (
                <div className="alerts-grid">
                  {overview.urgent_cases.map((urgent) => (
                    <article className="alert-card alert-critical_precaution" key={urgent.assessment_id}>
                      <div className="alert-head">
                        <span className="alert-icon critical"><AlertTriangle size={16} /></span>
                        <h3>{urgent.worker_name}</h3>
                        <span className="alert-priority-tag priority-critical_precaution">{tr(t, urgent.highest_priority)}</span>
                      </div>
                      <div className="topic-card-meta">
                        <span>{urgent.location}{urgent.work_area !== "Not provided" ? ` · ${urgent.work_area}` : ""}</span>
                        <span>{t.dashboard.tempCol}: {urgent.temperature_c ?? "—"} °C · {t.dashboard.alertsCol}: {urgent.alert_count}</span>
                      </div>
                    </article>
                  ))}
                </div>
              )}
            </section>

            <section className="section-block">
              <div className="section-heading"><div><h2>{t.dashboard.locationsHeading}</h2></div></div>
              {overview.locations.length === 0 ? (
                <p className="panel-copy">{t.dashboard.empty}</p>
              ) : (
                <div className="table-wrap panel">
                  <table className="data-table">
                    <thead>
                      <tr>
                        <th>{t.dashboard.locationCol}</th>
                        <th>{t.dashboard.assessmentsCol}</th>
                        <th>{t.dashboard.worstCol}</th>
                        <th>{t.dashboard.maxTempCol}</th>
                        <th>{t.dashboard.incomplete}</th>
                      </tr>
                    </thead>
                    <tbody>
                      {overview.locations.map((location) => (
                        <tr key={location.location}>
                          <td>{location.location}</td>
                          <td>{location.assessment_count}</td>
                          <td><span className={`alert-priority-tag priority-${location.worst_risk_level === "critical" ? "critical_precaution" : location.worst_risk_level === "heightened" ? "heightened_precaution" : location.worst_risk_level}`}>{tr(t, location.worst_risk_level)}</span></td>
                          <td>{location.max_temperature_c ?? "—"} °C</td>
                          <td>{location.workers_with_incomplete_profiles}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </section>

            <section className="section-block">
              <div className="section-heading"><div><h2>{t.dashboard.recentHeading}</h2></div></div>
              {overview.recent_assessments.length === 0 ? (
                <p className="panel-copy">{t.dashboard.empty}</p>
              ) : (
                <div className="table-wrap panel">
                  <table className="data-table">
                    <thead>
                      <tr>
                        <th>{t.dashboard.worker}</th>
                        <th>{t.dashboard.locationCol}</th>
                        <th>{t.dashboard.riskCol}</th>
                        <th>{t.dashboard.tempCol}</th>
                        <th>{t.dashboard.timeCol}</th>
                      </tr>
                    </thead>
                    <tbody>
                      {overview.recent_assessments.map((entry) => (
                        <tr key={entry.assessment_id}>
                          <td>{entry.worker_name}</td>
                          <td>{entry.location}</td>
                          <td><span className={`alert-priority-tag priority-${entry.highest_priority}`}>{tr(t, entry.highest_priority)}</span></td>
                          <td>{entry.temperature_c ?? "—"} °C</td>
                          <td>{entry.submitted_at.replace("T", " ").slice(0, 19)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </section>

            <section className="section-block">
              <details>
                <summary>{t.dashboard.limitationsHeading}</summary>
                <ul className="limitation-list">{overview.limitations.map((item) => <li key={item}>{item}</li>)}</ul>
              </details>
            </section>
          </>
        )}

        {!overview && loading && <p className="panel-copy"><span className="spinner" /></p>}

        <footer><strong>{t.footer.label}</strong> {t.footer.note}</footer>
      </div>
    </AppShell>
  );
}
