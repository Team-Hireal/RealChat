/**
 * Zypher Agent Service for RealChat
 * Deno-based AI agent that integrates with WeChat via Flask backend
 */

import {
  AnthropicModelProvider,
  createZypherContext,
  ZypherAgent,
} from "@zypher/agent";
import { eachValueFrom } from "rxjs-for-await";

// Helper function to load AI settings from parent directory
async function loadAISettings() {
  try {
    const settingsPath = "../ai_settings.json";
    const settingsText = await Deno.readTextFile(settingsPath);
    const settings = JSON.parse(settingsText);
    return settings;
  } catch (error) {
    console.warn("⚠️  Could not load ai_settings.json, falling back to environment variables");
    return null;
  }
}

// Helper function to safely get environment variables
function getRequiredEnv(name: string, fallback?: string): string {
  const value = Deno.env.get(name) || fallback;
  if (!value) {
    throw new Error(`Environment variable ${name} is not set and no fallback provided`);
  }
  return value;
}

// HTTP server for API endpoints
async function startHttpServer(agent: ZypherAgent, defaultModel: string) {
  const port = parseInt(Deno.env.get("ZYPHER_PORT") || "8000");

  const handler = async (req: Request): Promise<Response> => {
    const url = new URL(req.url);

    // CORS headers
    const corsHeaders = {
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type",
    };

    // Handle CORS preflight
    if (req.method === "OPTIONS") {
      return new Response(null, { headers: corsHeaders });
    }

    // Health check endpoint
    if (url.pathname === "/health") {
      return new Response(
        JSON.stringify({ status: "ok", service: "zypher-agent" }),
        {
          headers: { ...corsHeaders, "Content-Type": "application/json" },
        }
      );
    }

    // Chat endpoint
    if (url.pathname === "/api/chat" && req.method === "POST") {
      try {
        const body = await req.json();
        const { message, model, history } = body;

        if (!message) {
          return new Response(
            JSON.stringify({ success: false, error: "Message is required" }),
            {
              status: 400,
              headers: { ...corsHeaders, "Content-Type": "application/json" },
            }
          );
        }

        // Build context from history
        let contextPrompt = "";
        if (history && history.length > 0) {
          contextPrompt = "Previous conversation:\n";
          for (const msg of history) {
            if (msg.role === "user") {
              contextPrompt += `User: ${msg.content}\n`;
            } else if (msg.role === "assistant") {
              contextPrompt += `Assistant: ${msg.content}\n`;
            }
          }
          contextPrompt += "\n";
        }

        // Count user's words for length matching
        const userWordCount = message.trim().split(/\s+/).length;
        let targetWords: string;
        if (userWordCount <= 5) {
          targetWords = "1-5 words";
        } else if (userWordCount <= 15) {
          targetWords = "6-15 words";
        } else {
          targetWords = "15-25 words";
        }

        // Build task prompt - system identity is handled by systemPromptLoader
        const fullPrompt = `${contextPrompt}User sent ${userWordCount} words. Respond with ${targetWords} ONLY. Keep it SHORT and match their vibe.

User message: ${message}`;

        // Run the agent task (model is set at initialization)
        console.log(`[Zypher] Processing message with default model`);

        const event$ = agent.runTask(fullPrompt);

        // Collect the response - convert Observable to async iterable
        let response = "";
        for await (const event of eachValueFrom(event$)) {
          if (event.type === "text") {
            response += event.content;  // FIXED: Use 'content' not 'text'
          }
        }

        // Ensure [Zypher] prefix
        if (!response.trim().startsWith("[Zypher]")) {
          response = `[Zypher] ${response}`;
        }

        // Remove line breaks for WeChat
        response = response.replace(/\n/g, " ").replace(/\r/g, " ");
        response = response.split(/\s+/).join(" ");

        console.log(`[Zypher] Response: ${response.substring(0, 100)}...`);

        return new Response(
          JSON.stringify({
            success: true,
            response: response,
            model: "zypher",
          }),
          {
            headers: { ...corsHeaders, "Content-Type": "application/json" },
          }
        );
      } catch (error) {
        console.error("[Zypher] Error processing chat:", error);
        return new Response(
          JSON.stringify({
            success: false,
            error: error.message || "Failed to process message",
          }),
          {
            status: 500,
            headers: { ...corsHeaders, "Content-Type": "application/json" },
          }
        );
      }
    }

    // 404 for unknown routes
    return new Response(JSON.stringify({ error: "Not found" }), {
      status: 404,
      headers: { ...corsHeaders, "Content-Type": "application/json" },
    });
  };

  console.log(`🚀 Zypher Agent HTTP server starting on port ${port}...`);
  await Deno.serve({ port }, handler);
}

