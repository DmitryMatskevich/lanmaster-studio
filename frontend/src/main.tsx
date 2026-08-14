import React, { useEffect, useMemo, useRef, useState } from "react";
import ReactDOM from "react-dom/client";
import { Box, ChevronRight, Eye, Focus, Layers, LogIn, RefreshCw, Ruler, Scissors, Search, ShieldCheck } from "lucide-react";
import * as THREE from "three";

import type { DraftSummary, JobSummary, ModelSummary, RevisionSummary, UserInfo } from "../../clients/typescript/src";
import { createStudioClient, type SessionState, type StudioRole } from "./api";
import "./styles.css";

const defaultSession: SessionState = {
  subject: "engineer@example.test",
  role: "engineer"
};

interface TreeNode {
  id: string;
  label: string;
  children?: TreeNode[];
}

interface FlatTreeNode {
  id: string;
  label: string;
  depth: number;
  hasChildren: boolean;
}

interface PropertyField {
  key: string;
  label: string;
  unit: string;
  min: number;
  max: number;
  value: number;
  sourceStatus: "documented" | "estimated" | "missing";
}

const TREE_ROW_HEIGHT = 32;
const TREE_VIEWPORT_HEIGHT = 384;
const TREE_OVERSCAN = 6;

function buildDemoTree(totalNodes = 1000): TreeNode[] {
  const roots: TreeNode[] = [];
  let index = 0;
  while (index < totalNodes) {
    const root: TreeNode = { id: `cmp_${index}`, label: `Assembly ${index + 1}`, children: [] };
    index += 1;
    for (let child = 0; child < 9 && index < totalNodes; child += 1) {
      const childNode: TreeNode = { id: `cmp_${index}`, label: `Component ${index + 1}`, children: [] };
      index += 1;
      for (let leaf = 0; leaf < 9 && index < totalNodes; leaf += 1) {
        childNode.children?.push({ id: `cmp_${index}`, label: `Part ${index + 1}` });
        index += 1;
      }
      root.children?.push(childNode);
    }
    roots.push(root);
  }
  return roots;
}

function flattenTree(nodes: TreeNode[], depth = 0): FlatTreeNode[] {
  return nodes.flatMap((node) => [
    {
      id: node.id,
      label: node.label,
      depth,
      hasChildren: Boolean(node.children?.length)
    },
    ...flattenTree(node.children || [], depth + 1)
  ]);
}

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
  const [selectedComponentId, setSelectedComponentId] = useState("cmp_0");
  const [viewerMode, setViewerMode] = useState<ViewerMode>("visible");
  const [properties, setProperties] = useState<PropertyField[]>([
    { key: "width", label: "Width", unit: "mm", min: 600, max: 800, value: 600, sourceStatus: "documented" },
    { key: "depth", label: "Depth", unit: "mm", min: 600, max: 1200, value: 1000, sourceStatus: "documented" },
    { key: "railOffset", label: "Rail offset", unit: "mm", min: 0, max: 200, value: 100, sourceStatus: "estimated" }
  ]);
  const [baselineProperties, setBaselineProperties] = useState<PropertyField[]>(properties);
  const [undoStack, setUndoStack] = useState<PropertyField[][]>([]);
  const [redoStack, setRedoStack] = useState<PropertyField[][]>([]);
  const [previewState, setPreviewState] = useState<PreviewState>({ status: "idle" });

  function updateProperties(next: PropertyField[]) {
    setUndoStack((items) => [...items, properties]);
    setRedoStack([]);
    setProperties(next);
  }

  function undoProperties() {
    const previous = undoStack.at(-1);
    if (!previous) return;
    setRedoStack((items) => [...items, properties]);
    setUndoStack((items) => items.slice(0, -1));
    setProperties(previous);
  }

  function redoProperties() {
    const next = redoStack.at(-1);
    if (!next) return;
    setUndoStack((items) => [...items, properties]);
    setRedoStack((items) => items.slice(0, -1));
    setProperties(next);
  }
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
          <VirtualizedTree
            nodes={buildDemoTree(1000)}
            selectedId={selectedComponentId}
            onSelect={setSelectedComponentId}
          />
          <ModelViewer
            selectedRevisionId={selectedRevisionId}
            selectedComponentId={selectedComponentId}
            viewerMode={viewerMode}
            onModeChange={setViewerMode}
            onSelectComponent={setSelectedComponentId}
          />
          <PropertyEditor fields={properties} onChange={updateProperties} />
          <PreviewWorkflow
            client={client}
            model={model}
            properties={properties}
            state={previewState}
            onStateChange={setPreviewState}
          />
          <DiffQaPanel
            before={baselineProperties}
            after={properties}
            onAcceptBaseline={() => setBaselineProperties(properties)}
            onUndo={undoProperties}
            onRedo={redoProperties}
            canUndo={undoStack.length > 0}
            canRedo={redoStack.length > 0}
          />
        </div>
      )}
      {state === "loading" && <p className="message">Загрузка модели...</p>}
      {!model && state === "idle" && <p className="message">Модель не выбрана.</p>}
      {error && <p className="message error">{error}</p>}
    </section>
  );
}

