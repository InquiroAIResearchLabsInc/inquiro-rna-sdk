/**
 * Standalone merged-receipt verifier (Node 18+).
 * npm install  (installs @noble/hashes)
 * Usage: node verify-receipt.js path/to/merged.json [--tamper-test]
 */
import { blake3 } from "@noble/hashes/blake3.js";
import { createHash } from "node:crypto";
import { readFile } from "node:fs/promises";

function canonicalStringify(value) {
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

function verifyMerged(doc) {
  const rh = doc.receipt_hash;
  if (typeof rh !== "string") throw new Error("receipt_hash missing");
  const { sha: wantSha, b3: wantB3 } = splitReceiptHash(rh);
  const body = {
    device_id: doc.device_id,
    event_type: doc.event_type,
    payload: doc.payload,
    signature: doc.signature,
    timestamp: doc.timestamp,
  };
  const bytes = new TextEncoder().encode(canonicalStringify(body));
  const shaHex = createHash("sha256").update(bytes).digest("hex");
  const b3d = blake3(bytes);
  const b3Hex = Array.from(b3d)
    .map((b) => b.toString(16).padStart(2, "0"))
    .join("");
  const ok = shaHex === wantSha && b3Hex === wantB3;
  console.log("SHA256 match:", shaHex === wantSha);
  console.log("BLAKE3 match:", b3Hex === wantB3);
  console.log(ok ? "VERIFIED" : "FAILED");
  return ok;
}

async function tamperTest() {
  const url = "https://aiflightrecorder.onrender.com/mcp";
  const attestation = {
    event_type: "identity_verified",
    device_id: "TAMPER-TEST-NODE",
    payload: { test: "tamper_detection" },
    timestamp: "2026-01-01T00:00:00Z",
    signature: "dGVzdA==",
  };
  const r = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      jsonrpc: "2.0",
      id: "1",
      method: "tools/call",
      params: { name: "submit_attestation", arguments: attestation },
    }),
  });
  const api = await r.json();
  const res = api.result || {};
  let rh = res.receipt_hash;
  if (!rh && res.content?.[0]?.text) {
    rh = JSON.parse(res.content[0].text).receipt_hash;
  }
  if (!rh) throw new Error("no receipt_hash");
  const merged = { ...attestation, receipt_hash: rh };
  if (!verifyMerged(merged)) throw new Error("original should verify");
  merged.payload = { test: "TAMPERED" };
  if (verifyMerged(merged)) throw new Error("tampered must fail");
  console.log("Tamper detection: WORKING");
}

const arg = process.argv[2];
if (arg === "--tamper-test") {
  tamperTest().catch((e) => {
    console.error(e);
    process.exit(1);
  });
} else if (!arg) {
  console.error("Usage: node verify-receipt.js <merged.json> | --tamper-test");
  process.exit(1);
} else {
  const doc = JSON.parse(await readFile(arg, "utf8"));
  process.exit(verifyMerged(doc) ? 0 : 1);
}
