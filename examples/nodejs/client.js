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
