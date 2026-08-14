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

console.log("Frontend scaffold verification passed");
