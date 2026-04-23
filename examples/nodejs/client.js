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
