/**
 * Inquiro RNA receipt verifier (SHA256 + BLAKE3 over canonical attestation).
 * Browser: import { verifyReceipt } from './verify.js'
 * CLI: node verify.js path/to/merged.json
 */
import { blake3 } from "@noble/hashes/blake3.js";
import { createHash } from "node:crypto";
import { readFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

/** Canonical JSON: sorted object keys, compact separators, UTF-8 (matches Python verifier). */
export function canonicalStringify(value) {
  if (value === null || typeof value !== "object") {
    return JSON.stringify(value);
  }
  if (Array.isArray(value)) {
    return `[${value.map((x) => canonicalStringify(x)).join(",")}]`;
  }
  const keys = Object.keys(value).sort();
  return `{${keys.map((k) => `${JSON.stringify(k)}:${canonicalStringify(value[k])}`).join(",")}}`;
}

function splitReceiptHash(value) {
  const i = value.indexOf(":");
  if (i < 0) throw new Error("receipt_hash must be sha256_hex:blake3_hex");
  const sha = value.slice(0, i);
  const b3 = value.slice(i + 1);
  if (sha.length !== 64 || b3.length !== 64) {
    throw new Error("receipt_hash components must be 64 hex chars each");
  }
  return { sha, b3 };
}

function attestationBody(doc) {
  if (!doc.event_type || !doc.device_id || !doc.payload || !doc.timestamp || !doc.signature) {
    throw new Error("merged document must include event_type, device_id, payload, timestamp, signature");
  }
  return {
    device_id: doc.device_id,
    event_type: doc.event_type,
    payload: doc.payload,
    signature: doc.signature,
    timestamp: doc.timestamp,
  };
}

function liftResult(api) {
  const result = api.result && typeof api.result === "object" ? { ...api.result } : {};
  const c = result.content;
  if (Array.isArray(c) && c[0]?.type === "text" && typeof c[0].text === "string") {
    try {
      const inner = JSON.parse(c[0].text);
      if (inner && typeof inner === "object") {
        for (const k of Object.keys(inner)) {
          if (result[k] === undefined) result[k] = inner[k];
        }
      }
    } catch {
      /* ignore */
    }
  }
  return result;
}

/** @param {Record<string, unknown>} doc - merged attestation + receipt_hash or full RPC doc */
export async function verifyReceipt(doc) {
  let merged = doc;
  if (doc && doc.result) {
    const lifted = liftResult(doc);
    merged = { ...doc, ...lifted };
  }
  const rh = merged.receipt_hash;
  if (typeof rh !== "string") throw new Error("receipt_hash missing");
  const { sha: wantSha, b3: wantB3 } = splitReceiptHash(rh);
  const body = attestationBody(merged);
  const bytes = new TextEncoder().encode(canonicalStringify(body));
  const shaHex = createHash("sha256").update(bytes).digest("hex");
  const b3d = blake3(bytes);
  const b3Hex = Array.from(b3d)
    .map((b) => b.toString(16).padStart(2, "0"))
    .join("");
  const sha256 = shaHex === wantSha;
  const blake3ok = b3Hex === wantB3;
  return { sha256, blake3: blake3ok, verified: sha256 && blake3ok };
}

async function main() {
  const p = process.argv[2];
  if (!p) {
    console.error("Usage: node verify.js <merged.json>");
    process.exit(1);
  }
  const raw = await readFile(p, "utf8");
  const doc = JSON.parse(raw);
  const r = await verifyReceipt(doc);
  console.log(JSON.stringify(r, null, 2));
  process.exit(r.verified ? 0 : 1);
}

const __filename = fileURLToPath(import.meta.url);
if (path.resolve(process.argv[1] || "") === __filename) {
  main().catch((e) => {
    console.error(e);
    process.exit(1);
  });
}