function DiffQaPanel({
  before,
  after,
  onAcceptBaseline,
  onUndo,
  onRedo,
  canUndo,
  canRedo
}: {
  before: PropertyField[];
  after: PropertyField[];
  onAcceptBaseline: () => void;
  onUndo: () => void;
  onRedo: () => void;
  canUndo: boolean;
  canRedo: boolean;
}) {
  const diffs = after
    .map((field) => {
      const oldField = before.find((item) => item.key === field.key);
      return oldField && oldField.value !== field.value ? { key: field.key, label: field.label, before: oldField.value, after: field.value, unit: field.unit } : null;
    })
    .filter((item): item is { key: string; label: string; before: number; after: number; unit: string } => Boolean(item));

  return (
    <section className="qa-panel" aria-label="Diff and QA panel">
      <div className="tree-heading">
        <h2>Diff / QA</h2>
        <span>{diffs.length} changes</span>
      </div>
      <div className="preview-actions">
        <button type="button" onClick={onUndo} disabled={!canUndo}>Undo</button>
        <button type="button" onClick={onRedo} disabled={!canRedo}>Redo</button>
        <button type="button" onClick={onAcceptBaseline}>Accept baseline</button>
      </div>
      {diffs.length === 0 ? (
        <p className="message">Изменений параметров нет.</p>
      ) : (
        <div className="diff-table">
          {diffs.map((diff) => (
            <div className="diff-row" key={diff.key}>
              <span>{diff.label}</span>
              <code>{diff.before} {diff.unit}</code>
              <strong>{diff.after} {diff.unit}</strong>
            </div>
          ))}
        </div>
      )}
      <p className="message ok">QA: patch visible before commit; release action remains outside draft workflow.</p>
    </section>
  );
}

type PreviewState =
  | { status: "idle" }
  | { status: "patching"; draftId?: string }
  | { status: "queued"; draftId: string; jobId: string }
  | { status: "running"; draftId: string; job: JobSummary }
  | { status: "error"; message: string; jobId?: string };

function PreviewWorkflow({
  client,
  model,
  properties,
  state,
  onStateChange
}: {
  client: ReturnType<typeof createStudioClient>;
  model: ModelSummary;
  properties: PropertyField[];
  state: PreviewState;
  onStateChange: (state: PreviewState) => void;
}) {
  async function runPreview() {
    onStateChange({ status: "patching" });
    try {
      const draft = await client.createDraft(model.id, { baseRevisionId: model.activeRevisionId });
      const patched = await client.applyPatch(draft.id, {
        baseRevisionToken: draft.headRevisionToken,
        operations: properties.map((field) => ({
          op: "setParameter",
          path: `/${field.key}`,
          value: field.value,
          unit: field.unit
        }))
      });
      const updatedDraft: DraftSummary = await client.getDraft(patched.draftId);
      const accepted = await client.previewDraft(updatedDraft.id, {
        baseRevisionToken: updatedDraft.headRevisionToken,
        profile: "web-preview"
      });
      onStateChange({ status: "queued", draftId: updatedDraft.id, jobId: accepted.jobId });
    } catch (err) {
      onStateChange({ status: "error", message: err instanceof Error ? err.message : "Preview failed" });
    }
  }

  async function refreshJob(jobId: string, draftId: string) {
    try {
      const job = await client.getJob(jobId);
      onStateChange({ status: "running", draftId, job });
    } catch (err) {
      onStateChange({ status: "error", jobId, message: err instanceof Error ? err.message : "Progress failed" });
    }
  }

  async function cancelJob(jobId: string) {
    try {
      const job = await client.cancelJob(jobId);
      onStateChange({ status: "running", draftId: state.status === "queued" || state.status === "running" ? state.draftId : "", job });
    } catch (err) {
      onStateChange({ status: "error", jobId, message: err instanceof Error ? err.message : "Cancel failed" });
    }
  }

  async function retryJob(jobId: string) {
    try {
      const job = await client.retryJob(jobId);
      onStateChange({ status: "running", draftId: state.status === "running" ? state.draftId : "", job });
    } catch (err) {
      onStateChange({ status: "error", jobId, message: err instanceof Error ? err.message : "Retry failed" });
    }
  }

  const activeJobId = state.status === "queued" ? state.jobId : state.status === "running" ? state.job.id : state.status === "error" ? state.jobId : undefined;
  const activeDraftId = state.status === "queued" || state.status === "running" ? state.draftId : "";

  return (
    <section className="preview-panel" aria-label="Patch preview workflow">
      <div className="tree-heading">
        <h2>Preview workflow</h2>
        <span>{state.status}</span>
      </div>
      <div className="preview-actions">
        <button type="button" onClick={runPreview}>Preview patch</button>
        {activeJobId && <button type="button" onClick={() => refreshJob(activeJobId, activeDraftId)}>Progress</button>}
        {activeJobId && <button type="button" onClick={() => cancelJob(activeJobId)}>Cancel</button>}
        {activeJobId && <button type="button" onClick={() => retryJob(activeJobId)}>Retry</button>}
      </div>
      {state.status === "queued" && <p className="message ok">Queued job {state.jobId}</p>}
      {state.status === "running" && <p className="message ok">Job {state.job.id}: {state.job.state}, {state.job.progress}%</p>}
      {state.status === "error" && <p className="message error">{state.message}</p>}
    </section>
  );
}

