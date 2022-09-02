# Toy LSP implementation

Just figuring out how these things work

## Architecture

For now, the actual LSP server is implemented in Python (`lsp.py`), which calls out to an `aecor` executable (`find.ae`) to query type / location information. It is _not_ a long-running process that retains state of the program.

There is an in-progress rewrite of the server in aecor (`main.ae`), however due to lack of good memory management, it is not currently feasible since it would have
massive memory leaks when run for a long time.

## Running (Debug / Development)

First, compile and run the `aecor` executable. You will need [aecor](https://github.com/mustafaquraish/aecor) installed and set up on your system.

```bash
$ aecor find.ae -o find # Important, name this `find`
$ python3 lsp.py    # Run the server, on port 3333
```

Then, open the `vscode-ext` folder in VSCode and run the extension. Launch configurations are already provided. If everything goes right, a `Host Extension` winho will be opened, and it will connect to the Python server.