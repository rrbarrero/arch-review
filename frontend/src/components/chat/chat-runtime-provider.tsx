"use client"

import type { ReactNode } from "react"
import {
  AssistantRuntimeProvider,
  useLocalRuntime,
  type ChatModelAdapter,
  type ThreadMessage,
} from "@assistant-ui/react"
import {
  askQuestion,
  type ChatCitation,
  type ChatMessageInput,
} from "@/infrastructure/api/client"

function partText(part: ThreadMessage["content"][number]): string {
  if (part.type !== "text") return ""
  return part.text
}

function messageText(message: ThreadMessage): string {
  return message.content.map(partText).join("").trim()
}

function toApiMessages(messages: readonly ThreadMessage[]): ChatMessageInput[] {
  return messages
    .filter((message) => message.role === "user" || message.role === "assistant")
    .map((message) => ({
      role: message.role,
      content: messageText(message),
    }))
    .filter((message) => message.content.length > 0)
}

function citationsMarkdown(citations: ChatCitation[]): string {
  if (citations.length === 0) return ""

  const sources = citations
    .map((citation) => {
      const score = citation.score === null ? "" : ` · score ${citation.score.toFixed(2)}`
      return `- ${citation.filename} · chunk ${citation.chunkId}${score}`
    })
    .join("\n")

  return `\n\nSources:\n${sources}`
}

const modelAdapter: ChatModelAdapter = {
  async run({ messages, abortSignal }) {
    const result = await askQuestion(toApiMessages(messages), abortSignal)

    return {
      content: [
        {
          type: "text",
          text: `${result.text}${citationsMarkdown(result.citations)}`,
        },
      ],
    }
  },
}

export function ChatRuntimeProvider({ children }: { children: ReactNode }) {
  const runtime = useLocalRuntime(modelAdapter)

  return <AssistantRuntimeProvider runtime={runtime}>{children}</AssistantRuntimeProvider>
}
