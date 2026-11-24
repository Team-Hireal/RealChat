import type { MetadataRoute } from "next";

export default function robots(): MetadataRoute.Robots {
  return {
    rules: [{ userAgent: "*", allow: "/" }],
    sitemap: "https://realchat.work/sitemap.xml",
    host: "https://realchat.work",
  };
}
