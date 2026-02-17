/**
 * Example: Simple Echo Agent using RealChat SDK (Deno)
 * Demonstrates the minimal code needed to connect any agent to WeChat.
 *
 * Run:
 *   deno run --allow-net examples/simple_agent_deno.ts
 */

import { AgentBridge } from "../sdk/typescript/mod.ts";

const bridge = new AgentBridge({
  name: "echo",
  port: 9000,
  description: "Simple echo agent for testing",
  capabilities: { conversation_history: true, length_matching: true },
});

bridge.onMessage(async (message, context) => {
  const turnCount = Math.floor(context.history.length / 2) + 1;
  const wordCount = message.split(/\s+/).length;

  if (wordCount <= 3) {
    return `Got it: ${message}`;
  } else if (wordCount <= 10) {
    return `You said '${message}' — interesting! (turn ${turnCount})`;
  } else {
    return `That's a lot to unpack! Let me think about '${message.slice(0, 50)}...'`;
  }
});

bridge.start();
