# Toy LSP implementation

Just figuring out how these things work

## Running

First, compile and run the LSP server. You will need [aecor](https://github.com/mustafaquraish/aecor) installed and set up on your system.

```bash
$ aecor main.ae -o lsp
$ ./lsp
```
Run the simple go client to connect to the server and request a completion.

```bash
$ cd test
$ go run test.go
```