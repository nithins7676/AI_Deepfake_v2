import type React from "react"
import type { Metadata } from "next"
import { Inter, Orbitron, Audiowide, Rajdhani, Exo_2 } from "next/font/google"
import { Analytics } from "@vercel/analytics/next"
import { AIBackground } from "@/components/ai-background"
import { AuthProvider } from "@/contexts/auth-context"
import "./globals.css"

const _inter = Inter({ subsets: ["latin"], variable: "--font-inter" })
const _orbitron = Orbitron({ subsets: ["latin"], variable: "--font-orbitron" })
const _audiowide = Audiowide({ weight: "400", subsets: ["latin"], variable: "--font-audiowide" })
const _rajdhani = Rajdhani({ weight: ["400", "500", "600", "700"], subsets: ["latin"], variable: "--font-rajdhani" })
const _exo2 = Exo_2({ subsets: ["latin"], variable: "--font-exo2" })

export const metadata: Metadata = {
  title: "UNMASK — Deepfake Detection System",
  description: "Reveal the truth behind digital illusions with AI-powered deepfake detection.",
  generator: "v0.app",
  icons: {
    icon: [
      {
        url: "/icon-light-32x32.png",
        media: "(prefers-color-scheme: light)",
      },
      {
        url: "/icon-dark-32x32.png",
        media: "(prefers-color-scheme: dark)",
      },
      {
        url: "/icon.svg",
        type: "image/svg+xml",
      },
    ],
    apple: "/apple-icon.png",
  },
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en" className="dark">
      <body
        className={`${_inter.variable} ${_orbitron.variable} ${_audiowide.variable} ${_rajdhani.variable} ${_exo2.variable} font-sans antialiased min-h-screen`}
      >
        <AuthProvider>
          <AIBackground />
          <div className="relative z-10">{children}</div>
          <Analytics />
        </AuthProvider>
      </body>
    </html>
  )
}
