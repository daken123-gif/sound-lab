import { existsSync, readFileSync } from "node:fs";
import { dirname, extname, relative, resolve, sep } from "node:path";
import { fileURLToPath } from "node:url";

const REFERENCE_PATTERNS = [
  /\bimport\s+(?:[^"']+?\s+from\s+)?["']([^"']+)["']/g,
  /\bnew\s+URL\(\s*["']([^"']+)["']\s*,\s*import\.meta\.url\s*\)/g,
  /<script\b[^>]*\bsrc=["']([^"']+)["'][^>]*>/gi
];

export function extractRelativeAssetReferences(source) {
  const references = new Set();
  for (const pattern of REFERENCE_PATTERNS) {
    pattern.lastIndex = 0;
    for (const match of source.matchAll(pattern)) {
      if (match[1].startsWith("./") || match[1].startsWith("../")) references.add(match[1]);
    }
  }
  return [...references];
}

export function collectBrowserAssets(entryPath) {
  const entry = resolve(entryPath instanceof URL ? fileURLToPath(entryPath) : entryPath);
  const root = dirname(entry);
  const pending = [entry];
  const visited = new Set();

  while (pending.length > 0) {
    const current = pending.pop();
    if (visited.has(current)) continue;
    if (!existsSync(current)) throw new Error(`missing browser asset: ${relative(root, current)}`);
    visited.add(current);

    const extension = extname(current);
    if (extension !== ".html" && extension !== ".js") continue;
    const source = readFileSync(current, "utf8");
    for (const reference of extractRelativeAssetReferences(source)) {
      const dependency = resolve(dirname(current), reference);
      const relativePath = relative(root, dependency);
      if (relativePath === ".." || relativePath.startsWith(`..${sep}`)) {
        throw new Error(`browser asset escapes root: ${reference}`);
      }
      pending.push(dependency);
    }
  }

  return [...visited]
    .map(path => relative(root, path).split(sep).join("/"))
    .sort();
}
