<<<<<<< HEAD
// Example MCP client (stdlib): all 5 tools via JSON-RPC.
// Run: go run client.go
package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"os"
	"path/filepath"
)

const defaultURL = "https://aiflightrecorder.onrender.com/mcp"

func main() {
	url := os.Getenv("RNA_URL")
	if url == "" {
		url = defaultURL
	}
	if len(os.Args) > 1 && os.Args[1] == "--mock" {
		url = "http://localhost:8000/mcp"
	}

	root := findRoot()
	payloadPath := filepath.Join(root, "payloads", "identity_verified.json")
	raw, err := os.ReadFile(payloadPath)
	if err != nil {
		panic(err)
	}
	var att map[string]any
	if err := json.Unmarshal(raw, &att); err != nil {
		panic(err)
	}

	mustPrint(rpc(url, "1", "tools/list", map[string]any{}))
	sub := mustMap(rpc(url, "2", "tools/call", map[string]any{
		"name": "submit_attestation", "arguments": att,
	}))
	rh := liftReceiptHash(sub)
	if rh == "" {
		panic("no receipt_hash")
	}
	mustPrint(rpc(url, "3", "tools/call", map[string]any{
		"name": "verify_receipt", "arguments": map[string]any{"receipt_hash": rh},
	}))
	mustPrint(rpc(url, "4", "tools/call", map[string]any{
		"name": "query_flight_summary",
		"arguments": map[string]any{"flight_id": "FLIGHT-DEMO-001", "time_range": map[string]any{}},
	}))
	mustPrint(rpc(url, "5", "tools/call", map[string]any{
		"name": "get_flight_health", "arguments": map[string]any{"flight_id": "FLIGHT-DEMO-001"},
	}))
	mustPrint(rpc(url, "6", "tools/call", map[string]any{
		"name": "verify_chain_segment",
		"arguments": map[string]any{"start_hash": rh, "end_hash": rh},
	}))
}

func findRoot() string {
	if v := os.Getenv("INQUIRO_ROOT"); v != "" {
		return v
	}
	wd, err := os.Getwd()
	if err != nil {
		return "."
	}
	for d := wd; d != ""; d = filepath.Dir(d) {
		if _, e := os.Stat(filepath.Join(d, "payloads")); e == nil {
			return d
		}
		if filepath.Dir(d) == d {
			break
		}
	}
	return wd
}

func rpc(url, id, method string, params map[string]any) (map[string]any, error) {
	body := map[string]any{"jsonrpc": "2.0", "id": id, "method": method}
	if params != nil {
		body["params"] = params
	}
	b, _ := json.Marshal(body)
	req, err := http.NewRequest(http.MethodPost, url, bytes.NewReader(b))
	if err != nil {
		return nil, err
	}
	req.Header.Set("Content-Type", "application/json")
	resp, err := http.DefaultClient.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()
	rb, _ := io.ReadAll(resp)
	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("HTTP %d: %s", resp.StatusCode, string(rb))
	}
	var out map[string]any
	if err := json.Unmarshal(rb, &out); err != nil {
		return nil, err
	}
	return out, nil
}

func mustPrint(m map[string]any, err error) {
	if err != nil {
		panic(err)
	}
	b, _ := json.MarshalIndent(m, "", "  ")
	fmt.Println(string(b))
}

func mustMap(m map[string]any, err error) map[string]any {
	if err != nil {
		panic(err)
	}
	return m
}

func liftReceiptHash(api map[string]any) string {
	res, _ := api["result"].(map[string]any)
	if res == nil {
		return ""
	}
	if rh, ok := res["receipt_hash"].(string); ok && rh != "" {
		return rh
	}
	content, _ := res["content"].([]any)
	if len(content) == 0 {
		return ""
	}
	first, _ := content[0].(map[string]any)
	if first == nil {
		return ""
	}
	txt, _ := first["text"].(string)
	var inner map[string]any
	if json.Unmarshal([]byte(txt), &inner) == nil {
		if rh, ok := inner["receipt_hash"].(string); ok {
			return rh
		}
	}
	return ""
=======
//go:build ignore

// Example client: SHA-256 of a canonical attestation.
// Run: go run examples/go/client.go [-v]
// For SHA-256 + BLAKE3, see: go run examples/go/verify_receipt.go <receipt.json>
package main

import (
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"os"
)

type Metadata struct {
	Source  string `json:"source"`
	Version int    `json:"version"`
}

type Payload struct {
	DeviceID  string   `json:"device_id"`
	EventType string   `json:"event_type"`
	Metadata  Metadata `json:"metadata"`
	TenantID  string   `json:"tenant_id"`
}

func main() {
	fmt.Println("Inquiro RNA example — client (stdlib SHA-256 of canonical attestation).")
	fmt.Println("BLAKE3 in Go: see verify_receipt.go (github.com/zeebo/blake3).")
	p := Payload{
		DeviceID:  "DEV-001",
		EventType: "identity_verified",
		Metadata:  Metadata{Source: "sandbox", Version: 1},
		TenantID:  "demo_public",
	}
	b, err := json.Marshal(p)
	if err != nil {
		panic(err)
	}
	if len(os.Args) > 1 && os.Args[1] == "-v" {
		fmt.Println(string(b))
	}
	h := sha256.Sum256(b)
	fmt.Println("sha256", hex.EncodeToString(h[:]))
>>>>>>> 77e9a363fc0946913d50da8c968b2aa40bd8fec2
}
