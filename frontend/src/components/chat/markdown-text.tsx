"use client"

import { useMemo } from "react"
import { marked } from "marked"

marked.use({
  gfm: true,
  breaks: false,
})

export function MarkdownText({ text }: { text: string }) {
  const html = useMemo(() => {
    return marked.parse(text, { async: false }) as string
  }, [text])

  return (
    <div
      className="markdown-body text-sm leading-6 text-console-ink"
      dangerouslySetInnerHTML={{ __html: html }}
    />
  )
}
