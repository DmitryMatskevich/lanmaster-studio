import { readFile } from "node:fs/promises";
import { resolve } from "node:path";
import assert from "node:assert/strict";

const root = resolve(import.meta.dirname, "..");
const apiSource = await readFile(resolve(root, "src/api.ts"), "utf8");
const appSource = await readFile(resolve(root, "src/main.tsx"), "utf8");

assert.match(apiSource, /X-Dev-User/);
assert.match(apiSource, /X-Dev-Roles/);
assert.match(apiSource, /StudioApiClient/);
assert.match(appSource, /\/models\/new/);
assert.match(appSource, /\/models\/\$\{model\.id\}/);
assert.match(appSource, /client\.me\(\)/);
assert.match(appSource, /client\.listModels/);
assert.match(appSource, /client\.getModel/);
assert.match(appSource, /client\.listRevisions/);
assert.match(appSource, /Revision selector/);
assert.match(appSource, /buildDemoTree\(1000\)/);
assert.match(appSource, /TREE_ROW_HEIGHT = 32/);
assert.match(appSource, /TREE_VIEWPORT_HEIGHT = 384/);
assert.match(appSource, /translateY/);

console.log("Frontend scaffold verification passed");
