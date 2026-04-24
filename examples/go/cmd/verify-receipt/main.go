// Verify a receipt: SHA-256 (stdlib) + BLAKE3 (github.com/zeebo/blake3).
// When Python is available, canonical bytes come from scripts/payload_canonical_b64.py
// (same source of truth as verifier/verify.py). Otherwise falls back to pure-Go JSON.
//
// Run: cd examples/go && go mod download && go run ./cmd/verify-receipt <path/to/receipt.json>
package main

import (
	"crypto/sha256"
	"encoding/base64"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
	"strings"

	"github.com/zeebo/blake3"
)

func main() {
	if len(os.Args) < 2 {
		fmt.Fprintln(os.Stderr, "Usage: go run ./cmd/verify-receipt <receipt.json>")
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
	canon, err := canonicalBytes(os.Args[1], plink)
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

func findRepoRoot() string {
	if v := os.Getenv("INQUIRO_ROOT"); v != "" {
		return v
	}
	if v := os.Getenv("GITHUB_WORKSPACE"); v != "" {
		return v
	}
	wd, err := os.Getwd()
	if err != nil {
		return ""
	}
	prev := ""
	for d := wd; d != "" && d != prev; prev, d = d, filepath.Dir(d) {
		if st, e := os.Stat(filepath.Join(d, "canonical_payload.py")); e == nil && !st.IsDir() {
			return d
		}
	}
	return ""
}

func canonicalBytes(receiptPath string, plink map[string]any) ([]byte, error) {
	root := findRepoRoot()
	script := filepath.Join(root, "scripts", "payload_canonical_b64.py")
	if root != "" {
		if st, e := os.Stat(script); e == nil && !st.IsDir() {
			var cmd *exec.Cmd
			if p, _ := exec.LookPath("python3"); p != "" {
				cmd = exec.Command("python3", script, receiptPath)
			} else if p, _ := exec.LookPath("py"); p != "" {
				cmd = exec.Command("py", "-3", script, receiptPath)
			} else {
				return nil, fmt.Errorf("no python3 on PATH")
			}
			cmd.Dir = root
			out, err := cmd.CombinedOutput()
			if err != nil {
				if os.Getenv("INQUIRO_ROOT") != "" {
					return nil, fmt.Errorf("payload_canonical_b64: %w\n%s", err, string(out))
				}
			} else {
				b64s := strings.TrimSpace(string(out))
				b, decErr := base64.StdEncoding.DecodeString(b64s)
				if decErr == nil {
					return b, nil
				}
				if os.Getenv("INQUIRO_ROOT") != "" {
					clip := b64s
					if len(clip) > 64 {
						clip = clip[:64]
					}
					return nil, fmt.Errorf("base64 decode: %v (output: %q)", decErr, clip)
				}
			}
		}
	}
	norm := normalizeForCanonical(plink)
	return json.Marshal(norm)
}

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
