import { mkdir, rm } from "node:fs/promises";
import { resolve } from "node:path";
import { spawn } from "node:child_process";
import assert from "node:assert/strict";
import { chromium } from "playwright";
import { PNG } from "pngjs";

const root = resolve(import.meta.dirname, "..", "..");
const artifactDir = resolve(root, "frontend", "e2e-artifacts");
const databasePath = resolve(root, "var", "p5-11-e2e.db");
const port = 8091;
const baseUrl = `http://127.0.0.1:${port}`;
const python = process.env.PYTHON || "python3";

await mkdir(resolve(root, "var"), { recursive: true });
await rm(databasePath, { force: true });
await rm(artifactDir, { recursive: true, force: true });
await mkdir(artifactDir, { recursive: true });

const server = spawn(
  python,
  ["-m", "uvicorn", "studio_api.main:app", "--host", "127.0.0.1", "--port", String(port)],
  {
    cwd: root,
    env: {
      ...process.env,
      DATABASE_URL: `sqlite:///${databasePath}`,
      STUDIO_STORAGE_DIR: resolve(root, "var", "p5-11-storage"),
      STUDIO_AUTH_MODE: "dev"
    },
    stdio: ["ignore", "pipe", "pipe"]
  }
);

let serverLog = "";
server.stdout.on("data", (chunk) => {
  serverLog += chunk.toString();
});
server.stderr.on("data", (chunk) => {
  serverLog += chunk.toString();
});

async function waitForHealth() {
  const started = Date.now();
  while (Date.now() - started < 15000) {
    try {
      const response = await fetch(`${baseUrl}/health`);
      if (response.ok) return;
    } catch {
      await new Promise((resolveDelay) => setTimeout(resolveDelay, 250));
    }
  }
  throw new Error(`API did not start. Log:\n${serverLog}`);
}

async function api(path, options = {}) {
  const response = await fetch(`${baseUrl}${path}`, {
    ...options,
    headers: {
      "content-type": "application/json",
      "X-Dev-User": "e2e@example.test",
      "X-Dev-Roles": "engineer",
      ...(options.headers || {})
    }
  });
  if (!response.ok) {
    throw new Error(`${options.method || "GET"} ${path} failed: ${response.status} ${await response.text()}`);
  }
  return response.json();
}

