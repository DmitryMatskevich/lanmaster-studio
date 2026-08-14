import React, { useEffect, useMemo, useState } from "react";
import ReactDOM from "react-dom/client";
import { Box, LogIn, RefreshCw, Search, ShieldCheck } from "lucide-react";

import type { ModelSummary, RevisionSummary, UserInfo } from "../../clients/typescript/src";
import { createStudioClient, type SessionState, type StudioRole } from "./api";
import "./styles.css";

const defaultSession: SessionState = {
  subject: "engineer@example.test",
  role: "engineer"
};

function App() {
  const [session, setSession] = useState<SessionState>(defaultSession);
  const [path, setPath] = useState(window.location.pathname);
  const client = useMemo(() => createStudioClient(session), [session]);

  useEffect(() => {
    const onPopState = () => setPath(window.location.pathname);
    window.addEventListener("popstate", onPopState);
    return () => window.removeEventListener("popstate", onPopState);
  }, []);

  function navigate(nextPath: string) {
    window.history.pushState({}, "", nextPath);
    setPath(nextPath);
  }

  const modelRoute = path.match(/^\/models\/([^/]+)$/);
  const page = path === "/" || path === "/models"
    ? <ModelListPage client={client} navigate={navigate} />
    : path === "/models/new"
      ? <NewModelPage client={client} navigate={navigate} />
      : modelRoute
        ? <ModelRoute client={client} modelId={decodeURIComponent(modelRoute[1])} />
        : <ModelListPage client={client} navigate={navigate} />;

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <Box size={22} aria-hidden="true" />
          <span>LANMASTER Studio</span>
        </div>
        <nav aria-label="Studio navigation">
          <button type="button" className="nav-link" onClick={() => navigate("/models")}>Модели</button>
          <button type="button" className="nav-link" onClick={() => navigate("/models/new")}>Новая модель</button>
        </nav>
      </aside>
      <main className="workspace">
        <AuthBar session={session} onChange={setSession} client={client} />
        {page}
      </main>
    </div>
  );
}

function AuthBar({
  session,
  onChange,
  client
}: {
  session: SessionState;
  onChange: (session: SessionState) => void;
  client: ReturnType<typeof createStudioClient>;
}) {
  const [user, setUser] = useState<UserInfo | null>(null);
  const [error, setError] = useState("");

  async function verify() {
    setError("");
    try {
      setUser(await client.me());
    } catch (err) {
      setUser(null);
      setError(err instanceof Error ? err.message : "Auth check failed");
    }
  }

  return (
    <header className="topbar">
      <label>
        Пользователь
        <input
          value={session.subject}
          onChange={(event) => onChange({ ...session, subject: event.target.value })}
        />
      </label>
      <label>
        Роль
        <select
          value={session.role}
          onChange={(event) => onChange({ ...session, role: event.target.value as StudioRole })}
        >
          <option value="engineer">engineer</option>
          <option value="viewer">viewer</option>
          <option value="admin">admin</option>
        </select>
      </label>
      <button type="button" onClick={verify} title="Проверить доступ">
        <ShieldCheck size={18} aria-hidden="true" />
        Проверить
      </button>
      {user && <span className="status ok">{user.displayName} · {user.roles.join(", ")}</span>}
      {error && <span className="status error">{error}</span>}
    </header>
  );
}

function ModelListPage({
  client,
  navigate
}: {
  client: ReturnType<typeof createStudioClient>;
  navigate: (path: string) => void;
}) {
  const [query, setQuery] = useState("");
  const [models, setModels] = useState<ModelSummary[]>([]);
  const [state, setState] = useState<"idle" | "loading" | "error">("idle");

  async function load(nextQuery = query) {
    setState("loading");
    try {
      const result = await client.listModels({ query: nextQuery || undefined, limit: 50 });
      setModels(result.items);
      setState("idle");
    } catch {
      setState("error");
    }
  }

  useEffect(() => {
    void load("");
  }, [client]);

  function submitSearch(event: React.FormEvent) {
    event.preventDefault();
    void load();
  }

  return (
    <section className="panel">
      <div className="panel-heading">
        <h1>Каталог моделей</h1>
        <form className="toolbar" onSubmit={submitSearch}>
          <label className="search">
            <Search size={16} aria-hidden="true" />
            <input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Артикул или имя" />
          </label>
          <button type="submit" title="Найти модели">
            <RefreshCw size={18} aria-hidden="true" />
            Найти
          </button>
        </form>
      </div>
      {state === "error" && <p className="message error">Не удалось загрузить модели.</p>}
      {state === "loading" && <p className="message">Загрузка...</p>}
      {state !== "loading" && models.length === 0 && <p className="message">Список пуст.</p>}
      <div className="table">
        {models.map((model) => (
          <button className="row" key={model.id} type="button" onClick={() => navigate(`/models/${model.id}`)}>
            <span>{model.article}</span>
            <span>{model.series || "-"}</span>
            <span>{model.status}</span>
            <span>{model.activeRevisionId || "-"}</span>
          </button>
        ))}
      </div>
    </section>
  );
}

