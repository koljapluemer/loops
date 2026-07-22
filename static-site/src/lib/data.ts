import fs from "node:fs";
import path from "node:path";

// astro dev/build/preview always run with cwd = static-site/, and data/
// lives one level up from there. (import.meta.url isn't used here since
// bundling relocates this module's emitted chunk at build time.)
const DATA_DIR = path.resolve(process.cwd(), "../data");

type RatableTextEntry = [string, ...unknown[]];
type RatableTextList = RatableTextEntry[];
type UrlEntry = [string, string, ...unknown[]];

interface RawEntry {
  name: RatableTextList;
  description?: RatableTextList;
  topics?: RatableTextList;
  urls?: UrlEntry[];
  rels?: Record<string, RatableTextList>;
  img?: string;
}

export interface Entry {
  id: string; // e.g. "learn:able:to-sing"
  segments: string[]; // e.g. ["learn", "able", "to-sing"]
  top: string;
  sub?: string;
  slug: string;
  name: string;
  altNames: string[];
  raw: RawEntry;
}

export interface Backlink {
  from: Entry;
  label: string;
}

function firstOf(list: RatableTextList | undefined): string[] {
  return (list ?? []).map((entry) => entry[0]);
}

function walk(dir: string, segments: string[], out: Entry[]): void {
  for (const dirent of fs.readdirSync(dir, { withFileTypes: true })) {
    if (dirent.isDirectory()) {
      walk(path.join(dir, dirent.name), [...segments, dirent.name], out);
    } else if (dirent.isFile() && dirent.name.endsWith(".json")) {
      const slug = dirent.name.slice(0, -".json".length);
      const fullSegments = [...segments, slug];
      const raw = JSON.parse(
        fs.readFileSync(path.join(dir, dirent.name), "utf-8"),
      ) as RawEntry;
      const names = firstOf(raw.name);
      out.push({
        id: fullSegments.join(":"),
        segments: fullSegments,
        top: fullSegments[0],
        sub: fullSegments.length === 3 ? fullSegments[1] : undefined,
        slug,
        name: names[0] ?? slug,
        altNames: names.slice(1),
        raw,
      });
    }
  }
}

let entriesCache: Entry[] | null = null;

function loadEntries(): Entry[] {
  if (!entriesCache) {
    const out: Entry[] = [];
    walk(DATA_DIR, [], out);
    out.sort((a, b) => a.name.localeCompare(b.name));
    entriesCache = out;
  }
  return entriesCache;
}

let backlinksCache: Map<string, Backlink[]> | null = null;

function loadBacklinks(): Map<string, Backlink[]> {
  if (!backlinksCache) {
    const map = new Map<string, Backlink[]>();
    for (const entry of loadEntries()) {
      for (const [targetId, labelList] of Object.entries(
        entry.raw.rels ?? {},
      )) {
        const label = firstOf(labelList).join(", ");
        const list = map.get(targetId) ?? [];
        list.push({ from: entry, label });
        map.set(targetId, list);
      }
    }
    backlinksCache = map;
  }
  return backlinksCache;
}

export function getAllEntries(): Entry[] {
  return loadEntries();
}

export function getTopLevels(): string[] {
  return fs
    .readdirSync(DATA_DIR, { withFileTypes: true })
    .filter((d) => d.isDirectory())
    .map((d) => d.name)
    .sort();
}

export function getEntriesByTop(top: string): Entry[] {
  return loadEntries().filter((e) => e.top === top);
}

export function getEntry(id: string): Entry | undefined {
  return loadEntries().find((e) => e.id === id);
}

export function getBacklinks(id: string): Backlink[] {
  return loadBacklinks().get(id) ?? [];
}

export function idToHref(id: string): string {
  return "/" + id.split(":").join("/") + "/";
}

export function relLabel(labelList: RatableTextList): string {
  return firstOf(labelList).join(", ");
}

export function textList(list: RatableTextList | undefined): string[] {
  return firstOf(list);
}

const GIF_SIGNATURE = "R0lGOD";
const PNG_SIGNATURE = "iVBORw0KGgo";
const JPEG_SIGNATURE = "/9j/";

export function imgSrc(base64: string): string {
  let mime = "image/png";
  if (base64.startsWith(GIF_SIGNATURE)) mime = "image/gif";
  else if (base64.startsWith(JPEG_SIGNATURE)) mime = "image/jpeg";
  else if (base64.startsWith(PNG_SIGNATURE)) mime = "image/png";
  return `data:${mime};base64,${base64}`;
}
