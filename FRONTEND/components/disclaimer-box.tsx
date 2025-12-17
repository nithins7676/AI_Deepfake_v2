import { AlertTriangle } from "lucide-react"
import { GlassCard } from "./ui/glass-card"

interface DisclaimerBoxProps {
  variant?: "full" | "compact"
}

export function DisclaimerBox({ variant = "full" }: DisclaimerBoxProps) {
  if (variant === "compact") {
    return (
      <p className="text-muted-foreground text-xs text-center">
        Results may not be fully accurate. UNMASK is a testing model.
      </p>
    )
  }

  return (
    <GlassCard className="border-amber-500/30 bg-amber-500/5" glowColor="none">
      <div className="flex items-start gap-4">
        <AlertTriangle className="w-6 h-6 text-amber-500 shrink-0 mt-0.5" />
        <div className="space-y-2">
          <h3 className="font-semibold text-amber-500">Experimental Prototype</h3>
          <p className="text-muted-foreground text-sm leading-relaxed">
            This is an experimental test prototype. The model is still under training and{" "}
            <span className="text-amber-400 font-medium">NOT fully accurate</span>. Incorrect results may occur. Use for
            testing only.
          </p>
        </div>
      </div>
    </GlassCard>
  )
}
