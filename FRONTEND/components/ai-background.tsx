"use client"

export function AIBackground() {
  return (
    <div className="fixed inset-0 pointer-events-none overflow-hidden z-0">
      {/* Hologram gradient layers */}
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top_left,rgba(59,130,246,0.08),transparent_50%)]" />
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_bottom_right,rgba(168,85,247,0.08),transparent_50%)]" />
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,rgba(59,130,246,0.05),transparent_70%)]" />

      {/* Digital mesh grid */}
      <div
        className="absolute inset-0 opacity-[0.03]"
        style={{
          backgroundImage: `
            linear-gradient(rgba(59, 130, 246, 0.5) 1px, transparent 1px),
            linear-gradient(90deg, rgba(59, 130, 246, 0.5) 1px, transparent 1px)
          `,
          backgroundSize: "60px 60px",
        }}
      />

      {/* Flowing neon waves */}
      <div className="absolute top-1/4 left-0 w-full h-px bg-gradient-to-r from-transparent via-primary/20 to-transparent animate-wave-flow" />
      <div
        className="absolute top-2/4 left-0 w-full h-px bg-gradient-to-r from-transparent via-secondary/20 to-transparent animate-wave-flow"
        style={{ animationDelay: "2s", animationDuration: "10s" }}
      />
      <div
        className="absolute top-3/4 left-0 w-full h-px bg-gradient-to-r from-transparent via-primary/15 to-transparent animate-wave-flow"
        style={{ animationDelay: "4s", animationDuration: "12s" }}
      />

      {/* Floating particles */}
      {[...Array(20)].map((_, i) => (
        <div
          key={i}
          className="absolute w-1 h-1 rounded-full animate-particle-drift"
          style={{
            left: `${5 + ((i * 5) % 90)}%`,
            top: `${10 + ((i * 7) % 80)}%`,
            backgroundColor: i % 3 === 0 ? "rgba(59, 130, 246, 0.4)" : "rgba(168, 85, 247, 0.4)",
            animationDelay: `${i * 0.5}s`,
            animationDuration: `${8 + (i % 5) * 2}s`,
          }}
        />
      ))}

      {/* Abstract AI circuit nodes */}
      <svg className="absolute inset-0 w-full h-full opacity-[0.04]" xmlns="http://www.w3.org/2000/svg">
        <defs>
          <pattern id="circuit-pattern" x="0" y="0" width="200" height="200" patternUnits="userSpaceOnUse">
            <circle cx="20" cy="20" r="2" fill="#3b82f6" />
            <circle cx="100" cy="40" r="3" fill="#a855f7" />
            <circle cx="180" cy="80" r="2" fill="#3b82f6" />
            <circle cx="60" cy="120" r="2" fill="#a855f7" />
            <circle cx="140" cy="160" r="3" fill="#3b82f6" />
            <line x1="20" y1="20" x2="100" y2="40" stroke="#3b82f6" strokeWidth="0.5" />
            <line x1="100" y1="40" x2="180" y2="80" stroke="#a855f7" strokeWidth="0.5" />
            <line x1="60" y1="120" x2="140" y2="160" stroke="#3b82f6" strokeWidth="0.5" />
            <line x1="100" y1="40" x2="60" y2="120" stroke="#a855f7" strokeWidth="0.5" />
          </pattern>
        </defs>
        <rect width="100%" height="100%" fill="url(#circuit-pattern)" />
      </svg>
    </div>
  )
}
