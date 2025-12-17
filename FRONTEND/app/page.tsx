import Link from "next/link"
import Image from "next/image"
import { Shield, Eye, Brain, Fingerprint, ChevronRight } from "lucide-react"
import { GlowButton } from "@/components/ui/glow-button"
import { GlassCard } from "@/components/ui/glass-card"
import { DisclaimerBox } from "@/components/disclaimer-box"
import { NeuralNetworkBg } from "@/components/neural-network-bg"

export default function LandingPage() {
  return (
    <main className="min-h-screen bg-background relative overflow-hidden">
      <NeuralNetworkBg />

      <div className="fixed inset-0 pointer-events-none">
        <Image src="/images/landing-bg.jpg" alt="" fill className="object-cover opacity-[0.12]" priority />
        <div className="absolute inset-0 bg-gradient-to-b from-background via-background/70 to-background" />
      </div>

      <div className="fixed inset-0 pointer-events-none overflow-hidden">
        <div className="absolute -right-20 top-1/2 -translate-y-1/2 w-[800px] h-[800px] opacity-[0.25]">
          <Image src="/images/robot-face.jpg" alt="" fill className="object-contain" />
          <div className="absolute inset-0 bg-gradient-to-r from-background via-background/60 to-transparent" />
          <div className="absolute inset-0 bg-gradient-to-t from-background via-transparent to-background/50" />
        </div>
      </div>

      {/* Static background effects */}
      <div className="fixed inset-0 pointer-events-none">
        <div className="absolute top-1/4 left-1/4 w-[600px] h-[600px] bg-primary/10 rounded-full blur-[150px]" />
        <div className="absolute bottom-1/4 right-1/4 w-[500px] h-[500px] bg-accent/10 rounded-full blur-[120px]" />
      </div>

      {/* Hero Section */}
      <section className="relative min-h-screen flex items-center justify-center px-4 py-20">
        <div className="max-w-4xl mx-auto text-center space-y-8 relative z-10">
          <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
            <svg viewBox="0 0 400 400" className="w-[500px] h-[500px] opacity-20">
              {/* Rotating hexagon rings */}
              <g className="animate-hex-rotate" style={{ transformOrigin: "200px 200px" }}>
                <polygon
                  points="200,50 320,125 320,275 200,350 80,275 80,125"
                  fill="none"
                  stroke="url(#hexGradient)"
                  strokeWidth="1"
                />
              </g>
              <g
                className="animate-hex-rotate"
                style={{ transformOrigin: "200px 200px", animationDirection: "reverse", animationDuration: "25s" }}
              >
                <polygon
                  points="200,80 290,135 290,265 200,320 110,265 110,135"
                  fill="none"
                  stroke="url(#hexGradient2)"
                  strokeWidth="1"
                />
              </g>
              <g className="animate-hex-rotate" style={{ transformOrigin: "200px 200px", animationDuration: "30s" }}>
                <polygon
                  points="200,110 260,145 260,255 200,290 140,255 140,145"
                  fill="none"
                  stroke="url(#hexGradient)"
                  strokeWidth="1"
                />
              </g>
              <circle cx="200" cy="200" r="30" fill="none" stroke="#3b82f6" strokeWidth="2" className="animate-pulse" />
              <circle cx="200" cy="200" r="20" fill="none" stroke="#a855f7" strokeWidth="1" className="animate-ping" />

              <defs>
                <linearGradient id="hexGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" stopColor="#3b82f6" stopOpacity="0.6" />
                  <stop offset="100%" stopColor="#a855f7" stopOpacity="0.6" />
                </linearGradient>
                <linearGradient id="hexGradient2" x1="100%" y1="0%" x2="0%" y2="100%">
                  <stop offset="0%" stopColor="#a855f7" stopOpacity="0.4" />
                  <stop offset="100%" stopColor="#3b82f6" stopOpacity="0.4" />
                </linearGradient>
              </defs>
            </svg>
          </div>

          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary/10 border border-primary/30 text-sm text-primary relative z-10 font-rajdhani font-semibold tracking-wide">
            <div className="w-2 h-2 bg-primary rounded-full animate-pulse" />
            AI-Powered Detection
          </div>

          <h1 className="text-6xl md:text-8xl font-bold tracking-tight relative z-10 font-orbitron">
            <span className="text-neon-blue">UNMASK</span>
          </h1>

          <p className="text-xl md:text-2xl text-[#cfcfcf] max-w-2xl mx-auto relative z-10 leading-relaxed">
            Reveal the truth behind digital illusions. Advanced deepfake detection powered by cutting-edge AI forensics.
          </p>

          {/* Disclaimer */}
          <div className="max-w-xl mx-auto relative z-10">
            <DisclaimerBox />
          </div>

          <div className="pt-4 relative z-10">
            <Link href="/login">
              <GlowButton size="lg" className="group font-rajdhani font-semibold tracking-wide">
                Get Started
                <ChevronRight className="inline-block ml-2 w-5 h-5 group-hover:translate-x-1 transition-transform" />
              </GlowButton>
            </Link>
          </div>
        </div>
      </section>

      {/* Why Detection Matters Section */}
      <section className="relative py-24 px-4">
        <div className="max-w-6xl mx-auto space-y-16">
          <div className="text-center space-y-4">
            <h2 className="text-3xl md:text-4xl font-bold font-orbitron">
              Why Detection <span className="text-neon-blue">Matters</span>
            </h2>
            <p className="text-[#cfcfcf] max-w-2xl mx-auto">
              In an era of synthetic media, verifying authenticity is crucial for trust and security.
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            <GlassCard className="p-6 space-y-4 group hover:border-primary/50 transition-colors">
              <div className="w-12 h-12 rounded-lg bg-primary/20 flex items-center justify-center group-hover:scale-110 transition-transform">
                <Shield className="w-6 h-6 text-primary" />
              </div>
              <h3 className="font-semibold text-lg font-rajdhani">Protect Truth</h3>
              <p className="text-[#cfcfcf] text-sm">Combat misinformation and preserve digital integrity.</p>
            </GlassCard>

            <GlassCard className="p-6 space-y-4 group hover:border-accent/50 transition-colors">
              <div className="w-12 h-12 rounded-lg bg-accent/20 flex items-center justify-center group-hover:scale-110 transition-transform">
                <Eye className="w-6 h-6 text-accent" />
              </div>
              <h3 className="font-semibold text-lg font-rajdhani">Verify Identity</h3>
              <p className="text-[#cfcfcf] text-sm">Ensure the authenticity of faces in digital content.</p>
            </GlassCard>

            <GlassCard className="p-6 space-y-4 group hover:border-primary/50 transition-colors">
              <div className="w-12 h-12 rounded-lg bg-primary/20 flex items-center justify-center group-hover:scale-110 transition-transform">
                <Brain className="w-6 h-6 text-primary" />
              </div>
              <h3 className="font-semibold text-lg font-rajdhani">AI Analysis</h3>
              <p className="text-[#cfcfcf] text-sm">Advanced neural networks trained to detect manipulation.</p>
            </GlassCard>

            <GlassCard className="p-6 space-y-4 group hover:border-accent/50 transition-colors">
              <div className="w-12 h-12 rounded-lg bg-accent/20 flex items-center justify-center group-hover:scale-110 transition-transform">
                <Fingerprint className="w-6 h-6 text-accent" />
              </div>
              <h3 className="font-semibold text-lg font-rajdhani">Forensic Precision</h3>
              <p className="text-[#cfcfcf] text-sm">Detailed analysis with probability scores and heatmaps.</p>
            </GlassCard>
          </div>

          <div className="text-center">
            <p className="text-[#cfcfcf] text-sm inline-block px-4 py-2 rounded-full border border-border font-rajdhani">
              Note: Model mainly trained on human faces.
            </p>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-8 border-t border-border relative z-10">
        <div className="max-w-6xl mx-auto px-4 text-center text-[#cfcfcf] text-sm">
          <p>© 2025 UNMASK. Experimental deepfake detection prototype.</p>
        </div>
      </footer>
    </main>
  )
}
