"use client"

import { GlassCard } from "./ui/glass-card"
import { ExternalLink, AlertTriangle, CheckCircle, XCircle } from "lucide-react"

interface ResultPanelProps {
  type: "image" | "video"
  results: {
    real: number
    fake: number
    ai: number
  } | null
  heatmapUrl?: string | null
  reverseLinks?: { title: string; link: string }[]
}

export function ResultPanel({ type, results, heatmapUrl, reverseLinks }: ResultPanelProps) {
  if (!results) {
    return (
      <div className="h-full flex items-center justify-center">
        <div className="text-center space-y-4 text-muted-foreground">
          <div className="w-20 h-20 mx-auto rounded-xl bg-muted/50 flex items-center justify-center">
            <AlertTriangle className="w-10 h-10" />
          </div>
          <div>
            <p className="font-medium">No Results Yet</p>
            <p className="text-sm">Upload and analyze media to see results</p>
          </div>
        </div>
      </div>
    )
  }

  const getVerdict = () => {
    if (results.real > results.fake && results.real > results.ai) {
      return { label: "Likely Authentic", color: "text-green-500", icon: CheckCircle }
    } else if (results.fake > results.real && results.fake > results.ai) {
      return { label: "Likely Fake", color: "text-red-500", icon: XCircle }
    } else {
      return { label: "Likely AI Generated", color: "text-amber-500", icon: AlertTriangle }
    }
  }

  const verdict = getVerdict()
  const VerdictIcon = verdict.icon

  return (
    <div className="space-y-6">
      {/* Verdict */}
      <GlassCard className="text-center" glowColor={results.real > 50 ? "blue" : "purple"}>
        <div className="space-y-3">
          <VerdictIcon className={`w-12 h-12 mx-auto ${verdict.color}`} />
          <h3 className={`text-2xl font-bold ${verdict.color}`}>{verdict.label}</h3>
        </div>
      </GlassCard>

      {/* Probabilities */}
      <GlassCard glowColor="none">
        <h4 className="font-semibold mb-4">Detection Probabilities</h4>
        <div className="space-y-4">
          {/* Real */}
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span className="text-muted-foreground">Real</span>
              <span className="text-green-500 font-medium">{results.real}%</span>
            </div>
            <div className="h-2 bg-muted rounded-full overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-green-500 to-green-400 rounded-full transition-all duration-500"
                style={{ width: `${results.real}%` }}
              />
            </div>
          </div>

          {/* Fake */}
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span className="text-muted-foreground">Fake</span>
              <span className="text-red-500 font-medium">{results.fake}%</span>
            </div>
            <div className="h-2 bg-muted rounded-full overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-red-500 to-red-400 rounded-full transition-all duration-500"
                style={{ width: `${results.fake}%` }}
              />
            </div>
          </div>

          {/* AI Generated */}
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span className="text-muted-foreground">AI Generated</span>
              <span className="text-amber-500 font-medium">{results.ai}%</span>
            </div>
            <div className="h-2 bg-muted rounded-full overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-amber-500 to-amber-400 rounded-full transition-all duration-500"
                style={{ width: `${results.ai}%` }}
              />
            </div>
          </div>
        </div>
      </GlassCard>

      {/* Heatmap (Image only) */}
      {type === "image" && (
        <GlassCard glowColor="none">
          <h4 className="font-semibold mb-4">Manipulation Heatmap</h4>
          {heatmapUrl ? (
            <img src={heatmapUrl || "/placeholder.svg"} alt="Heatmap" className="w-full rounded-lg" />
          ) : (
            <div className="aspect-square rounded-lg bg-muted/50 flex items-center justify-center">
              <p className="text-muted-foreground text-sm">Heatmap visualization</p>
            </div>
          )}
        </GlassCard>
      )}

      {/* Reverse Search (Image only, RapidAPI) */}
      {type === "image" && (
        <GlassCard glowColor="none">
          <h4 className="font-semibold mb-4">Reverse Search Links</h4>
          <div className="space-y-2">
            {reverseLinks && reverseLinks.length > 0 ? (
              reverseLinks.map((item, idx) => (
                <a
                  key={idx}
                  href={item.link}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center justify-between p-3 rounded-lg bg-muted/50 hover:bg-muted transition-colors group"
                >
                  <span className="text-sm truncate max-w-[220px]" title={item.title}>
                    {item.title}
                  </span>
                  <ExternalLink className="w-4 h-4 text-muted-foreground group-hover:text-primary transition-colors" />
                </a>
              ))
            ) : (
              <p className="text-sm text-muted-foreground">
                No reverse image matches found yet.
              </p>
            )}
          </div>
        </GlassCard>
      )}
    </div>
  )
}
