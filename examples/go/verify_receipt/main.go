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
	// Match Python json.loads+canonical: JSON integers become float64 in Go; json.Marshal
	// of float64(1) must match int 1 in Python — normalize whole numbers to int64.
	norm := normalizeForCanonical(plink)
	canon, err := json.Marshal(norm)
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

// normalizeForCanonical aligns JSON number types with Python's json: whole floats → int64
// so encoding matches json.dumps on dicts that used int for JSON integer literals.
func normalizeForCanonical(v any) any {
	switch t := v.(type) {
	case float64:
		if t == float64(int64(t)) {
			return int64(t)
		}
		return t
	case map[string]any:
		m := make(map[string]any, len(t))
		for k, v := range t {
			m[k] = normalizeForCanonical(v)
		}
		return m
	case []any:
		out := make([]any, len(t))
		for i, x := range t {
			out[i] = normalizeForCanonical(x)
		}
		return out
	default:
		return v
	}
}
