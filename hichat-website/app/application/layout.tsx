import type { Metadata } from "next";

const TITLE = "Get Started — Download & Install RealChat";
const DESCRIPTION =
  "Download the RealChat (真聊) desktop assistant for macOS or set it up with Quick Start, Docker or a manual install, then automate your WeChat messages in minutes.";

export const metadata: Metadata = {
  title: { absolute: TITLE },
  description: DESCRIPTION,
  alternates: { canonical: "/application" },
  openGraph: {
    type: "website",
    url: "https://realchat.work/application",
    siteName: "RealChat",
    title: TITLE,
    description: DESCRIPTION,
  },
  twitter: {
    card: "summary_large_image",
    title: TITLE,
    description: DESCRIPTION,
  },
};

export default function ApplicationLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return children;
}
