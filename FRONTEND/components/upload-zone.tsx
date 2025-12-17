"use client"

import type React from "react"

import { useCallback, useState } from "react"
import { Upload, X, FileImage, FileVideo } from "lucide-react"
import { cn } from "@/lib/utils"

interface UploadZoneProps {
  type: "image" | "video"
  onFileSelect: (file: File | null) => void
  file: File | null
  preview: string | null
}

export function UploadZone({ type, onFileSelect, file, preview }: UploadZoneProps) {
  const [isDragging, setIsDragging] = useState(false)

  const acceptTypes =
    type === "image" ? "image/jpeg,image/png,image/webp,image/gif" : "video/mp4,video/webm,video/quicktime"

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === "dragenter" || e.type === "dragover") {
      setIsDragging(true)
    } else if (e.type === "dragleave") {
      setIsDragging(false)
    }
  }, [])

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault()
      e.stopPropagation()
      setIsDragging(false)

      const droppedFile = e.dataTransfer.files[0]
      if (droppedFile) {
        onFileSelect(droppedFile)
      }
    },
    [onFileSelect],
  )

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0]
    if (selectedFile) {
      onFileSelect(selectedFile)
    }
  }

  const clearFile = () => {
    onFileSelect(null)
  }

  if (file && preview) {
    return (
      <div className="relative rounded-xl overflow-hidden border border-border bg-muted/30">
        <button
          onClick={clearFile}
          className="absolute top-3 right-3 z-10 p-2 rounded-lg bg-background/80 hover:bg-background transition-colors"
        >
          <X className="w-4 h-4" />
        </button>
        {type === "image" ? (
          <img src={preview || "/placeholder.svg"} alt="Preview" className="w-full h-64 object-contain" />
        ) : (
          <video src={preview} controls className="w-full h-64 object-contain" />
        )}
        <div className="p-3 border-t border-border bg-muted/50">
          <p className="text-sm text-muted-foreground truncate">{file.name}</p>
        </div>
      </div>
    )
  }

  return (
    <div
      onDragEnter={handleDrag}
      onDragLeave={handleDrag}
      onDragOver={handleDrag}
      onDrop={handleDrop}
      className={cn(
        "relative rounded-xl border-2 border-dashed transition-all duration-300 cursor-pointer",
        isDragging ? "border-primary bg-primary/10" : "border-border hover:border-primary/50 hover:bg-muted/30",
      )}
    >
      <input
        type="file"
        accept={acceptTypes}
        onChange={handleFileChange}
        className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
      />
      <div className="flex flex-col items-center justify-center py-12 px-4 space-y-4">
        <div
          className={cn(
            "w-16 h-16 rounded-xl flex items-center justify-center transition-colors",
            isDragging ? "bg-primary/20" : "bg-muted",
          )}
        >
          {type === "image" ? (
            <FileImage className={cn("w-8 h-8", isDragging ? "text-primary" : "text-muted-foreground")} />
          ) : (
            <FileVideo className={cn("w-8 h-8", isDragging ? "text-primary" : "text-muted-foreground")} />
          )}
        </div>
        <div className="text-center space-y-1">
          <p className="font-medium">
            <span className="text-primary">Click to upload</span> or drag and drop
          </p>
          <p className="text-sm text-muted-foreground">
            {type === "image" ? "PNG, JPG, WEBP or GIF" : "MP4, WEBM or MOV"}
          </p>
        </div>
        <div className="flex items-center gap-2 text-muted-foreground">
          <Upload className="w-4 h-4" />
          <span className="text-sm">Max file size: 50MB</span>
        </div>
      </div>
    </div>
  )
}
