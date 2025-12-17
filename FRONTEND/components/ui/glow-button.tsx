"use client"

import { cn } from "@/lib/utils"
import { type ButtonHTMLAttributes, forwardRef } from "react"

interface GlowButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary" | "outline"
  size?: "sm" | "md" | "lg"
  glowColor?: "blue" | "purple"
}

const GlowButton = forwardRef<HTMLButtonElement, GlowButtonProps>(
  ({ className, variant = "primary", size = "md", glowColor = "blue", children, ...props }, ref) => {
    return (
      <button
        ref={ref}
        className={cn(
          "relative font-semibold rounded-xl transition-all duration-300 cursor-pointer",
          "disabled:opacity-50 disabled:cursor-not-allowed",
          {
            "bg-primary text-primary-foreground hover:bg-primary/90": variant === "primary",
            "bg-accent text-accent-foreground hover:bg-accent/90": variant === "secondary",
            "bg-transparent border-2 border-primary text-primary hover:bg-primary/10": variant === "outline",
          },
          {
            "px-4 py-2 text-sm": size === "sm",
            "px-6 py-3 text-base": size === "md",
            "px-8 py-4 text-lg": size === "lg",
          },
          glowColor === "blue"
            ? "hover:shadow-[0_0_30px_rgba(59,130,246,0.5)]"
            : "hover:shadow-[0_0_30px_rgba(168,85,247,0.5)]",
          className,
        )}
        {...props}
      >
        {children}
      </button>
    )
  },
)
GlowButton.displayName = "GlowButton"

export { GlowButton }
