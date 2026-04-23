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
}
