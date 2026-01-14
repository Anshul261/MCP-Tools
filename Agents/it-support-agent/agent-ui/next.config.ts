import type { NextConfig } from 'next'

const nextConfig: NextConfig = {
  devIndicators: false,
  async rewrites() {
    return [
      {
        source: '/api/proxy/:path*',
        destination: 'http://127.0.0.1:7777/:path*',
      },
    ]
  },
}

export default nextConfig
