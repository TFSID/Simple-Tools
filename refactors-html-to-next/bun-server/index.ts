console.log("Starting Bun API gateway on http://localhost:3000");

// The URL for our new Python microservice
const PYTHON_SERVER_URL = "http://localhost:5000/convert";

const server = Bun.serve({
  port: 3000,
  async fetch(req) {
    const url = new URL(req.url);

    if (url.pathname === "/convert" && req.method === "POST") {
      try {
        // 1. Get the raw HTML from the request body
        const htmlBody = await req.text();

        if (!htmlBody) {
          return new Response("No HTML content provided.", { status: 400 });
        }

        // 2. Forward the request to the Python server using fetch
        console.log("Forwarding request to Python server...");
        const pythonResponse = await fetch(PYTHON_SERVER_URL, {
          method: "POST",
          body: htmlBody,
          headers: {
            // Send as plain text, as our Python server expects
            "Content-Type": "text/plain", 
          },
        });

        // 3. Check if the Python server request was successful
        if (!pythonResponse.ok) {
          const errorText = await pythonResponse.text();
          console.error("Python server error:", errorText);
          return new Response(
            `Error from conversion service: ${errorText}`,
            { status: pythonResponse.status }
          );
        }

        // 4. Stream the response from the Python server back to the client
        const convertedCode = await pythonResponse.text();

        return new Response(convertedCode, {
          headers: { "Content-Type": "text/plain" },
        });

      } catch (error) {
        // Handle network errors (e.g., if Python server is down)
        if (error.code === 'ECONNREFUSED') {
            console.error("Error: Connection refused. Is the Python server running?");
            return new Response("Conversion service is offline.", { status: 503 });
        }
        return new Response(`Server error: ${error.message}`, { status: 500 });
      }
    }

    return new Response("Not Found. POST to /convert", { status: 404 });
  },
});

console.log(`Bun server running at ${server.url}`);