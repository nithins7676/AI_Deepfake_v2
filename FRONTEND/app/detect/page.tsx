"use client"

import Link from "next/link"
import Image from "next/image"
import { useRouter } from "next/navigation"
import { ImageIcon, Video, ArrowLeft, Sparkles, LogOut } from "lucide-react"
import { GlassCard } from "@/components/ui/glass-card"
import { ProtectedRoute } from "@/components/protected-route"
import { useAuth } from "@/contexts/auth-context"
import { GlowButton } from "@/components/ui/glow-button"

function DetectPageContent() {
  const router = useRouter()
  const { user, signOut } = useAuth()

  return (
    <main className="min-h-screen bg-background flex items-center justify-center px-4 relative overflow-hidden">
      <div className="absolute inset-0 pointer-events-none">
        <Image src="/images/detect-bg.jpg" alt="" fill className="object-cover opacity-[0.1]" priority />
        <div className="absolute inset-0 bg-gradient-to-t from-background via-background/85 to-background" />
      </div>

      {/* Base gradients */}
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,rgba(59,130,246,0.1),transparent_70%)]" />
      <div className="absolute top-0 left-1/3 w-[500px] h-[500px] bg-primary/5 rounded-full blur-3xl" />
      <div className="absolute bottom-0 right-1/3 w-[500px] h-[500px] bg-accent/5 rounded-full blur-3xl" />

      {/* Animated orbs */}
      <div className="absolute top-20 left-20 w-32 h-32 bg-primary/15 rounded-full blur-2xl animate-float" />
      <div className="absolute bottom-20 right-20 w-40 h-40 bg-accent/15 rounded-full blur-2xl animate-float-delayed" />
      <div className="absolute top-1/2 left-10 w-24 h-24 bg-primary/10 rounded-full blur-xl animate-float-slow" />
      <div className="absolute top-1/3 right-10 w-28 h-28 bg-accent/10 rounded-full blur-xl animate-float" />

      {/* Circuit pattern */}
      <svg className="absolute inset-0 w-full h-full opacity-[0.04]" xmlns="http://www.w3.org/2000/svg">
        <defs>
          <pattern id="circuit" x="0" y="0" width="100" height="100" patternUnits="userSpaceOnUse">
            <path
              d="M0 50 H40 M60 50 H100 M50 0 V40 M50 60 V100"
              stroke="currentColor"
              strokeWidth="1"
              fill="none"
              className="text-primary"
            />
            <circle cx="50" cy="50" r="4" fill="currentColor" className="text-primary" />
            <circle cx="0" cy="50" r="2" fill="currentColor" className="text-accent" />
            <circle cx="100" cy="50" r="2" fill="currentColor" className="text-accent" />
            <circle cx="50" cy="0" r="2" fill="currentColor" className="text-primary" />
            <circle cx="50" cy="100" r="2" fill="currentColor" className="text-primary" />
          </pattern>
        </defs>
        <rect width="100%" height="100%" fill="url(#circuit)" />
      </svg>

      {/* Horizontal scan line */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute w-full h-px bg-gradient-to-r from-transparent via-primary/40 to-transparent animate-scanline-move" />
        <div
          className="absolute w-full h-px bg-gradient-to-r from-transparent via-accent/30 to-transparent animate-scanline-move"
          style={{ animationDelay: "2s" }}
        />
      </div>

      {/* Corner brackets */}
      <div className="absolute top-6 left-6 w-16 h-16 border-l-2 border-t-2 border-primary/40 rounded-tl-lg" />
      <div className="absolute top-6 right-6 w-16 h-16 border-r-2 border-t-2 border-accent/40 rounded-tr-lg" />
      <div className="absolute bottom-6 left-6 w-16 h-16 border-l-2 border-b-2 border-accent/40 rounded-bl-lg" />
      <div className="absolute bottom-6 right-6 w-16 h-16 border-r-2 border-b-2 border-primary/40 rounded-br-lg" />

      {/* Floating particles */}
      {[...Array(6)].map((_, i) => (
        <div
          key={i}
          className="absolute w-1 h-1 rounded-full animate-float-particle"
          style={{
            left: `${15 + i * 15}%`,
            top: `${20 + (i % 3) * 25}%`,
            backgroundColor: i % 2 === 0 ? "rgb(59, 130, 246)" : "rgb(168, 85, 247)",
            boxShadow: `0 0 10px ${i % 2 === 0 ? "rgb(59, 130, 246)" : "rgb(168, 85, 247)"}`,
            animationDelay: `${i * 0.5}s`,
          }}
        />
      ))}

      <div className="relative z-10 w-full max-w-3xl space-y-8">
        {/* Header with logout */}
        <div className="flex items-center justify-between">
          <Link
            href="/"
            className="inline-flex items-center gap-2 text-muted-foreground hover:text-foreground transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
            Back to Home
          </Link>
          <div className="flex items-center gap-3">
            {user && (
              <span className="text-sm text-muted-foreground font-rajdhani">
                {user.email}
              </span>
            )}
            <GlowButton
              variant="outline"
              size="sm"
              onClick={signOut}
              className="font-rajdhani"
            >
              <LogOut className="w-4 h-4 mr-2" />
              Logout
            </GlowButton>
          </div>
        </div>

        {/* Header */}
        <div className="text-center space-y-4">
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full glass-panel text-sm text-muted-foreground">
            <Sparkles className="w-4 h-4 text-primary" />
            Choose Detection Mode
          </div>
          <h1 className="text-3xl md:text-4xl font-bold">
            What would you like to <span className="text-primary">analyze</span>?
          </h1>
          <p className="text-muted-foreground">Select the type of media you want to check for deepfakes.</p>
        </div>

        {/* Selection Cards */}
        <div className="grid md:grid-cols-2 gap-6">
          {/* Image Detection */}
          <GlassCard
            className="group cursor-pointer hover:border-primary/50 transition-all duration-300"
            hover
            onClick={() => router.push("/detect/image")}
          >
            <div className="space-y-6 text-center py-8">
              <div className="w-20 h-20 mx-auto rounded-2xl bg-gradient-to-br from-primary/20 to-primary/5 flex items-center justify-center group-hover:scale-110 transition-transform duration-300">
                <ImageIcon className="w-10 h-10 text-primary" />
              </div>
              <div className="space-y-2">
                <h2 className="text-2xl font-bold">Image Detection</h2>
                <p className="text-muted-foreground text-sm">
                  Analyze photos and images for AI-generated or manipulated content.
                </p>
              </div>
              <div className="flex flex-wrap justify-center gap-2">
                <span className="px-3 py-1 rounded-full bg-primary/10 text-primary text-xs">Heatmap Analysis</span>
                <span className="px-3 py-1 rounded-full bg-primary/10 text-primary text-xs">Reverse Search</span>
              </div>
            </div>
          </GlassCard>

          {/* Video Detection */}
          <GlassCard
            className="group cursor-pointer hover:border-accent/50 transition-all duration-300"
            hover
            glowColor="purple"
            onClick={() => router.push("/detect/video")}
          >
            <div className="space-y-6 text-center py-8">
              <div className="w-20 h-20 mx-auto rounded-2xl bg-gradient-to-br from-accent/20 to-accent/5 flex items-center justify-center group-hover:scale-110 transition-transform duration-300">
                <Video className="w-10 h-10 text-accent" />
              </div>
              <div className="space-y-2">
                <h2 className="text-2xl font-bold">Video Detection</h2>
                <p className="text-muted-foreground text-sm">
                  Scan video content frame-by-frame for deepfake manipulation.
                </p>
              </div>
              <div className="flex flex-wrap justify-center gap-2">
                <span className="px-3 py-1 rounded-full bg-accent/10 text-accent text-xs">Frame Analysis</span>
                <span className="px-3 py-1 rounded-full bg-accent/10 text-accent text-xs">Probability Score</span>
              </div>
            </div>
          </GlassCard>
        </div>
      </div>
    </main>
  )
}

export default function DetectPage() {
  return (
    <ProtectedRoute>
      <DetectPageContent />
    </ProtectedRoute>
  )
}
