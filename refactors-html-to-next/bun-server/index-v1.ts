// @ts-ignore
import { file } from "bun";

console.log("Starting Bun server on http://localhost:3000");

const server = Bun.serve({
  port: 3000,
  async fetch(req) {
    const url = new URL(req.url);

    // Endpoint for our converter
    if (url.pathname === "/convert" && req.method === "POST") {
      try {
        // 1. Get the raw HTML from the request body
        const htmlBody = await req.text();

        if (!htmlBody) {
          return new Response("No HTML content provided.", { status: 400 });
        }

        // 2. Define the command to run the Python script
        // We use 'source' to activate the venv first, then run the script
        // This path is relative from where you run the 'bun' command
        const pythonScriptPath = "../python-scripts/convert.py";
        const venvPath = "../python-scripts/venv/bin/activate";

        const cmd = [
            "bash",
            "-c",
            `source ${venvPath} && python ${pythonScriptPath}`
        ];
        
        // Note: On Windows, this would be different (e.g., cmd /c "...")
        // For simplicity, this example assumes a bash-like shell (Linux, macOS, WSL)

        // 3. Spawn the Python process
        const proc = Bun.spawn(cmd, {
          stdin: "pipe", // We will pipe the HTML *in*
          stdout: "pipe", // We will read the result *out*
          stderr: "pipe", // We will read any errors
        });

        // 4. Write the HTML body to the Python script's standard input
        proc.stdin.write(htmlBody);
        proc.stdin.end();

        // 5. Await the results
        const stdout = await new Response(proc.stdout).text();
        const stderr = await new Response(proc.stderr).text();

        // Check if the process exited successfully
        const exitCode = await proc.exited;

        if (exitCode !== 0) {
          console.error("Python script error:", stderr);
          return new Response(
            `Conversion failed. Error: ${stderr}`,
            { status: 500 }
          );
        }

        // 6. Send the converted code back to the client
        return new Response(stdout, {
          headers: { "Content-Type": "text/plain" },
        });

      } catch (error) {
        return new Response(`Server error: ${error.message}`, { status: 500 });
      }
    }

    return new Response("Not Found. POST to /convert", { status: 404 });
  },
});

console.log(`Bun server running at ${server.url}`);