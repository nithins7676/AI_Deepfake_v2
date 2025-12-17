"use client"

export function HeroAnimations() {
  return (
    <div className="absolute inset-0 overflow-hidden pointer-events-none">
      {/* Rotating hexagon grid behind hero */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] opacity-[0.06]">
        <svg viewBox="0 0 800 800" className="w-full h-full animate-hex-rotate">
          <defs>
            <pattern id="hexagons" width="50" height="43.4" patternUnits="userSpaceOnUse" patternTransform="scale(2)">
              <polygon
                points="25,0 50,14.4 50,43.4 25,57.7 0,43.4 0,14.4"
                fill="none"
                stroke="#3b82f6"
                strokeWidth="0.5"
              />
            </pattern>
          </defs>
          <rect width="100%" height="100%" fill="url(#hexagons)" />
        </svg>
      </div>

      {/* Floating holographic cards */}
      <div
        className="absolute top-20 left-[10%] w-32 h-20 rounded-lg glass-panel opacity-20 animate-float-slow"
        style={{ animationDelay: "0s" }}
      />
      <div
        className="absolute top-40 right-[15%] w-24 h-16 rounded-lg glass-panel opacity-15 animate-float-slow"
        style={{ animationDelay: "1s" }}
      />
      <div
        className="absolute bottom-32 left-[20%] w-28 h-18 rounded-lg glass-panel opacity-20 animate-float-slow"
        style={{ animationDelay: "2s" }}
      />
      <div
        className="absolute bottom-48 right-[10%] w-20 h-14 rounded-lg glass-panel opacity-15 animate-float-slow"
        style={{ animationDelay: "3s" }}
      />

      {/* Neon particle clouds */}
      {[...Array(8)].map((_, i) => (
        <div
          key={`cloud-${i}`}
          className="absolute rounded-full blur-xl animate-particle-drift"
          style={{
            width: `${40 + i * 10}px`,
            height: `${40 + i * 10}px`,
            left: `${10 + i * 12}%`,
            top: `${20 + ((i * 15) % 60)}%`,
            background: i % 2 === 0 ? "rgba(59, 130, 246, 0.1)" : "rgba(168, 85, 247, 0.1)",
            animationDelay: `${i * 1.2}s`,
            animationDuration: `${12 + i * 2}s`,
          }}
        />
      ))}

      {/* Pulsing neon circles synced with time */}
      <div className="absolute top-1/3 left-1/4 w-4 h-4 rounded-full bg-primary/30 animate-pulse-ring" />
      <div
        className="absolute top-2/3 right-1/4 w-3 h-3 rounded-full bg-secondary/30 animate-pulse-ring"
        style={{ animationDelay: "0.5s" }}
      />
      <div
        className="absolute bottom-1/4 left-1/3 w-5 h-5 rounded-full bg-primary/20 animate-pulse-ring"
        style={{ animationDelay: "1s" }}
      />

      {/* AI brain/circuit icons floating */}
      <svg
        className="absolute top-1/4 right-1/4 w-16 h-16 opacity-10 animate-float-slow"
        style={{ animationDelay: "0.5s" }}
        viewBox="0 0 24 24"
        fill="none"
        stroke="#3b82f6"
        strokeWidth="1"
      >
        <path d="M12 2a10 10 0 0 1 10 10 10 10 0 0 1-10 10A10 10 0 0 1 2 12 10 10 0 0 1 12 2z" />
        <circle cx="12" cy="12" r="3" />
        <line x1="12" y1="2" x2="12" y2="9" />
        <line x1="12" y1="15" x2="12" y2="22" />
        <line x1="2" y1="12" x2="9" y2="12" />
        <line x1="15" y1="12" x2="22" y2="12" />
      </svg>

      <svg
        className="absolute bottom-1/3 left-1/5 w-12 h-12 opacity-10 animate-float-slow"
        style={{ animationDelay: "1.5s" }}
        viewBox="0 0 24 24"
        fill="none"
        stroke="#a855f7"
        strokeWidth="1"
      >
        <rect x="4" y="4" width="16" height="16" rx="2" />
        <circle cx="9" cy="9" r="1" fill="#a855f7" />
        <circle cx="15" cy="9" r="1" fill="#a855f7" />
        <circle cx="9" cy="15" r="1" fill="#a855f7" />
        <circle cx="15" cy="15" r="1" fill="#a855f7" />
        <line x1="9" y1="9" x2="15" y2="15" />
        <line x1="15" y1="9" x2="9" y2="15" />
      </svg>

      {/* Glitching border effect on hero text area */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[500px] h-[200px] pointer-events-none">
        <div className="absolute inset-0 border border-primary/10 rounded-2xl animate-neon-pulse" />
        <div
          className="absolute inset-2 border border-secondary/5 rounded-xl animate-neon-pulse"
          style={{ animationDelay: "0.5s" }}
        />
      </div>
    </div>
  )
}