// Main initialization
async function main() {
  console.log("🤖 Initializing Zypher Agent for RealChat...");

  try {
    let apiKey: string;
    let baseURL: string;
    let defaultModel: string;

    // Priority 1: Check ZYPHER_* environment variables first (from .env file)
    // These use ZYPHER_ prefix to avoid conflicts with system ANTHROPIC_* variables
    const zypherApiKey = Deno.env.get("ZYPHER_API_KEY");
    const zypherBaseURL = Deno.env.get("ZYPHER_BASE_URL");
    const zypherModel = Deno.env.get("ZYPHER_MODEL");

    if (zypherApiKey) {
      // Use ZYPHER_* environment variables (highest priority)
      console.log("✅ Using ZYPHER_* environment variables from .env file");
      apiKey = zypherApiKey;
      baseURL = zypherBaseURL || "https://api.anthropic.com";
      defaultModel = zypherModel || "claude-sonnet-4-5-20250929";
      console.log(`   API Base URL: ${baseURL}`);
      console.log(`   Default Model: ${defaultModel}`);
    } else {
      // Priority 2: Check ANTHROPIC_* environment variables
      const envApiKey = Deno.env.get("ANTHROPIC_API_KEY");
      const envBaseURL = Deno.env.get("ANTHROPIC_BASE_URL");
      const envModel = Deno.env.get("ANTHROPIC_MODEL");

      if (envApiKey) {
        // Use ANTHROPIC_* environment variables
        console.log("✅ Using ANTHROPIC_* environment variables");
        apiKey = envApiKey;
        baseURL = envBaseURL || "https://api.anthropic.com";
        defaultModel = envModel || "claude-sonnet-4-5-20250929";
        console.log(`   API Base URL: ${baseURL}`);
        console.log(`   Default Model: ${defaultModel}`);
      } else {
        // Priority 3: Fall back to ai_settings.json (shared with Flask backend)
        const aiSettings = await loadAISettings();

        if (aiSettings) {
          console.log("✅ Loaded AI settings from ai_settings.json");
          apiKey = aiSettings.api_key;
          baseURL = aiSettings.base_url || "https://api.anthropic.com";
          defaultModel = aiSettings.model || "claude-sonnet-4-5-20250929";
          console.log(`   API Base URL: ${baseURL}`);
          console.log(`   Default Model: ${defaultModel}`);
        } else {
          throw new Error("No API configuration found. Please set ZYPHER_API_KEY environment variable or create ai_settings.json");
        }
      }
    }

    // Initialize the agent execution context
    const zypherContext = await createZypherContext(Deno.cwd());

    // IMPORTANT: Override system ANTHROPIC_* environment variables
    // This ensures our ZYPHER_* settings take priority
    Deno.env.set("ANTHROPIC_API_KEY", apiKey);
    Deno.env.set("ANTHROPIC_BASE_URL", baseURL);

    // Create the agent with Anthropic provider using shared configuration
    // Override the default system prompt to use our WeChat assistant identity
    const agent = new ZypherAgent(
      zypherContext,
      new AnthropicModelProvider({
        model: defaultModel,
        anthropicClientOptions: {
          apiKey: apiKey,
          baseURL: baseURL,
        }
      }),
      {
        overrides: {
          systemPromptLoader: async () => `You are Zypher, a WeChat messaging assistant.

CRITICAL RULES:
1. Always start with '[Zypher]'
2. ONE LINE ONLY - no line breaks, no lists, no paragraphs
3. Match the user's energy and emotional tone
4. Be casual and conversational like texting
5. When asked who you are, identify yourself as "Zypher"
6. NEVER identify as any other AI (not Kiro, not Claude, not any other name)
7. You are NOT a coding assistant - you are a friendly WeChat chat companion`,
        },
      }
    );

    console.log("✅ Zypher Agent initialized successfully");

    // Start HTTP server (pass default model for reference)
    await startHttpServer(agent, defaultModel);
  } catch (error) {
    console.error("❌ Failed to initialize Zypher Agent:", error);
    Deno.exit(1);
  }
}

// Run the main function
if (import.meta.main) {
  main();
}