function PropertyEditor({
  fields,
  onChange
}: {
  fields: PropertyField[];
  onChange: (fields: PropertyField[]) => void;
}) {
  function updateField(key: string, value: number) {
    onChange(fields.map((field) => field.key === key ? { ...field, value } : field));
  }

  return (
    <section className="property-panel" aria-label="Property editor">
      <div className="tree-heading">
        <h2>Свойства компонента</h2>
        <span>schema-driven</span>
      </div>
      <div className="property-grid">
        {fields.map((field) => (
          <label className="property-row" key={field.key}>
            <span>
              {field.label}
              <small>{field.sourceStatus}</small>
            </span>
            <input
              type="number"
              min={field.min}
              max={field.max}
              value={field.value}
              onChange={(event) => updateField(field.key, Number(event.target.value))}
            />
            <code>{field.unit}</code>
          </label>
        ))}
      </div>
    </section>
  );
}

type ViewerMode = "visible" | "isolate" | "views" | "section" | "measure" | "explode";

function ModelViewer({
  selectedRevisionId,
  selectedComponentId,
  viewerMode,
  onModeChange,
  onSelectComponent
}: {
  selectedRevisionId: string;
  selectedComponentId: string;
  viewerMode: ViewerMode;
  onModeChange: (mode: ViewerMode) => void;
  onSelectComponent: (componentId: string) => void;
}) {
  const hostRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    const host = hostRef.current;
    if (!host) return;
    const width = host.clientWidth || 640;
    const height = host.clientHeight || 360;
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0xf8fafc);
    const camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 1000);
    camera.position.set(4, 3, 5);
    camera.lookAt(0, 0, 0);

    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.setSize(width, height, false);
    host.appendChild(renderer.domElement);

    const cabinet = new THREE.BoxGeometry(2.2, 1.4, 3.2);
    const material = new THREE.MeshStandardMaterial({ color: 0x8aa0ad, metalness: 0.25, roughness: 0.55 });
    const mesh = new THREE.Mesh(cabinet, material);
    mesh.userData.componentId = "cmp_0";
    scene.add(mesh);

    const edges = new THREE.EdgesGeometry(cabinet);
    const edgeLines = new THREE.LineSegments(edges, new THREE.LineBasicMaterial({ color: 0x1f2933 }));
    mesh.add(edgeLines);

    scene.add(new THREE.HemisphereLight(0xffffff, 0x94a3b8, 2.4));
    const light = new THREE.DirectionalLight(0xffffff, 1.8);
    light.position.set(4, 5, 3);
    scene.add(light);
    const raycaster = new THREE.Raycaster();
    const pointer = new THREE.Vector2();

    function selectFromCanvas(event: PointerEvent) {
      const bounds = renderer.domElement.getBoundingClientRect();
      pointer.x = ((event.clientX - bounds.left) / bounds.width) * 2 - 1;
      pointer.y = -((event.clientY - bounds.top) / bounds.height) * 2 + 1;
      raycaster.setFromCamera(pointer, camera);
      const hit = raycaster.intersectObject(mesh, true)[0];
      if (hit) {
        onSelectComponent(mesh.userData.componentId);
      }
    }
    renderer.domElement.addEventListener("pointerdown", selectFromCanvas);

    let frame = 0;
    function render() {
      material.color.set(selectedComponentId === "cmp_0" ? 0x2f8f83 : 0x8aa0ad);
      mesh.visible = viewerMode !== "isolate" || selectedComponentId === "cmp_0";
      mesh.position.x = viewerMode === "explode" ? 0.35 : 0;
      mesh.scale.z = viewerMode === "section" ? 0.65 : 1;
      mesh.rotation.z = 0.02;
      mesh.rotation.y += 0.006;
      renderer.render(scene, camera);
      frame = window.requestAnimationFrame(render);
    }
    render();

    return () => {
      window.cancelAnimationFrame(frame);
      renderer.domElement.removeEventListener("pointerdown", selectFromCanvas);
      host.removeChild(renderer.domElement);
      cabinet.dispose();
      edges.dispose();
      material.dispose();
      (edgeLines.material as THREE.Material).dispose();
      renderer.dispose();
    };
  }, [onSelectComponent, selectedComponentId, selectedRevisionId, viewerMode]);

  return (
    <section className="viewer-panel" aria-label="3D viewer">
      <div className="tree-heading">
        <h2>3D viewer</h2>
        <span>{selectedRevisionId || "no revision"} · {selectedComponentId}</span>
      </div>
      <div className="viewer-toolbar" aria-label="Viewer tools">
        <ToolButton active={viewerMode === "visible"} label="Visibility" onClick={() => onModeChange("visible")}><Eye size={17} /></ToolButton>
        <ToolButton active={viewerMode === "isolate"} label="Isolate" onClick={() => onModeChange("isolate")}><Focus size={17} /></ToolButton>
        <ToolButton active={viewerMode === "views"} label="Views" onClick={() => onModeChange("views")}><Layers size={17} /></ToolButton>
        <ToolButton active={viewerMode === "section"} label="Section" onClick={() => onModeChange("section")}><Scissors size={17} /></ToolButton>
        <ToolButton active={viewerMode === "measure"} label="Measure" onClick={() => onModeChange("measure")}><Ruler size={17} /></ToolButton>
        <ToolButton active={viewerMode === "explode"} label="Exploded view" onClick={() => onModeChange("explode")}><ChevronRight size={17} /></ToolButton>
      </div>
      <div className="viewer-host" ref={hostRef} />
      {viewerMode === "measure" && <div className="measure-readout">X 2200 · Y 1400 · Z 3200 mm</div>}
    </section>
  );
}

