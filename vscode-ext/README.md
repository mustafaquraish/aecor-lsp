# Generic LSP Client for VS Code

_Originally from: https://gitlab.com/torokati44/vscode-glspc_

This is a simple VSCode LSP client that communicates with the `lsp.py` server in the above directory. 

Note that this extension currently expects I/O to be done through stdin and stdout, but since the Python server uses sockets (to leave stdout for debugging), the extension uses the `server.sh` script here to wrap the Python server with `nc` to send I/O through stdin and stdout.

