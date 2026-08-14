import { mkdir, copyFile, rm } from "node:fs/promises";
import { resolve } from "node:path";
import * as esbuild from "esbuild";

const root = resolve(import.meta.dirname, "..");
const dist = resolve(root, "dist");

await rm(dist, { recursive: true, force: true });
await mkdir(resolve(dist, "assets"), { recursive: true });
await copyFile(resolve(root, "index.html"), resolve(dist, "index.html"));

await esbuild.build({
  entryPoints: [resolve(root, "src/main.tsx")],
  bundle: true,
  outfile: resolve(dist, "assets/main.js"),
  format: "esm",
  sourcemap: true,
  jsx: "automatic",
  loader: {
    ".ts": "ts",
    ".tsx": "tsx"
  }
});
