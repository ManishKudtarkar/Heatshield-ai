"use client";

import { useCallback, useEffect, useState } from "react";
import { AppShell, API_URL } from "@/components/AppShell";
import { useI18n } from "@/lib/i18n";
import {
  AlertTriangle,
  ArrowLeft,
  BookOpenCheck,
  ExternalLink,
  LibraryBig,
  Search,
  ShieldCheck,
} from "lucide-react";

type TopicIndexEntry = {
  id: string;
  title: string;
  category: string;
  validated: boolean;
  reviewed_at: string;
  source_count: number;
};

type TopicDetail = {
  id: string;
  title: string;
  category: string;
  summary: string;
  guidance: string[];
  sources: { name: string; url: string }[];
  validated: boolean;
  reviewed_at: string;
  language: string;
  relevance_score?: number;
};

type TopicLike = TopicDetail | TopicIndexEntry;

function isDetail(topic: TopicLike): topic is TopicDetail {
  return "summary" in topic && Array.isArray((topic as TopicDetail).guidance);
}

export default function GuidancePage() {
  const { t, lang } = useI18n();
  const [topics, setTopics] = useState<TopicIndexEntry[]>([]);
  const [kbVersion, setKbVersion] = useState("");
  const [integrityOk, setIntegrityOk] = useState(false);
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<TopicDetail[] | null>(null);
  const [selected, setSelected] = useState<TopicDetail | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const loadIndex = useCallback(async () => {
    setError("");
    try {
      const [indexRes, validateRes] = await Promise.all([
        fetch(`${API_URL}/api/v1/knowledge/topics`),
        fetch(`${API_URL}/api/v1/knowledge/validate`),
      ]);
      if (!indexRes.ok) throw new Error(t.guidance.loadError);
      const index = (await indexRes.json()) as { success: boolean; kb_version: string; topics: TopicIndexEntry[] };
      setTopics(index.topics ?? []);
      setKbVersion(index.kb_version ?? "");
      if (validateRes.ok) {
        const validation = (await validateRes.json()) as { success: boolean };
        setIntegrityOk(Boolean(validation.success));
      }
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : t.guidance.loadError);
    }
  }, [t.guidance.loadError]);

  useEffect(() => {
    void loadIndex();
  }, [loadIndex]);

  async function openTopic(topicId: string) {
    setLoading(true);
    setError("");
    try {
      const response = await fetch(`${API_URL}/api/v1/knowledge/topics/${topicId}?language=${lang}`);
      if (!response.ok) throw new Error(t.guidance.loadError);
      const data = (await response.json()) as { success: boolean; topic: TopicDetail };
      setSelected(data.topic);
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : t.guidance.loadError);
    } finally {
      setLoading(false);
    }
  }

  // Re-fetch the open topic when the worker switches language.
  useEffect(() => {
    if (selected) void openTopic(selected.id);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [lang]);

  async function runSearch(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const term = query.trim();
    if (term.length < 2) return;
    setLoading(true);
    setError("");
    setSelected(null);
    try {
      const response = await fetch(`${API_URL}/api/v1/knowledge/search?q=${encodeURIComponent(term)}&language=${lang}`);
      if (!response.ok) throw new Error(t.guidance.loadError);
      const data = (await response.json()) as { success: boolean; results: TopicDetail[] };
      setResults(data.results ?? []);
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : t.guidance.loadError);
    } finally {
      setLoading(false);
    }
  }

  function browseAll() {
    setResults(null);
    setSelected(null);
    setQuery("");
  }

  const listItems: TopicLike[] | null = results;
  const displayList: TopicLike[] = listItems ?? topics;

  return (
    <AppShell>
      <div className="content-wrap">
        <section className="page-heading">
          <div>
            <p className="overline">{t.guidance.overline}</p>
            <h1>{t.guidance.title}</h1>
            <p>{t.guidance.subtitle}</p>
          </div>
          {integrityOk && (
            <span className="status-tag integrity-tag">
              <ShieldCheck size={12} /> {t.guidance.integrityOk}
            </span>
          )}
        </section>

        <section className="section-block">
          <form className="kb-search" onSubmit={runSearch}>
            <Search size={16} aria-hidden="true" />
            <input
              value={query}
              onChange={(event) => setQuery(event.target.value)}
              placeholder={t.guidance.searchPh}
              aria-label={t.guidance.searchBtn}
            />
            <button className="primary-button" type="submit" disabled={loading || query.trim().length < 2}>
              {t.guidance.searchBtn}
            </button>
          </form>
          <div className="kb-meta">
            <span><LibraryBig size={14} /> {t.guidance.kbVersion}: v{kbVersion || "—"}</span>
            <span>{t.guidance.resultsCount.replace("{count}", String(displayList.length))}</span>
            {(results !== null || selected) && (
              <button className="link-button" onClick={browseAll}>{t.guidance.browseAll}</button>
            )}
          </div>
          {error && <p className="error" role="alert"><AlertTriangle size={16} />{error}</p>}
        </section>

        {selected ? (
          <section className="panel topic-detail">
            <button className="link-button" onClick={() => setSelected(null)}>
              <ArrowLeft size={14} /> {t.guidance.backToList}
            </button>
            <div className="topic-head">
              <h2>{selected.title}</h2>
              <div className="topic-tags">
                <span className="alert-priority-tag priority-advisory">{t.guidance.category}: {selected.category}</span>
                {selected.validated && (
                  <span className="alert-priority-tag priority-none">
                    <BookOpenCheck size={12} /> {t.guidance.validated} · {t.guidance.reviewed}: {selected.reviewed_at}
                  </span>
                )}
              </div>
            </div>
            <p className="panel-copy topic-summary">{selected.summary}</p>
            <h3 className="topic-subheading">{t.guidance.guidanceHeading}</h3>
            <ul className="alert-guidance">
              {(selected.guidance ?? []).map((item, index) => <li key={index}>{item}</li>)}
            </ul>
            <h3 className="topic-subheading">{t.guidance.sources}</h3>
            <ul className="source-list">
              {(selected.sources ?? []).map((source) => (
                <li key={source.url}>
                  <ExternalLink size={13} />
                  <a href={source.url} target="_blank" rel="noopener noreferrer">{source.name}</a>
                </li>
              ))}
            </ul>
          </section>
        ) : (
          <section className="alerts-grid">
            {displayList.map((topic) => (
              <article className="alert-card alert-advisory topic-card" key={topic.id}>
                <div className="alert-head">
                  <span className="alert-icon advisory"><ShieldCheck size={16} /></span>
                  <h3>{topic.title}</h3>
                </div>
                <div className="topic-card-meta">
                  <span>{t.guidance.category}: {topic.category}</span>
                  <span>
                    {t.guidance.validated}{topic.validated ? " ✓" : ""} · {t.guidance.reviewed}: {topic.reviewed_at}
                  </span>
                  <span>
                    {t.guidance.sources}: {isDetail(topic) ? topic.sources.length : topic.source_count}
                  </span>
                </div>
                {isDetail(topic) && topic.summary ? <p className="panel-copy topic-excerpt">{topic.summary}</p> : null}
                <button className="primary-button topic-open" onClick={() => void openTopic(topic.id)}>
                  {t.guidance.guidanceHeading} →
                </button>
              </article>
            ))}
            {listItems !== null && listItems.length === 0 && <p className="panel-copy">{t.guidance.noResults}</p>}
          </section>
        )}

        <footer><strong>{t.footer.label}</strong> {t.footer.note}</footer>
      </div>
    </AppShell>
  );
}
