// gta6-meme-x-01 entry v3 -- "13 Years. The Coin Waited Too -- GTA 6".
//
// The entry itself is the X post: a 2x2 timeline meme (2013 -> 2026, the same
// make.fun ghost and its magenta coin in every panel) plus the post text in
// post.txt. This program's whole job is to hand the post's address to the
// gate: it copies POST.json from the bot directory to the output directory.
//
// Node 22, standard library only. Deterministic: no network, no clock.
//
// Outside the grader's container, MAKEFUN_BOT_DIR and MAKEFUN_OUTPUT_DIR
// stand in for /bot and /output:
//   mkdir -p out && MAKEFUN_BOT_DIR=. MAKEFUN_OUTPUT_DIR=out node main.ts

import { copyFileSync, mkdirSync, readFileSync } from "node:fs";
import { join } from "node:path";

const BOT_DIR = process.env.MAKEFUN_BOT_DIR ?? "/bot";
const OUTPUT_DIR = process.env.MAKEFUN_OUTPUT_DIR ?? "/output";

const SOURCE = join(BOT_DIR, "POST.json");
const TARGET = join(OUTPUT_DIR, "POST.json");

function fail(message: string): never {
  console.error(`main.ts: ${message}`);
  process.exit(1);
}

// Read and validate POST.json before copying anything: it must parse as
// JSON and carry the post address in a string `url` field.
let raw: string;
try {
  raw = readFileSync(SOURCE, "utf8");
} catch (err) {
  fail(`cannot read ${SOURCE}: ${(err as Error).message}`);
}

let post: unknown;
try {
  post = JSON.parse(raw!);
} catch (err) {
  fail(`POST.json is not valid JSON: ${(err as Error).message}`);
}

if (
  typeof post !== "object" ||
  post === null ||
  typeof (post as { url?: unknown }).url !== "string" ||
  (post as { url: string }).url.length === 0
) {
  fail("POST.json must be a JSON object with a non-empty string `url`.");
}

// The post checks out -- copy it, byte for byte, to the output directory,
// then read the copy back and confirm it survived the trip intact.
try {
  mkdirSync(OUTPUT_DIR, { recursive: true });
  copyFileSync(SOURCE, TARGET);
  if (readFileSync(TARGET, "utf8") !== raw!) {
    fail(`copied POST.json at ${TARGET} does not match the source.`);
  }
} catch (err) {
  if ((err as Error).message.startsWith("copied POST.json")) throw err;
  fail(`could not copy POST.json to ${TARGET}: ${(err as Error).message}`);
}

console.log(`main.ts: copied POST.json -> ${TARGET}`);
