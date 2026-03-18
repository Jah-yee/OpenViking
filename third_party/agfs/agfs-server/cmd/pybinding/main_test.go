package main

import (
	"encoding/json"
	"fmt"
	"os"
	"testing"
	"time"

	"github.com/c4pt0r/agfs/agfs-server/pkg/filesystem"
)

// CGO_ENABLED=1 go test -v main.go main_test.go

// TestAGFS_Read_TOS_Logic tests the core logic of AGFS_Read (using globalFS.Read)
// with the configuration from ov-byted-tos.conf.
func TestAGFS_Read_TOS_Logic(t *testing.T) {
	// 1. Read configuration from OPENVIKING_CONFIG_FILE environment variable
	confPath := os.Getenv("OPENVIKING_CONFIG_FILE")
	confData, err := os.ReadFile(confPath)
	if err != nil {
		t.Fatalf("failed to read config file: %v", err)
	}

	var fullConfig map[string]interface{}
	if err := json.Unmarshal(confData, &fullConfig); err != nil {
		t.Fatalf("failed to unmarshal config: %v", err)
	}

	storage := fullConfig["storage"].(map[string]interface{})
	agfs := storage["agfs"].(map[string]interface{})
	s3Config := agfs["s3"].(map[string]interface{})

	// 2. Map configuration parameters for s3fs plugin
	mappedConfig := make(map[string]interface{})
	for k, v := range s3Config {
		switch k {
		case "access_key":
			mappedConfig["access_key_id"] = v
		case "secret_key":
			mappedConfig["secret_access_key"] = v
		case "use_ssl":
			mappedConfig["disable_ssl"] = !(v.(bool))
		default:
			mappedConfig[k] = v
		}
	}

	// 3. Mount S3 plugin using the globalFS initialized in main.go
	mountPath := "/s3"
	err = globalFS.MountPlugin("s3fs", mountPath, mappedConfig)
	if err != nil {
		t.Fatalf("Failed to mount s3fs: %v", err)
	}
	fmt.Printf("Mounted s3fs at %s\n", mountPath)

	// 4. Prepare test data with unique path
	testPath := fmt.Sprintf("/s3/test_read_logic_%d.txt", time.Now().Unix())
	testContent := "test data for pybinding s3 read logic"
	contentBytes := []byte(testContent)

	// Write data using globalFS with create and truncate flags
	n, err := globalFS.Write(testPath, contentBytes, -1, filesystem.WriteFlagCreate|filesystem.WriteFlagTruncate)
	if err != nil {
		t.Fatalf("Failed to write to s3: %v", err)
	}
	fmt.Printf("Written %d bytes\n", n)

	// 5. Test the core logic of AGFS_Read (fs.Read)
	// This corresponds to main.go:216
	data, err := globalFS.Read(testPath, 0, int64(len(contentBytes)))
	if err != nil && err.Error() != "EOF" {
		t.Fatalf("fs.Read failed: %v", err)
	}

	// Verify the data returned by fs.Read
	if string(data) != testContent {
		t.Errorf("Content mismatch: expected %q, got %q", testContent, string(data))
	} else {
		fmt.Printf("Read logic verification successful: %s\n", string(data))
	}
}
