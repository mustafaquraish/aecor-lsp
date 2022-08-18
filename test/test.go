package main

import (
	"log"
	"path/filepath"

	"github.com/dbanck/go-lsp-test/client"
	p "github.com/dbanck/go-lsp-test/protocol"
)

func main() {
	testDir, err := filepath.Abs(".")
	if err != nil {
		log.Fatal(err)
	}
	lsc, err := client.NewClient("localhost:3333", testDir)
	if err != nil {
        log.Fatal(err)
	}
	defer lsc.Close()

	doc, err := lsc.OpenDoc("test.go", "Go")
	if err != nil {
        log.Fatal(err)
	}

	result, err := lsc.GetCompletions(doc, p.Position{
		Line:      5,
		Character: 5,
	})
	if err != nil {
        log.Fatal(err)
	}

	log.Printf("Got completions %#v\n", result)
}