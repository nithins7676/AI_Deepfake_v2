"use client"

export function ScanAnimation() {
  return (
    <div className="absolute inset-0 overflow-hidden rounded-xl pointer-events-none">
      <div className="absolute inset-0 bg-gradient-to-b from-primary/20 via-primary/10 to-transparent h-1/3 animate-scan" />
      <div className="absolute inset-0 bg-[linear-gradient(transparent_50%,rgba(59,130,246,0.03)_50%)] bg-[length:100%_4px]" />
    </div>
  )
}
