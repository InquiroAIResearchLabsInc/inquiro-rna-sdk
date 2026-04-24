<<<<<<< HEAD
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
=======
#!/usr/bin/env node
/**
 * Verify RNA receipt: recompute SHA-256 and BLAKE3 of canonical attestation payload.
 * PROTOCOL TESTING ONLY — not suitable for cryptographic verification in production.
 * Usage: node verifier/verify.js <receipt.json>
 * Exit 0 on success, 1 on failure.
 *
 * Requires: npm install blake3  (in this directory or a parent with package.json)
 */
'use strict';

const crypto = require('crypto');
const fs = require('fs');

let blake3;
try {
  blake3 = require('blake3');
} catch {
  process.stderr.write(
    'WARN: blake3 npm package not found. Run: npm install blake3\n' +
    '      SHA-256 will be verified; BLAKE3 will be skipped.\n'
  );
  blake3 = null;
}

function canonicalJson(obj) {
  if (obj === null || Array.isArray(obj) || typeof obj !== 'object') {
    return JSON.stringify(obj);
  }
  const keys = Object.keys(obj).sort();
  return '{' + keys.map((k) => JSON.stringify(k) + ':' + canonicalJson(obj[k])).join(',') + '}';
}

function canonicalBytes(obj) {
  return Buffer.from(canonicalJson(obj), 'utf-8');
}

function extractReceipt(doc) {
  if (doc.receipt && typeof doc.receipt === 'object') return doc.receipt;
  if (doc.result && typeof doc.result === 'object') {
    const r = doc.result;
    if (r.receipt && typeof r.receipt === 'object') return r.receipt;
    if (r.sha256 && r.blake3 && r.payload) return r;
  }
  if (doc.sha256 && doc.blake3 && doc.payload) return doc;
  throw new Error(
    'Could not find receipt object (expected receipt.payload, result.receipt, or inline sha256/blake3/payload)'
  );
}

function main() {
  const args = process.argv.slice(2).filter((a) => a !== '--all');
  if (!args.length || args[0] === '-h' || args[0] === '--help') {
    process.stderr.write('Usage: node verifier/verify.js <receipt.json>\n');
    process.exit(1);
  }
  const filePath = args[0];
  if (!fs.existsSync(filePath)) {
    process.stderr.write(`FAIL: not a file: ${filePath}\n`);
    process.exit(1);
  }
  let doc, receipt;
  try {
    doc = JSON.parse(fs.readFileSync(filePath, 'utf-8'));
    receipt = extractReceipt(doc);
  } catch (e) {
    process.stderr.write(`FAIL: ${e.message}\n`);
    process.exit(1);
  }
  const pl = receipt.payload;
  if (!pl || typeof pl !== 'object' || Array.isArray(pl)) {
    process.stderr.write('FAIL: receipt missing dict payload\n');
    process.exit(1);
  }
  const expectedSha = receipt.sha256;
  const expectedB3 = receipt.blake3;
  if (typeof expectedSha !== 'string' || typeof expectedB3 !== 'string') {
    process.stderr.write('FAIL: receipt missing sha256 or blake3 string fields\n');
    process.exit(1);
  }
  const data = canonicalBytes(pl);
  const gotSha = crypto.createHash('sha256').update(data).digest('hex');
  let gotB3 = null;
  if (blake3) {
    const h = blake3.createHash();
    h.update(data);
    gotB3 = h.digest('hex');
  }
  const shaMatch = gotSha === expectedSha;
  const b3Match = gotB3 !== null ? gotB3 === expectedB3 : true;

  if (shaMatch && b3Match) {
    console.log(`VERIFIED: dual hash matches (sha256=${gotSha.slice(0, 12)}...)`);
    process.exit(0);
  }
  const parts = [];
  if (!shaMatch) parts.push(`SHA256 mismatch (expected ${expectedSha}, got ${gotSha})`);
  if (gotB3 !== null && !b3Match) parts.push(`BLAKE3 mismatch (expected ${expectedB3}, got ${gotB3})`);
  console.log(`FAILED: ${parts.join('; ')}`);
  process.exit(1);
}

main();
>>>>>>> 77e9a363fc0946913d50da8c968b2aa40bd8fec2