function ToolButton({
  active,
  label,
  onClick,
  children
}: {
  active: boolean;
  label: string;
  onClick: () => void;
  children: React.ReactNode;
}) {
  return (
    <button type="button" className={active ? "tool-button active" : "tool-button"} onClick={onClick} title={label} aria-label={label}>
      {children}
    </button>
  );
}

function VirtualizedTree({
  nodes,
  selectedId,
  onSelect
}: {
  nodes: TreeNode[];
  selectedId: string;
  onSelect: (componentId: string) => void;
}) {
  const flatNodes = useMemo(() => flattenTree(nodes), [nodes]);
  const [scrollTop, setScrollTop] = useState(0);
  const visibleCount = Math.ceil(TREE_VIEWPORT_HEIGHT / TREE_ROW_HEIGHT) + TREE_OVERSCAN * 2;
  const startIndex = Math.max(0, Math.floor(scrollTop / TREE_ROW_HEIGHT) - TREE_OVERSCAN);
  const visibleNodes = flatNodes.slice(startIndex, startIndex + visibleCount);
  const totalHeight = flatNodes.length * TREE_ROW_HEIGHT;

  return (
    <section className="tree-panel" aria-label="Component tree">
      <div className="tree-heading">
        <h2>Дерево компонентов</h2>
        <span>{flatNodes.length} nodes</span>
      </div>
      <div
        className="tree-viewport"
        style={{ height: TREE_VIEWPORT_HEIGHT }}
        onScroll={(event) => setScrollTop(event.currentTarget.scrollTop)}
      >
        <div className="tree-spacer" style={{ height: totalHeight }}>
          <div className="tree-window" style={{ transform: `translateY(${startIndex * TREE_ROW_HEIGHT}px)` }}>
            {visibleNodes.map((node) => (
              <button
                className={node.id === selectedId ? "tree-row selected" : "tree-row"}
                key={node.id}
                type="button"
                onClick={() => onSelect(node.id)}
                style={{ height: TREE_ROW_HEIGHT, paddingLeft: 10 + node.depth * 18 }}
              >
                {node.hasChildren ? <ChevronRight size={15} aria-hidden="true" /> : <span className="tree-dot" />}
                <span>{node.label}</span>
                <code>{node.id}</code>
              </button>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