function NewModelPage({
  client,
  navigate
}: {
  client: ReturnType<typeof createStudioClient>;
  navigate: (path: string) => void;
}) {
  const [article, setArticle] = useState("TWT-CBB-42U-6x10-P1");
  const [created, setCreated] = useState<ModelSummary | null>(null);
  const [error, setError] = useState("");

  async function createModel(event: React.FormEvent) {
    event.preventDefault();
    setError("");
    try {
      setCreated(await client.createModel({ article, manufacturer: "LANMASTER" }));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Create failed");
    }
  }

  return (
    <section className="panel narrow">
      <h1>Новая модель</h1>
      <form className="stack" onSubmit={createModel}>
        <label>
          Артикул
          <input value={article} onChange={(event) => setArticle(event.target.value)} required />
        </label>
        <button type="submit">
          <LogIn size={18} aria-hidden="true" />
          Создать
        </button>
      </form>
      {created && (
        <p className="message ok">
          <button type="button" className="text-link" onClick={() => navigate(`/models/${created.id}`)}>
            {created.article}
          </button>{" "}
          создана.
        </p>
      )}
      {error && <p className="message error">{error}</p>}
    </section>
  );
}

function ModelRoute({
  client,
  modelId
}: {
  client: ReturnType<typeof createStudioClient>;
  modelId: string;
}) {
  const [model, setModel] = useState<ModelSummary | null>(null);
  const [revisions, setRevisions] = useState<RevisionSummary[]>([]);
  const [selectedRevisionId, setSelectedRevisionId] = useState("");
  const [state, setState] = useState<"idle" | "loading" | "error">("idle");
  const [error, setError] = useState("");

  async function load() {
    setError("");
    setState("loading");
    try {
      const [loadedModel, loadedRevisions] = await Promise.all([
        client.getModel(modelId),
        client.listRevisions(modelId)
      ]);
      setModel(loadedModel);
      setRevisions(loadedRevisions.items);
      setSelectedRevisionId(loadedModel.activeRevisionId || loadedRevisions.items[0]?.id || "");
      setState("idle");
    } catch (err) {
      setState("error");
      setError(err instanceof Error ? err.message : "Model load failed");
    }
  }

  useEffect(() => {
    void load();
  }, [client, modelId]);

  return (
    <section className="panel">
      <div className="panel-heading">
        <h1>Маршрут модели</h1>
        <button type="button" onClick={load} title="Загрузить модель">
          <RefreshCw size={18} aria-hidden="true" />
          Загрузить
        </button>
      </div>
      {model && (
        <div className="model-layout">
          <dl className="details">
            <dt>ID</dt><dd>{model.id}</dd>
            <dt>Артикул</dt><dd>{model.article}</dd>
            <dt>Производитель</dt><dd>{model.manufacturer}</dd>
            <dt>Статус</dt><dd>{model.status}</dd>
            <dt>Active revision</dt><dd>{model.activeRevisionId || "-"}</dd>
          </dl>
          <section className="selector-panel" aria-label="Revision selector">
            <h2>Revision selector</h2>
            {revisions.length > 0 ? (
              <label>
                Ревизия
                <select value={selectedRevisionId} onChange={(event) => setSelectedRevisionId(event.target.value)}>
                  {revisions.map((revision) => (
                    <option value={revision.id} key={revision.id}>
                      {revision.id} · {revision.contentHash.slice(0, 18)}
                    </option>
                  ))}
                </select>
              </label>
            ) : (
              <p className="message">У модели пока нет ревизий.</p>
            )}
          </section>
        </div>
      )}
      {state === "loading" && <p className="message">Загрузка модели...</p>}
      {!model && state === "idle" && <p className="message">Модель не выбрана.</p>}
      {error && <p className="message error">{error}</p>}
    </section>
  );
}

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
