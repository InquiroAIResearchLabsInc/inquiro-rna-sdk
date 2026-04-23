// BLAKE3 requires: go get github.com/zeebo/blake3
// Verify merged attestation + receipt_hash (same canonical rules as Python verifier).
package main

import (
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"os"
	"sort"
	"strings"

	"github.com/zeebo/blake3"
)

func main() {
	if len(os.Args) < 2 {
		fmt.Fprintln(os.Stderr, "Usage: go run verify_receipt.go <merged.json>")
		os.Exit(1)
	}
	raw, err := os.ReadFile(os.Args[1])
	if err != nil {
		fmt.Fprintln(os.Stderr, "FAIL", err)
		os.Exit(1)
	}
	var doc map[string]any
	if err := json.Unmarshal(raw, &doc); err != nil {
		fmt.Fprintln(os.Stderr, "FAIL", err)
		os.Exit(1)
	}
	rh, _ := doc["receipt_hash"].(string)
	if rh == "" {
		fmt.Fprintln(os.Stderr, "FAIL: receipt_hash missing")
		os.Exit(1)
	}
	parts := strings.SplitN(rh, ":", 2)
	if len(parts) != 2 || len(parts[0]) != 64 || len(parts[1]) != 64 {
		fmt.Fprintln(os.Stderr, "FAIL: invalid receipt_hash")
		os.Exit(1)
	}
	wantSha, wantB3 := parts[0], parts[1]

	body := map[string]any{
		"device_id":   doc["device_id"],
		"event_type":  doc["event_type"],
		"payload":     doc["payload"],
		"signature":   doc["signature"],
		"timestamp":   doc["timestamp"],
	}
	canon, err := canonicalJSON(body)
	if err != nil {
		fmt.Fprintln(os.Stderr, "FAIL", err)
		os.Exit(1)
	}
	sum := sha256.Sum256(canon)
	gotSha := hex.EncodeToString(sum[:])
	gotB3 := hex.EncodeToString(blake3.Sum256(canon))
	shaOK := gotSha == wantSha
	b3OK := gotB3 == wantB3
	fmt.Println("SHA256 match:", shaOK)
	fmt.Println("BLAKE3 match:", b3OK)
	if shaOK && b3OK {
		fmt.Println("VERIFIED")
		return
	}
	fmt.Println("FAILED")
	os.Exit(1)
}

func canonicalJSON(v any) ([]byte, error) {
	s, err := stringify(v)
	if err != nil {
		return nil, err
	}
	return []byte(s), nil
}

func stringify(v any) (string, error) {
	switch t := v.(type) {
	case nil:
		return "null", nil
	case bool:
		if t {
			return "true", nil
		}
		return "false", nil
	case float64:
		// Match encoding/json for integers stored as float64
		if t == float64(int64(t)) {
			return fmt.Sprintf("%d", int64(t)), nil
		}
		//nolint:errchkjson // fmt for JSON numbers
		b, err := json.Marshal(t)
		return string(b), err
	case string:
		b, err := json.Marshal(t)
		return string(b), err
	case []any:
		var parts []string
		for _, x := range t {
			s, err := stringify(x)
			if err != nil {
				return "", err
			}
			parts = append(parts, s)
		}
		return "[" + strings.Join(parts, ",") + "]", nil
	case map[string]any:
		keys := make([]string, 0, len(t))
		for k := range t {
			keys = append(keys, k)
		}
		sort.Strings(keys)
		var parts []string
		for _, k := range keys {
			ks, err := json.Marshal(k)
			if err != nil {
				return "", err
			}
			vs, err := stringify(t[k])
			if err != nil {
				return "", err
			}
			parts = append(parts, string(ks)+":"+vs)
		}
		return "{" + strings.Join(parts, ",") + "}", nil
	default:
		b, err := json.Marshal(t)
		return string(b), err
	}
}
