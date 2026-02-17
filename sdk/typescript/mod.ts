/**
 * RealChat Agent SDK for TypeScript/Deno
 * Connect any LLM/agent to WeChat through the RealChat universal bridge.
 *
 * Usage:
 *   import { AgentBridge } from "./mod.ts";
 *
 *   const bridge = new AgentBridge({ name: "MyAgent", port: 9000 });
 *
 *   bridge.onMessage(async (message, context) => {
 *     return `[MyAgent] ${await myLLM.respond(message)}`;
 *   });
 *
 *   bridge.start();
 */

export { AgentBridge } from "./src/bridge.ts";
export type { AgentConfig, MessageContext, MessageHandler } from "./src/bridge.ts";
