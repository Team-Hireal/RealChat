import { ImageResponse } from "next/og";

export const alt = "RealChat (真聊) — AI assistant that supercharges WeChat";
export const size = { width: 1200, height: 630 };
export const contentType = "image/png";

export default function OpengraphImage() {
  return new ImageResponse(
    (
      <div
        style={{
          width: "100%",
          height: "100%",
          display: "flex",
          flexDirection: "column",
          justifyContent: "center",
          padding: "80px",
          background: "linear-gradient(135deg, #06ad56 0%, #07c160 55%, #95ec69 100%)",
          color: "white",
          fontFamily: "sans-serif",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", marginBottom: 40 }}>
          <div
            style={{
              width: 96,
              height: 96,
              borderRadius: 24,
              background: "rgba(255,255,255,0.2)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              fontSize: 56,
              fontWeight: 700,
            }}
          >
            R
          </div>
          <div style={{ marginLeft: 28, fontSize: 64, fontWeight: 700 }}>RealChat</div>
        </div>
        <div style={{ fontSize: 76, fontWeight: 800, lineHeight: 1.1 }}>Supercharge Your WeChat</div>
        <div style={{ marginTop: 28, fontSize: 34, opacity: 0.92 }}>
          Triage, reply, and stay on top of chats — without leaving WeChat
        </div>
        <div style={{ marginTop: 48, fontSize: 28, opacity: 0.85 }}>realchat.work</div>
      </div>
    ),
    size
  );
}
