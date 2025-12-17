"use client"

import { useEffect, useRef } from "react"

export function NeuralNetworkBg() {
  const canvasRef = useRef<HTMLCanvasElement>(null)

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return

    const ctx = canvas.getContext("2d")
    if (!ctx) return

    let animationId: number
    let nodes: { x: number; y: number; vx: number; vy: number; radius: number; pulse: number }[] = []

    const resize = () => {
      canvas.width = window.innerWidth
      canvas.height = window.innerHeight
      initNodes()
    }

    const initNodes = () => {
      nodes = []
      const nodeCount = Math.floor((canvas.width * canvas.height) / 25000)
      for (let i = 0; i < nodeCount; i++) {
        nodes.push({
          x: Math.random() * canvas.width,
          y: Math.random() * canvas.height,
          vx: (Math.random() - 0.5) * 0.5,
          vy: (Math.random() - 0.5) * 0.5,
          radius: Math.random() * 2 + 1,
          pulse: Math.random() * Math.PI * 2,
        })
      }
    }

    const draw = () => {
      ctx.fillStyle = "rgba(10, 10, 10, 0.1)"
      ctx.fillRect(0, 0, canvas.width, canvas.height)

      // Update and draw nodes
      nodes.forEach((node, i) => {
        node.x += node.vx
        node.y += node.vy
        node.pulse += 0.02

        // Bounce off edges
        if (node.x < 0 || node.x > canvas.width) node.vx *= -1
        if (node.y < 0 || node.y > canvas.height) node.vy *= -1

        // Draw connections to nearby nodes
        nodes.slice(i + 1).forEach((other) => {
          const dx = other.x - node.x
          const dy = other.y - node.y
          const dist = Math.sqrt(dx * dx + dy * dy)

          if (dist < 150) {
            const opacity = (1 - dist / 150) * 0.3
            ctx.beginPath()
            ctx.strokeStyle = `rgba(59, 130, 246, ${opacity})`
            ctx.lineWidth = 0.5
            ctx.moveTo(node.x, node.y)
            ctx.lineTo(other.x, other.y)
            ctx.stroke()
          }
        })

        // Draw node with pulse effect
        const pulseSize = Math.sin(node.pulse) * 0.5 + 1
        const gradient = ctx.createRadialGradient(node.x, node.y, 0, node.x, node.y, node.radius * pulseSize * 3)
        gradient.addColorStop(0, "rgba(59, 130, 246, 0.8)")
        gradient.addColorStop(0.5, "rgba(168, 85, 247, 0.3)")
        gradient.addColorStop(1, "transparent")

        ctx.beginPath()
        ctx.fillStyle = gradient
        ctx.arc(node.x, node.y, node.radius * pulseSize * 3, 0, Math.PI * 2)
        ctx.fill()

        // Core dot
        ctx.beginPath()
        ctx.fillStyle = "#3b82f6"
        ctx.arc(node.x, node.y, node.radius * pulseSize, 0, Math.PI * 2)
        ctx.fill()
      })

      animationId = requestAnimationFrame(draw)
    }

    resize()
    window.addEventListener("resize", resize)
    draw()

    return () => {
      window.removeEventListener("resize", resize)
      cancelAnimationFrame(animationId)
    }
  }, [])

  return <canvas ref={canvasRef} className="fixed inset-0 pointer-events-none opacity-60" style={{ zIndex: 0 }} />
}
