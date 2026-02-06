// Quick test to verify configuration loading
async function testConfig() {
  try {
    const settingsPath = "../ai_settings.json";
    const settingsText = await Deno.readTextFile(settingsPath);
    const settings = JSON.parse(settingsText);

    console.log("✅ Successfully loaded ai_settings.json");
    console.log("   API Key:", settings.api_key ? "SET (hidden)" : "NOT SET");
    console.log("   Base URL:", settings.base_url || "NOT SET");
    console.log("   Model:", settings.model || "NOT SET");
  } catch (error) {
    console.error("❌ Failed to load ai_settings.json:", error.message);
  }
}

testConfig();
