import { cn } from "@/lib/utils"
import { type HTMLAttributes, forwardRef } from "react"

interface GlassCardProps extends HTMLAttributes<HTMLDivElement> {
  glowColor?: "blue" | "purple" | "none"
  hover?: boolean
}

const GlassCard = forwardRef<HTMLDivElement, GlassCardProps>(
  ({ className, glowColor = "blue", hover = false, children, ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={cn(
          "glass-panel rounded-2xl p-6 transition-all duration-300",
          {
            "neon-glow": glowColor === "blue",
            "neon-glow-purple": glowColor === "purple",
          },
          hover && "hover:scale-[1.02] hover:border-primary/50 cursor-pointer",
          className,
        )}
        {...props}
      >
        {children}
      </div>
    )
  },
)
GlassCard.displayName = "GlassCard"

export { GlassCard }
