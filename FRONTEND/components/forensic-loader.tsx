"use client"

import { useEffect, useState } from "react"

interface ForensicLoaderProps {
  compact?: boolean
}

export function ForensicLoader({ compact = false }: ForensicLoaderProps) {
  const [progress, setProgress] = useState(0)
  const [scanPhase, setScanPhase] = useState<"grid" | "analyze" | "process">("grid")

  useEffect(() => {
    const interval = setInterval(() => {
      setProgress((prev) => {
        if (prev >= 100) return 100
        return prev + 1
      })
    }, 50)

    // Change scan phases
    const phaseTimer1 = setTimeout(() => setScanPhase("analyze"), 1500)
    const phaseTimer2 = setTimeout(() => setScanPhase("process"), 3500)

    return () => {
      clearInterval(interval)
      clearTimeout(phaseTimer1)
      clearTimeout(phaseTimer2)
    }
  }, [])

  return (
    <div className="absolute inset-0 z-40 rounded-xl overflow-hidden bg-black/90">
      <div
        className="absolute inset-0"
        style={{
          backgroundImage: `
            linear-gradient(rgba(59, 130, 246, 0.4) 1px, transparent 1px),
            linear-gradient(90deg, rgba(59, 130, 246, 0.4) 1px, transparent 1px)
          `,
          backgroundSize: compact ? "20px 20px" : "30px 30px",
        }}
      />

      <div
        className="absolute left-0 right-0 h-1 bg-gradient-to-r from-transparent via-primary to-transparent animate-forensic-scan"
        style={{
          boxShadow: "0 0 20px 10px rgba(59, 130, 246, 0.5), 0 0 60px 20px rgba(59, 130, 246, 0.3)",
        }}
      />

      <div
        className="absolute left-0 right-0 h-0.5 bg-gradient-to-r from-transparent via-accent to-transparent animate-forensic-scan-delayed"
        style={{
          boxShadow: "0 0 15px 5px rgba(168, 85, 247, 0.5)",
        }}
      />

      {[...Array(compact ? 8 : 16)].map((_, i) => (
        <div
          key={i}
          className="absolute w-2 h-2 rounded-full bg-primary animate-data-point"
          style={{
            left: `${15 + (i % 4) * 25}%`,
            top: `${15 + Math.floor(i / 4) * 25}%`,
            animationDelay: `${i * 0.2}s`,
            boxShadow: "0 0 10px rgba(59, 130, 246, 0.8)",
          }}
        />
      ))}

      <div className="absolute top-4 left-4 w-8 h-8 border-l-2 border-t-2 border-primary animate-pulse" />
      <div className="absolute top-4 right-4 w-8 h-8 border-r-2 border-t-2 border-primary animate-pulse" />
      <div className="absolute bottom-4 left-4 w-8 h-8 border-l-2 border-b-2 border-primary animate-pulse" />
      <div className="absolute bottom-4 right-4 w-8 h-8 border-r-2 border-b-2 border-primary animate-pulse" />

      <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
        <div className="relative">
          <div className="w-16 h-0.5 bg-primary/60" />
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-0.5 h-16 bg-primary/60" />
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-6 h-6 border border-primary rounded-full animate-ping" />
        </div>
      </div>

      <div className="absolute bottom-3 left-0 right-0 flex flex-col items-center gap-2">
        <div className="flex items-center gap-2 font-mono text-xs text-primary">
          <span className="animate-pulse">●</span>
          <span className="uppercase tracking-wider">
            {scanPhase === "grid" && "Mapping Grid..."}
            {scanPhase === "analyze" && "Analyzing Pixels..."}
            {scanPhase === "process" && "Processing Data..."}
          </span>
        </div>
        {/* Progress bar */}
        <div className="w-32 h-1 bg-primary/20 rounded-full overflow-hidden">
          <div
            className="h-full bg-gradient-to-r from-primary to-accent transition-all duration-100"
            style={{ width: `${progress}%` }}
          />
        </div>
        <span className="font-mono text-xs text-muted-foreground">{progress}%</span>
      </div>

      <div className="absolute top-4 left-4 font-mono text-[10px] text-primary/70 space-y-1">
        <div>RES: 1920x1080</div>
        <div>DEPTH: 24-BIT</div>
        <div className="animate-pulse">SCAN: ACTIVE</div>
      </div>
      <div className="absolute top-4 right-4 font-mono text-[10px] text-accent/70 text-right space-y-1">
        <div>GRID: 64x64</div>
        <div>NODES: {compact ? 8 : 16}</div>
        <div className="animate-pulse">AI: ONLINE</div>
      </div>
    </div>
  )
}
