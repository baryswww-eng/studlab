import path from "node:path";
import type { NextConfig } from "next";
import createNextIntlPlugin from "next-intl/plugin";

const withNextIntl = createNextIntlPlugin("./src/i18n/request.ts");

const nextConfig: NextConfig = {
  // Self-contained server bundle for the Docker image.
  output: "standalone",
  // The monorepo root; prevents Next from guessing the workspace root
  // from lockfiles in parent folders.
  outputFileTracingRoot: path.join(__dirname),
  poweredByHeader: false,
  // The site used to have /kk and /ru prefixes; it is Russian-only now.
  async redirects() {
    return [
      { source: "/kk", destination: "/", permanent: true },
      { source: "/kk/:path*", destination: "/:path*", permanent: true },
      { source: "/ru", destination: "/", permanent: true },
      { source: "/ru/:path*", destination: "/:path*", permanent: true },
    ];
  },
  turbopack: {
    root: path.join(__dirname),
    rules: {
      "*.css": {
        loaders: ["@tailwindcss/turbopack"],
        as: "*.css",
      },
    },
  },
};

export default withNextIntl(nextConfig);
