"use client"

import { ScanAnimation } from "./scan-animation"

interface AnalysisOverlayProps {
  isAnalyzing: boolean
}

export function AnalysisOverlay({ isAnalyzing }: AnalysisOverlayProps) {
  if (!isAnalyzing) return null

  return (
    <div className="absolute inset-0 bg-background/80 backdrop-blur-sm rounded-xl flex items-center justify-center z-20">
      <div className="text-center space-y-4">
        <div className="relative w-24 h-24 mx-auto">
          <div className="absolute inset-0 rounded-full border-2 border-primary/30 animate-ping" />
          <div className="absolute inset-2 rounded-full border-2 border-primary/50 animate-pulse" />
          <div className="absolute inset-4 rounded-full bg-primary/20 flex items-center justify-center">
            <div className="w-4 h-4 bg-primary rounded-full animate-pulse" />
          </div>
        </div>
        <div className="space-y-1">
          <p className="font-semibold text-primary animate-pulse">Analyzing...</p>
          <p className="text-sm text-muted-foreground">Running forensic detection</p>
        </div>
      </div>
      <ScanAnimation />
    </div>
  )
}
