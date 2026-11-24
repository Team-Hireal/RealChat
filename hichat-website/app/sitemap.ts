import type { MetadataRoute } from "next";

const SITE_URL = "https://realchat.work";

export default function sitemap(): MetadataRoute.Sitemap {
  return [
    { url: `${SITE_URL}/`, changeFrequency: "weekly", priority: 1 },
    { url: `${SITE_URL}/application`, changeFrequency: "monthly", priority: 0.8 },
  ];
}
