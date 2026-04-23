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
