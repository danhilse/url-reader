import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* config options here */
};

export const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:10000';

export default nextConfig;