try {
  await waitForHealth();
  const model = await api("/api/v1/models", {
    method: "POST",
    body: JSON.stringify({
      article: "P5-11-E2E",
      manufacturer: "LANMASTER",
      series: "Studio",
      name: "Responsive visual E2E fixture"
    })
  });
  const draft = await api(`/api/v1/models/${model.id}/drafts`, {
    method: "POST",
    body: JSON.stringify({})
  });
  const revision = await api(`/api/v1/drafts/${draft.id}/commit`, {
    method: "POST",
    body: JSON.stringify({
      baseRevisionToken: draft.headRevisionToken,
      schemaVersion: "2.0.0",
      pmd: {
        schemaVersion: "2.0.0",
        id: "P5-11-E2E",
        parameters: {
          width: 600,
          depth: 1000,
          height: 2055,
          railOffset: 95
        },
        parameterSchemas: {
          width: { label: "Width", unit: "mm", min: 600, max: 800, sourceStatus: "documented" },
          depth: { label: "Depth", unit: "mm", min: 600, max: 1200, sourceStatus: "documented" },
          height: { label: "Height", unit: "mm", min: 1800, max: 2200, sourceStatus: "documented" },
          railOffset: { label: "Rail offset", unit: "mm", min: 0, max: 200, sourceStatus: "documented" }
        },
        assembly: {
          components: [
            { id: "cabinet", name: "LANMASTER PMD cabinet", type: "assembly", children: ["front-door", "left-rail", "right-rail"] },
            { id: "front-door", parentId: "cabinet", name: "Three-part front door", type: "door" },
            { id: "left-rail", parentId: "cabinet", name: "Left mounting rail with square holes", type: "rail" },
            { id: "right-rail", parentId: "cabinet", name: "Right mounting rail with square holes", type: "rail" }
          ]
        }
      }
    })
  });
  assert.ok(revision.id, "seed revision was not committed");

  const browser = await chromium.launch({ headless: true });
  const viewports = [
    { name: "desktop", width: 1440, height: 1000 },
    { name: "narrow", width: 390, height: 1200 }
  ];

  for (const viewport of viewports) {
    const page = await browser.newPage({ viewport });
    await page.goto(`${baseUrl}/models/${model.id}`, { waitUntil: "networkidle" });
    await page.locator(".tree-row").first().waitFor();
    const treeRows = await page.locator(".tree-row").allTextContents();
    assert.ok(
      treeRows.some((text) => text.includes("Left mounting rail with square holes")),
      `${viewport.name} PMD tree did not load: ${treeRows.join(" | ")}`
    );
    await page.locator(".tree-row", { hasText: "Left mounting rail with square holes" }).click();
    await page.locator(".property-row", { hasText: "Width" }).locator("input").fill("650");
    await page.getByRole("button", { name: "Exploded view" }).click();
    await page.getByRole("button", { name: "Measure" }).click();
    await page.getByRole("button", { name: "Preview patch" }).click();
    await page.getByText("Queued job").waitFor();
    await page.getByRole("button", { name: "Commit draft" }).click();
    await page.getByText("Committed").waitFor();
    await page.screenshot({
      path: resolve(artifactDir, `${viewport.name}.png`),
      fullPage: true
    });

    const canvasPng = PNG.sync.read(await page.locator("canvas").screenshot());
    let canvasSignal = 0;
    for (let index = 0; index < canvasPng.data.length; index += 4) {
      const red = canvasPng.data[index];
      const green = canvasPng.data[index + 1];
      const blue = canvasPng.data[index + 2];
      const alpha = canvasPng.data[index + 3];
      if (alpha > 0 && (red < 245 || green < 245 || blue < 245)) {
        canvasSignal += 1;
      }
    }
    assert.ok(canvasSignal > 1000, `${viewport.name} viewer canvas is blank`);

    const report = await page.evaluate(() => {
      const selectors = [
        ".details",
        ".selector-panel",
        ".tree-panel",
        ".viewer-panel",
        ".property-panel",
        ".preview-panel",
        ".qa-panel",
        ".release-panel"
      ];
      const boxes = selectors.map((selector) => {
        const element = document.querySelector(selector);
        if (!element) throw new Error(`Missing ${selector}`);
        const rect = element.getBoundingClientRect();
        return { selector, left: rect.left, top: rect.top, right: rect.right, bottom: rect.bottom };
      });
      const overlaps = [];
      for (let first = 0; first < boxes.length; first += 1) {
        for (let second = first + 1; second < boxes.length; second += 1) {
          const a = boxes[first];
          const b = boxes[second];
          const intersects = a.left < b.right && a.right > b.left && a.top < b.bottom && a.bottom > b.top;
          if (intersects) overlaps.push(`${a.selector} overlaps ${b.selector}`);
        }
      }
      return {
        title: document.title,
        main: document.querySelector("main")?.getAttribute("aria-label"),
        headings: Array.from(document.querySelectorAll("h1,h2")).map((node) => node.textContent),
        overlaps
      };
    });

    assert.equal(report.title, "LANMASTER Studio");
    assert.equal(report.main, "LANMASTER Studio workspace");
    assert.equal(report.overlaps.length, 0, `${viewport.name} layout overlaps: ${report.overlaps.join(", ")}`);
    assert.ok(report.headings.includes("Commit / release"), `${viewport.name} missing release heading`);
    assert.ok(report.headings.includes("Revision selector"), `${viewport.name} missing PMD revision selector`);
    await page.close();
  }

  await browser.close();
  console.log(`P5-11 E2E passed. Screenshots: ${artifactDir}`);
} finally {
  server.kill("SIGTERM");
}
