/* --------------------------------------------------------------------------------------------
 * Copyright (c) Microsoft Corporation. All rights reserved.
 * Licensed under the MIT License. See License.txt in the project root for license information.
 * ------------------------------------------------------------------------------------------ */

import { ExtensionContext, workspace, commands, window } from 'vscode';
import { LanguageClient, LanguageClientOptions, ServerOptions } from 'vscode-languageclient';
import { ChildProcess, spawn } from "child_process";

let client: LanguageClient;
let server: ChildProcess;

function startServer(server_path: string) {
    const serverOptions: ServerOptions = async (): Promise<ChildProcess> => {
        server = spawn(server_path);
        window.showInformationMessage("Started aecor server: " + server_path);
        return server;
    };

    const clientOptions: LanguageClientOptions = {
        diagnosticCollectionName: 'aecorlsp',
        // Register the server for plain text documents
        documentSelector: [
            {
                pattern: '**/*.ae',
            }
        ],
    };

    client = new LanguageClient('aecorlsp', 'Aecor LSP Client', serverOptions, clientOptions);
    client.start();
}

async function killServer() : Promise<void> {
    await client.stop();
    server.kill();
}

export function activate(context: ExtensionContext) {
    const server_path = context.asAbsolutePath("server.sh");
    startServer(server_path);
    context.subscriptions.push(commands.registerCommand('aecorlsp.restartServer', async () => {
        await killServer();
        startServer(server_path);
    }));
}

export function deactivate(): Thenable<void> | undefined {
    return killServer();
}
