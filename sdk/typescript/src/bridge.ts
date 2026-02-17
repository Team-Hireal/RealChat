/**
 * AgentBridge - Core SDK class for connecting agents to RealChat.
 * Works with both Deno and Node.js.
 */

export interface AgentConfig {
  name: string;
  port?: number;
  gatewayUrl?: string;
  description?: string;
  capabilities?: Record<string, boolean>;
}

export interface MessageContext {
  history: Array<{ role: string; content: string }>;
  context: Record<string, unknown>;
  model?: string;
}

export type MessageHandler = (
  message: string,
  context: MessageContext
) => Promise<string> | string;

export class AgentBridge {
  private name: string;
  private port: number;
  private gatewayUrl: string;
  private description: string;
  private prefix: string;
  private capabilities: Record<string, boolean>;
  private handler: MessageHandler | null = null;
  private startTime = Date.now();
  private abortController: AbortController | null = null;

  constructor(config: AgentConfig) {
    this.name = config.name.toLowerCase().trim();
    this.port = config.port ?? 9000;
    this.gatewayUrl = config.gatewayUrl ?? "http://localhost:5001";
    this.description = config.description ?? `${config.name} agent`;
    this.prefix = `[${config.name.charAt(0).toUpperCase() + config.name.slice(1)}]`;
    this.capabilities = config.capabilities ?? {};
  }

  onMessage(handler: MessageHandler): void {
    this.handler = handler;
  }

  private formatResponse(text: string): string {
    text = text.replace(/\n/g, " ").replace(/\r/g, " ");
    text = text.split(/\s+/).join(" ");
    if (!text.startsWith(this.prefix)) {
      text = `${this.prefix} ${text}`;
    }
    return text;
  }

  private async registerWithGateway(): Promise<void> {
    try {
      const resp = await fetch(`${this.gatewayUrl}/api/agents/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          name: this.name,
          url: `http://localhost:${this.port}`,
          port: this.port,
          description: this.description,
          prefix: this.prefix,
          capabilities: this.capabilities,
          health_endpoint: "/health",
          chat_endpoint: "/api/chat",
        }),
      });
      const data = await resp.json();
      if (data.success) {
        console.log(`✅ Registered with gateway at ${this.gatewayUrl}`);
      } else {
        console.warn(`⚠️ Registration response: ${JSON.stringify(data)}`);
      }
    } catch (e) {
      console.warn(`⚠️ Could not register with gateway (is it running?): ${e}`);
    }
  }

  private async deregisterFromGateway(): Promise<void> {
    try {
      await fetch(`${this.gatewayUrl}/api/agents/${this.name}`, {
        method: "DELETE",
      });
      console.log("Deregistered from gateway");
    } catch {
      // Best effort on shutdown
    }
  }

  private corsHeaders = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
    "Content-Type": "application/json",
  };

  private jsonResponse(data: unknown, status = 200): Response {
    return new Response(JSON.stringify(data), {
      status,
      headers: this.corsHeaders,
    });
  }

  private async handleRequest(req: Request): Promise<Response> {
    const url = new URL(req.url);

    if (req.method === "OPTIONS") {
      return this.jsonResponse({});
    }

    if (url.pathname === "/health" && req.method === "GET") {
      return this.jsonResponse({
        status: "ok",
        service: this.name,
        version: "1.0.0",
        uptime: (Date.now() - this.startTime) / 1000,
      });
    }

    if (url.pathname === "/api/chat" && req.method === "POST") {
      if (!this.handler) {
        return this.jsonResponse(
          { success: false, error: "No handler registered" },
          500
        );
      }

      try {
        const body = await req.json();
        const message = body.message;

        if (!message) {
          return this.jsonResponse(
            { success: false, error: "Message required" },
            400
          );
        }

        const context: MessageContext = {
          history: body.history ?? [],
          context: body.context ?? {},
          model: body.model,
        };

        const response = await this.handler(message, context);
        const formatted = this.formatResponse(response);

        return this.jsonResponse({
          success: true,
          response: formatted,
          model: this.name,
          agent: this.name,
        });
      } catch (e: unknown) {
        const errorMsg = e instanceof Error ? e.message : String(e);
        return this.jsonResponse(
          { success: false, error: errorMsg },
          500
        );
      }
    }

    return this.jsonResponse({ error: "Not found" }, 404);
  }

  async start(): Promise<void> {
    if (!this.handler) {
      throw new Error("No message handler registered. Use bridge.onMessage()");
    }

    // Register with gateway
    await this.registerWithGateway();

    // Handle shutdown
    this.abortController = new AbortController();

    const onSignal = async () => {
      console.log(`\nShutting down ${this.name}...`);
      await this.deregisterFromGateway();
      this.abortController?.abort();
    };

    Deno.addSignalListener("SIGINT", onSignal);
    Deno.addSignalListener("SIGTERM", onSignal);

    console.log(`🤖 ${this.name} agent running on http://localhost:${this.port}`);
    console.log(`   Health: http://localhost:${this.port}/health`);
    console.log(`   Chat:   http://localhost:${this.port}/api/chat`);

    await Deno.serve(
      { port: this.port, signal: this.abortController.signal },
      (req) => this.handleRequest(req)
    );
  }
}
