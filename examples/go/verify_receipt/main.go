// Verify a receipt: SHA-256 (stdlib) + BLAKE3 (github.com/zeebo/blake3).
// Run: go mod download
//
//   go run . ../../path/to/receipt.json
package main

import (
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"os"

	"github.com/zeebo/blake3"
)

func main() {
	if len(os.Args) < 2 {
		fmt.Fprintln(os.Stderr, "Usage: go run . <receipt.json>")
		os.Exit(1)
	}
	raw, err := os.ReadFile(os.Args[1])
	if err != nil {
		fmt.Fprintln(os.Stderr, "FAIL", err)
		os.Exit(1)
	}
	doc, err := unmarshalObject(raw)
	if err != nil {
		fmt.Fprintln(os.Stderr, "FAIL", err)
		os.Exit(1)
	}
	receipt, err := extractReceipt(doc)
	if err != nil {
		fmt.Fprintln(os.Stderr, "FAIL", err)
		os.Exit(1)
	}
	pl, ok := receipt["payload"]
	if !ok {
		fmt.Fprintln(os.Stderr, "FAIL: no payload in receipt")
		os.Exit(1)
	}
	plink, ok := pl.(map[string]any)
	if !ok {
		fmt.Fprintln(os.Stderr, "FAIL: payload not an object")
		os.Exit(1)
	}
	canon, err := json.Marshal(plink)
	if err != nil {
		fmt.Fprintln(os.Stderr, "FAIL", err)
		os.Exit(1)
	}
	shaE, _ := receipt["sha256"].(string)
	b3E, _ := receipt["blake3"].(string)
	shaG := sha256.Sum256(canon)
	shaGhex := hex.EncodeToString(shaG[:])
	b3G := blake3.Sum256(canon)
	b3Ghex := hex.EncodeToString(b3G[:])
	if shaE == shaGhex && b3E == b3Ghex {
		fmt.Println("VERIFIED")
		return
	}
	if shaE != shaGhex {
		fmt.Println("FAILED: sha256 expected", shaE, "got", shaGhex)
	}
	if b3E != b3Ghex {
		fmt.Println("FAILED: blake3 expected", b3E, "got", b3Ghex)
	}
	os.Exit(1)
}

func unmarshalObject(raw []byte) (map[string]any, error) {
	var doc map[string]any
	if err := json.Unmarshal(raw, &doc); err != nil {
		return nil, err
	}
	if doc == nil {
		return nil, fmt.Errorf("top-level must be a JSON object")
	}
	return doc, nil
}

func extractReceipt(doc map[string]any) (map[string]any, error) {
	if r, ok := doc["receipt"]; ok {
		if m, ok := r.(map[string]any); ok {
			return m, nil
		}
	}
	if r := doc["result"]; r != nil {
		if rm, ok := r.(map[string]any); ok {
			if rec, ok := rm["receipt"]; ok {
				if m, ok := rec.(map[string]any); ok {
					return m, nil
				}
			}
			if hasHashes(rm) {
				return rm, nil
			}
		}
	}
	if hasHashes(doc) {
		return doc, nil
	}
	return nil, fmt.Errorf("could not find receipt (expected inline, result.receipt, or receipt key)")
}

func hasHashes(m map[string]any) bool {
	_, s := m["sha256"]
	_, b := m["blake3"]
	_, p := m["payload"]
	return s && b && p
}
