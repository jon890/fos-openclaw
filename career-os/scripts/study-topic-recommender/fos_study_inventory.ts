import { readdirSync, statSync } from "fs";
import { join, relative, sep } from "path";

export interface FosStudyInventoryOptions {
  root: string;
  excludeDirs?: string[];
}

export interface FosStudyInventory {
  root: string;
  scannedMarkdownCount: number;
  excludedDirs: string[];
  markdownPathsRelative: string[];
}

export function scanFosStudyInventory(opts: FosStudyInventoryOptions): FosStudyInventory {
  const excludeDirs = opts.excludeDirs ?? [".git", ".claude"];
  const results: string[] = [];

  function walk(dir: string): void {
    let entries;
    try {
      entries = readdirSync(dir, { withFileTypes: true });
    } catch {
      return;
    }
    for (const entry of entries) {
      if (entry.isDirectory()) {
        if (excludeDirs.includes(entry.name)) continue;
        walk(join(dir, entry.name));
      } else if (entry.isFile() && entry.name.endsWith(".md")) {
        const abs = join(dir, entry.name);
        const rel = relative(opts.root, abs).split(sep).join("/");
        results.push(rel);
      }
    }
  }

  walk(opts.root);
  results.sort();

  return {
    root: opts.root,
    scannedMarkdownCount: results.length,
    excludedDirs: excludeDirs,
    markdownPathsRelative: results,
  };
}
