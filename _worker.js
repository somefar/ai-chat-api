export default {
  async fetch(request, env, ctx) {
    const corsHeaders = {
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type",
    };

    // Handle CORS preflight requests
    if (request.method === "OPTIONS") {
      return new Response(null, {
        headers: corsHeaders
      });
    }

    const url = new URL(request.url);
    if (url.pathname === "/api/chat") {
      if (request.method !== "POST") {
        return new Response(JSON.stringify({ error: "Method not allowed" }), {
          status: 405,
          headers: {
            "Content-Type": "application/json",
            ...corsHeaders
          }
        });
      }

      try {
        const body = await request.json();
        const { message, model } = body;

        if (!message || !model) {
          return new Response(JSON.stringify({ error: "Missing message or model" }), {
            status: 400,
            headers: {
              "Content-Type": "application/json",
              ...corsHeaders
            }
          });
        }

        let response;
        if (model === "gpt") {
          const openaiResponse = await fetch("https://api.openai.com/v1/chat/completions", {
            method: "POST",
            headers: {
              "Authorization": `Bearer ${env.OPENAI_API_KEY}`,
              "Content-Type": "application/json"
            },
            body: JSON.stringify({
              model: "gpt-3.5-turbo",
              messages: [{ role: "user", content: message }]
            })
          });
          const data = await openaiResponse.json();
          response = { response: data.choices[0].message.content };
        }
        else if (model === "claude") {
          const claudeResponse = await fetch("https://api.anthropic.com/v1/messages", {
            method: "POST",
            headers: {
              "x-api-key": env.ANTHROPIC_API_KEY,
              "anthropic-version": "2023-06-01",
              "Content-Type": "application/json"
            },
            body: JSON.stringify({
              model: "claude-3-sonnet-20240229",
              max_tokens: 1024,
              messages: [{ role: "user", content: message }]
            })
          });
          const data = await claudeResponse.json();
          response = { response: data.content[0].text };
        }
        else if (model === "deepseek") {
          const deepseekResponse = await fetch("https://api.deepseek.com/v1/chat/completions", {
            method: "POST",
            headers: {
              "Authorization": `Bearer ${env.DEEPSEEK_API_KEY}`,
              "Content-Type": "application/json"
            },
            body: JSON.stringify({
              model: "deepseek-chat",
              messages: [{ role: "user", content: message }]
            })
          });
          const data = await deepseekResponse.json();
          response = { response: data.choices[0].message.content };
        }
        else {
          return new Response(JSON.stringify({ error: "Invalid model specified" }), {
            status: 400,
            headers: {
              "Content-Type": "application/json",
              ...corsHeaders
            }
          });
        }

        return new Response(JSON.stringify(response), {
          headers: {
            "Content-Type": "application/json",
            ...corsHeaders
          }
        });
      } catch (err) {
        return new Response(JSON.stringify({ error: err.message }), {
          status: 500,
          headers: {
            "Content-Type": "application/json",
            ...corsHeaders
          }
        });
      }
    }

    // Handle requests to the root path
    if (url.pathname === "/" || url.pathname === "") {
      // Serve the static content
      return env.ASSETS.fetch(request);
    }

    return new Response(JSON.stringify({ error: "Not found" }), {
      status: 404,
      headers: {
        "Content-Type": "application/json",
        ...corsHeaders
      }
    });
  }
}; 