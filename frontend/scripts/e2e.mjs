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

  const browser = await chromium.launch({ headless: true });
  const viewports = [
    { name: "desktop", width: 1440, height: 1000 },
    { name: "narrow", width: 390, height: 1200 }
  ];

  for (const viewport of viewports) {
    const page = await browser.newPage({ viewport });
    await page.goto(`${baseUrl}/models/${model.id}`, { waitUntil: "networkidle" });
    await page.getByRole("button", { name: "Exploded view" }).click();
    await page.getByRole("button", { name: "Measure" }).click();
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
    await page.close();
  }

  await browser.close();
  console.log(`P5-11 E2E passed. Screenshots: ${artifactDir}`);
} finally {
  server.kill("SIGTERM");
}
