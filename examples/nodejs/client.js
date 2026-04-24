<<<<<<< HEAD
/**
 * Inquiro RNA MCP example client (Node 18+ fetch). Requires: npm install
 * Usage: node client.js [--mock]
 */
import { readFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const DEFAULT_URL = "https://aiflightrecorder.onrender.com/mcp";

async function rpc(url, id, method, params) {
  const body = { jsonrpc: "2.0", id, method, ...(params !== undefined ? { params } : {}) };
  const r = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!r.ok) {
    console.error(`HTTP ${r.status}`, await r.text());
    process.exit(1);
  }
  return r.json();
}

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(__dirname, "../..");

const mock = process.argv.includes("--mock");
const url = mock ? "http://localhost:8000/mcp" : process.env.RNA_URL || DEFAULT_URL;

const payloadPath = path.join(root, "payloads", "identity_verified.json");
const att = JSON.parse(await readFile(payloadPath, "utf8"));

console.log("=== tools/list ===");
console.log(JSON.stringify(await rpc(url, "1", "tools/list", {}), null, 2));

console.log("\n=== submit_attestation ===");
const sub = await rpc(url, "2", "tools/call", {
  name: "submit_attestation",
  arguments: att,
});
console.log(JSON.stringify(sub, null, 2));

let rh = sub.result?.receipt_hash;
if (!rh && sub.result?.content?.[0]?.text) {
  rh = JSON.parse(sub.result.content[0].text).receipt_hash;
}
if (!rh) {
  console.error("No receipt_hash");
  process.exit(1);
}

console.log("\n=== verify_receipt ===");
console.log(
  JSON.stringify(
    await rpc(url, "3", "tools/call", { name: "verify_receipt", arguments: { receipt_hash: rh } }),
    null,
    2,
  ),
);

console.log("\n=== query_flight_summary ===");
console.log(
  JSON.stringify(
    await rpc(url, "4", "tools/call", {
      name: "query_flight_summary",
      arguments: { flight_id: "FLIGHT-DEMO-001", time_range: {} },
    }),
    null,
    2,
  ),
);

console.log("\n=== get_flight_health ===");
console.log(
  JSON.stringify(
    await rpc(url, "5", "tools/call", {
      name: "get_flight_health",
      arguments: { flight_id: "FLIGHT-DEMO-001" },
    }),
    null,
    2,
  ),
);

console.log("\n=== verify_chain_segment ===");
console.log(
  JSON.stringify(
    await rpc(url, "6", "tools/call", {
      name: "verify_chain_segment",
      arguments: { start_hash: rh, end_hash: rh },
    }),
    null,
    2,
  ),
);
=======
#!/usr/bin/env node
// Example: submit an attestation to the RNA mock server and print the receipt.
// Usage: node examples/nodejs/client.js
// Set RNA_BASE_URL to override the default mock server URL.
'use strict';

const http = require('http');
const https = require('https');
const { URL } = require('url');

const BASE_URL = process.env.RNA_BASE_URL || 'http://localhost:8000/mcp';

const payload = {
  event_type: 'identity_verified',
  device_id: 'DEV-001',
  tenant_id: 'demo_public',
  metadata: { source: 'sdk-example', version: 1 },
};

const body = JSON.stringify({
  jsonrpc: '2.0',
  id: '1',
  method: 'tools/call',
  params: { name: 'submit_attestation', arguments: { payload } },
});

function post(urlStr, bodyStr, cb) {
  const u = new URL(urlStr);
  const lib = u.protocol === 'https:' ? https : http;
  const options = {
    hostname: u.hostname,
    port: u.port || (u.protocol === 'https:' ? 443 : 80),
    path: u.pathname,
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Content-Length': Buffer.byteLength(bodyStr),
    },
  };
  const req = lib.request(options, (res) => {
    let data = '';
    res.on('data', (chunk) => { data += chunk; });
    res.on('end', () => cb(null, data));
  });
  req.on('error', (e) => cb(e));
  req.write(bodyStr);
  req.end();
}

post(BASE_URL, body, (err, raw) => {
  if (err) {
    process.stderr.write(`FAIL: ${err.message}\n`);
    process.exit(1);
  }
  let resp;
  try {
    resp = JSON.parse(raw);
  } catch (e) {
    process.stderr.write(`FAIL: invalid JSON: ${raw.slice(0, 200)}\n`);
    process.exit(1);
  }
  const result = resp.result || resp;
  const receipt = result.receipt || result;
  const sha = receipt.sha256 || '?';
  const b3 = receipt.blake3 || '?';
  console.log(`receipt_hash: ${sha}:${b3}`);
  console.log(JSON.stringify(receipt, null, 2));
});
>>>>>>> 77e9a363fc0946913d50da8c968b2aa40bd8fec2
