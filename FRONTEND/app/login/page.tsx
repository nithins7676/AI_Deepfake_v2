"use client"

import type React from "react"
import Image from "next/image"
import { useState } from "react"
import Link from "next/link"
import { useRouter } from "next/navigation"
import { ArrowLeft, User, Mail, Lock, CheckSquare, Square, AlertCircle } from "lucide-react"
import { GlowButton } from "@/components/ui/glow-button"
import { GlassCard } from "@/components/ui/glass-card"
import { useAuth } from "@/contexts/auth-context"

export default function LoginPage() {
  const router = useRouter()
  const { signIn, signUp, resetPassword } = useAuth()
  const [isSignUp, setIsSignUp] = useState(false)
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    password: "",
  })
  const [acceptedTerms, setAcceptedTerms] = useState(false)
  const [showForgotPassword, setShowForgotPassword] = useState(false)
  const [resetEmail, setResetEmail] = useState("")
  const [resetSent, setResetSent] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)
    
    if (!acceptedTerms) {
      setError("Please accept the terms to continue")
      return
    }

    if (!formData.email || !formData.password) {
      setError("Please fill in all required fields")
      return
    }

    setLoading(true)
    try {
      if (isSignUp) {
        const { error } = await signUp(formData.email, formData.password, formData.name)
        if (error) {
          setError(error.message || "Sign up failed. Please try again.")
        }
      } else {
        const { error } = await signIn(formData.email, formData.password)
        if (error) {
          setError(error.message || "Invalid email or password")
        }
      }
    } catch (err) {
      setError("An unexpected error occurred. Please try again.")
    } finally {
      setLoading(false)
    }
  }

  const handlePasswordReset = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)
    
    if (!resetEmail) {
      setError("Please enter your email address")
      return
    }

    setLoading(true)
    try {
      const { error } = await resetPassword(resetEmail)
      if (error) {
        setError(error.message || "Failed to send reset email")
      } else {
        setResetSent(true)
        setTimeout(() => {
          setShowForgotPassword(false)
          setResetSent(false)
          setResetEmail("")
        }, 3000)
      }
    } catch (err) {
      setError("An unexpected error occurred. Please try again.")
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="min-h-screen bg-background flex items-center justify-center px-4 relative overflow-hidden">
      <div className="absolute inset-0 pointer-events-none">
        <Image src="/images/login-bg.jpg" alt="" fill className="object-cover opacity-[0.1]" priority />
        <div className="absolute inset-0 bg-gradient-to-br from-background via-background/90 to-background" />
      </div>

      <div className="absolute inset-0 pointer-events-none overflow-hidden">
        <div className="absolute -left-32 top-1/2 -translate-y-1/2 w-[700px] h-[700px] opacity-[0.2]">
          <Image src="/images/robot-face.jpg" alt="" fill className="object-contain" />
          <div className="absolute inset-0 bg-gradient-to-l from-background via-background/70 to-transparent" />
          <div className="absolute inset-0 bg-gradient-to-t from-background via-transparent to-background/50" />
        </div>
      </div>

      {/* Gradient orbs */}
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,rgba(59,130,246,0.15),transparent_50%)]" />
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_bottom,rgba(168,85,247,0.15),transparent_50%)]" />

      {/* Animated floating orbs */}
      <div className="absolute top-1/4 left-1/4 w-64 h-64 bg-primary/20 rounded-full blur-3xl animate-float" />
      <div className="absolute bottom-1/4 right-1/4 w-72 h-72 bg-accent/20 rounded-full blur-3xl animate-float-delayed" />
      <div className="absolute top-1/2 right-1/3 w-48 h-48 bg-primary/10 rounded-full blur-2xl animate-float-slow" />

      {/* Grid pattern overlay */}
      <div
        className="absolute inset-0 opacity-[0.03]"
        style={{
          backgroundImage: `linear-gradient(rgba(59, 130, 246, 0.3) 1px, transparent 1px), 
                            linear-gradient(90deg, rgba(59, 130, 246, 0.3) 1px, transparent 1px)`,
          backgroundSize: "50px 50px",
        }}
      />

      {/* Scanline effect */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute w-full h-px bg-gradient-to-r from-transparent via-primary/30 to-transparent animate-scanline-move" />
      </div>

      {/* Corner decorations */}
      <div className="absolute top-8 left-8 w-20 h-20 border-l-2 border-t-2 border-primary/30 rounded-tl-lg" />
      <div className="absolute top-8 right-8 w-20 h-20 border-r-2 border-t-2 border-accent/30 rounded-tr-lg" />
      <div className="absolute bottom-8 left-8 w-20 h-20 border-l-2 border-b-2 border-accent/30 rounded-bl-lg" />
      <div className="absolute bottom-8 right-8 w-20 h-20 border-r-2 border-b-2 border-primary/30 rounded-br-lg" />

      <div className="relative z-10 w-full max-w-md space-y-6">
        {/* Back button - uses Rajdhani */}
        <Link
          href="/"
          className="inline-flex items-center gap-2 text-muted-foreground hover:text-foreground transition-colors font-rajdhani"
        >
          <ArrowLeft className="w-4 h-4" />
          Back to Home
        </Link>

        {/* Login Card */}
        <GlassCard className="animate-pulse-glow">
          <div className="space-y-6">
            {/* Header - uses Orbitron for title */}
            <div className="text-center space-y-2">
              <h1 className="text-3xl font-bold text-neon-blue font-orbitron">UNMASK</h1>
              <p className="text-[#cfcfcf] font-rajdhani">{isSignUp ? "Create an account" : "Sign in to continue"}</p>
            </div>

            {/* Error Message */}
            {error && (
              <div className="p-3 rounded-lg bg-red-500/10 border border-red-500/20 flex items-center gap-2">
                <AlertCircle className="w-4 h-4 text-red-500" />
                <p className="text-sm text-red-500">{error}</p>
              </div>
            )}

            {/* Form */}
            <form onSubmit={handleSubmit} className="space-y-4">
              {/* Name - only show for sign up */}
              {isSignUp && (
                <div className="space-y-2">
                  <label className="text-sm text-[#cfcfcf] font-rajdhani">Name (Optional)</label>
                  <div className="relative">
                    <User className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground" />
                    <input
                      type="text"
                      value={formData.name}
                      onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                      className="w-full pl-11 pr-4 py-3 bg-muted/50 border border-border rounded-xl focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-all font-rajdhani"
                      placeholder="Enter your name"
                    />
                  </div>
                </div>
              )}

              {/* Email */}
              <div className="space-y-2">
                <label className="text-sm text-[#cfcfcf] font-rajdhani">Email</label>
                <div className="relative">
                  <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground" />
                  <input
                    type="email"
                    value={formData.email}
                    onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                    className="w-full pl-11 pr-4 py-3 bg-muted/50 border border-border rounded-xl focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-all font-rajdhani"
                    placeholder="Enter your email"
                    required
                  />
                </div>
              </div>

              {/* Password */}
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <label className="text-sm text-[#cfcfcf] font-rajdhani">Password</label>
                  <button
                    type="button"
                    onClick={() => setShowForgotPassword(true)}
                    className="text-xs text-primary hover:text-primary/80 transition-colors font-rajdhani"
                  >
                    Forgot Password?
                  </button>
                </div>
                <div className="relative">
                  <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground" />
                  <input
                    type="password"
                    value={formData.password}
                    onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                    className="w-full pl-11 pr-4 py-3 bg-muted/50 border border-border rounded-xl focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-all font-rajdhani"
                    placeholder="Enter your password"
                    required
                  />
                </div>
              </div>

              {/* Terms Checkbox - disclaimer uses Inter (sans) */}
              <div
                className="flex items-start gap-3 p-4 rounded-xl bg-amber-500/5 border border-amber-500/20 cursor-pointer"
                onClick={() => setAcceptedTerms(!acceptedTerms)}
              >
                {acceptedTerms ? (
                  <CheckSquare className="w-5 h-5 text-primary shrink-0 mt-0.5" />
                ) : (
                  <Square className="w-5 h-5 text-muted-foreground shrink-0 mt-0.5" />
                )}
                <p className="text-xs text-[#cfcfcf] leading-relaxed">
                  I understand that UNMASK is an experimental prototype. The detection model is still under training and{" "}
                  <span className="text-amber-400">NOT fully accurate</span>. Results may be incorrect and should be
                  used for testing purposes only.
                </p>
              </div>

              {/* Submit Button - uses Rajdhani */}
              <GlowButton
                type="submit"
                className="w-full font-rajdhani font-semibold tracking-wide"
                size="lg"
                disabled={!acceptedTerms || loading}
              >
                {loading ? "Please wait..." : isSignUp ? "Sign Up" : "Login"}
              </GlowButton>
            </form>

            {/* Toggle Sign Up/Sign In */}
            <div className="text-center">
              <button
                type="button"
                onClick={() => {
                  setIsSignUp(!isSignUp)
                  setError(null)
                }}
                className="text-sm text-primary hover:text-primary/80 transition-colors font-rajdhani"
              >
                {isSignUp ? "Already have an account? Sign in" : "Don't have an account? Sign up"}
              </button>
            </div>
          </div>
        </GlassCard>
      </div>

      {showForgotPassword && (
        <div className="fixed inset-0 bg-background/80 backdrop-blur-sm flex items-center justify-center z-50 px-4">
          <GlassCard className="w-full max-w-md">
            <div className="space-y-6">
              <div className="text-center space-y-2">
                <h2 className="text-2xl font-bold text-neon-blue font-orbitron">Reset Password</h2>
                <p className="text-sm text-[#cfcfcf]">Enter your email and we'll send you a reset link</p>
              </div>

              {resetSent ? (
                <div className="text-center py-8 space-y-3">
                  <div className="w-16 h-16 bg-primary/20 rounded-full flex items-center justify-center mx-auto">
                    <CheckSquare className="w-8 h-8 text-primary" />
                  </div>
                  <p className="text-foreground font-medium font-rajdhani">Reset link sent!</p>
                  <p className="text-sm text-[#cfcfcf]">Check your email for the password reset link</p>
                </div>
              ) : (
                <form onSubmit={handlePasswordReset} className="space-y-4">
                  <div className="space-y-2">
                    <label className="text-sm text-[#cfcfcf] font-rajdhani">Email</label>
                    <div className="relative">
                      <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground" />
                      <input
                        type="email"
                        value={resetEmail}
                        onChange={(e) => setResetEmail(e.target.value)}
                        className="w-full pl-11 pr-4 py-3 bg-muted/50 border border-border rounded-xl focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-all font-rajdhani"
                        placeholder="Enter your email"
                        required
                      />
                    </div>
                  </div>

                  <div className="flex gap-3">
                    <button
                      type="button"
                      onClick={() => setShowForgotPassword(false)}
                      className="flex-1 px-4 py-3 rounded-xl border border-border hover:bg-muted/50 transition-all font-rajdhani"
                    >
                      Cancel
                    </button>
                    <GlowButton type="submit" className="flex-1 font-rajdhani font-semibold">
                      Send Reset Link
                    </GlowButton>
                  </div>
                </form>
              )}
            </div>
          </GlassCard>
        </div>
      )}
    </main>
  )
}
