"use client"

import { useState } from "react"
import Link from "next/link"
import { ArrowLeft, Scan, RotateCcw } from "lucide-react"
import { GlowButton } from "@/components/ui/glow-button"
import { GlassCard } from "@/components/ui/glass-card"
import { UploadZone } from "@/components/upload-zone"
import { ForensicLoader } from "@/components/forensic-loader"
import { ResultPanel } from "@/components/result-panel"
import { DisclaimerBox } from "@/components/disclaimer-box"
import { ProtectedRoute } from "@/components/protected-route"
import { useAuth } from "@/contexts/auth-context"
import { supabase } from "@/lib/supabase"

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:5000"

function ImageDetectionPageContent() {
  const [file, setFile] = useState<File | null>(null)
  const [preview, setPreview] = useState<string | null>(null)
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [results, setResults] = useState<{ real: number; fake: number; ai: number } | null>(null)
  const [heatmapUrl, setHeatmapUrl] = useState<string | null>(null)
  const [reverseLinks, setReverseLinks] = useState<{ title: string; link: string }[] | null>(null)
  const { session } = useAuth()

  const runReverseSearch = async (file: File, signal?: AbortSignal) => {
    try {
      const token = session?.access_token
      if (!token) return

      const formData = new FormData()
      formData.append("file", file)

      const resp = await fetch(`${BACKEND_URL}/reverse_search`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
        },
        body: formData,
        signal,
      })

      const data = await resp.json()

      if (!resp.ok) {
        console.error("Reverse search error", data)
        return
      }

      if (data.reverse_search?.results) {
        const links = (data.reverse_search.results as { title?: string; link?: string }[])
          .filter((r) => r.link)
          .map((r) => ({ title: r.title || r.link!, link: r.link! }))
        setReverseLinks(links.length > 0 ? links : null)
        
        // Log if using fallback
        if (data.reverse_search.note) {
          console.log("[REVERSE_SEARCH]", data.reverse_search.note)
        }
      } else {
        setReverseLinks(null)
      }
    } catch (err) {
      console.error("Reverse search failed", err)
      setReverseLinks(null)
    }
  }

  const handleFileSelect = (selectedFile: File | null) => {
    if (selectedFile) {
      setFile(selectedFile)
      const reader = new FileReader()
      reader.onload = (e) => setPreview(e.target?.result as string)
      reader.readAsDataURL(selectedFile)
      setResults(null)
      setHeatmapUrl(null)
      setReverseLinks(null)
    } else {
      setFile(null)
      setPreview(null)
      setResults(null)
      setHeatmapUrl(null)
      setReverseLinks(null)
    }
  }

  const handleAnalyze = async () => {
    if (!file) return

    setIsAnalyzing(true)
    setResults(null)
    setHeatmapUrl(null)
    setReverseLinks(null)

    try {
      // Get auth token
      const token = session?.access_token
      if (!token) {
        throw new Error("Not authenticated")
      }

      const formData = new FormData()
      formData.append("file", file)

      const resp = await fetch(`${BACKEND_URL}/predict`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
        },
        body: formData,
      })

      const data = await resp.json()

      if (!resp.ok) {
        throw new Error(data?.error || "Image prediction failed")
      }

      // data.all_scores is like { "Real": "88.00%", "Deepfake": "5.00%", "AI-Generated Face": "7.00%" }
      const scores = (data.all_scores || {}) as Record<string, string>

      const real = parseFloat((scores["Real"] || "0").replace("%", "")) || 0
      const fake = parseFloat((scores["Deepfake"] || "0").replace("%", "")) || 0
      const ai = parseFloat((scores["AI-Generated Face"] || "0").replace("%", "")) || 0

      setResults({ real, fake, ai })

      // heatmap_url is a path like "/uploads/image_heatmaps/xxx_heatmap.png"
      if (data.heatmap_url) {
        setHeatmapUrl(`${BACKEND_URL}${data.heatmap_url}`)
      }

      // Fire reverse search in background, do not block main analysis
      void runReverseSearch(file)
    } catch (err) {
      console.error("Image analyze error", err)
      alert("Image analysis failed. Please try again.")
    } finally {
      setIsAnalyzing(false)
    }
  }

  const handleReset = () => {
    setFile(null)
    setPreview(null)
    setResults(null)
    setIsAnalyzing(false)
  }

  return (
    <main className="min-h-screen bg-transparent px-4 py-8 relative overflow-hidden">
      <div className="relative z-10 max-w-6xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <Link
            href="/detect"
            className="inline-flex items-center gap-2 text-muted-foreground hover:text-foreground transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
            Back
          </Link>
          <h1 className="text-xl font-bold">
            Image <span className="text-primary">Detection</span>
          </h1>
          <div className="w-20" />
        </div>

        {/* Main Content */}
        <div className="grid lg:grid-cols-2 gap-6">
          {/* Left Panel - Upload */}
          <GlassCard className="relative">
            <div className="space-y-6">
              <h2 className="text-lg font-semibold">Upload Image</h2>

              <div className="relative">
                <UploadZone type="image" onFileSelect={handleFileSelect} file={file} preview={preview} />
                {isAnalyzing && <ForensicLoader compact />}
              </div>

              <div className="flex gap-3">
                <GlowButton onClick={handleAnalyze} disabled={!file || isAnalyzing} className="flex-1">
                  <Scan className="w-4 h-4 mr-2" />
                  Analyze
                </GlowButton>
                <GlowButton variant="outline" onClick={handleReset} disabled={isAnalyzing}>
                  <RotateCcw className="w-4 h-4" />
                </GlowButton>
              </div>
            </div>
          </GlassCard>

          {/* Right Panel - Results */}
          <GlassCard glowColor="purple">
            <h2 className="text-lg font-semibold mb-6">Analysis Results</h2>
            <ResultPanel
              type="image"
              results={results}
              heatmapUrl={heatmapUrl ?? undefined}
              reverseLinks={reverseLinks ?? undefined}
            />
          </GlassCard>
        </div>

        {/* Disclaimer */}
        <div className="text-center">
          <DisclaimerBox variant="compact" />
        </div>
      </div>
    </main>
  )
}

export default function ImageDetectionPage() {
  return (
    <ProtectedRoute>
      <ImageDetectionPageContent />
    </ProtectedRoute>
  )
}
