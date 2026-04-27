"use client"

import type { FC } from "react"
import {
  ActionBarPrimitive,
  AuiIf,
  ComposerPrimitive,
  MessagePrimitive,
  ThreadPrimitive,
  useAuiState,
  useMessagePartText,
} from "@assistant-ui/react"
import {
  ArrowDown,
  ArrowUp,
  Bot,
  Braces,
  Database,
  GitBranch,
  MessageSquareText,
  RefreshCw,
  Sparkles,
  Square,
  User,
} from "lucide-react"
import { Button } from "@/components/ui/button"
import dynamic from "next/dynamic"

const MarkdownText = dynamic(
  () => import("@/components/chat/markdown-text").then((m) => m.MarkdownText),
  { ssr: false },
)

export function ChatThread() {
  return (
    <ThreadPrimitive.Root className="flex h-full min-h-[520px] flex-1 flex-col bg-card">
      <div className="border-b border-border bg-card px-5 py-4">
        <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <div className="flex items-center gap-3">
            <span className="flex h-10 w-10 items-center justify-center rounded-md bg-primary text-primary-foreground shadow-sm">
              <Bot className="h-5 w-5" />
            </span>
            <div>
              <p className="text-sm font-semibold text-console-ink">Review chat</p>
              <p className="text-xs text-console-muted">
                Ask about architecture, dependencies, operations, or risks.
              </p>
            </div>
          </div>
          <div className="flex flex-wrap gap-1.5">
            {["RAG", "Citations", "Local LLM"].map((tag) => (
              <span
                key={tag}
                className="min-w-20 rounded-full border border-border bg-console-panel-muted px-2.5 py-1 text-center text-xs font-medium text-console-secondary"
              >
                {tag}
              </span>
            ))}
          </div>
        </div>
      </div>
      <ThreadPrimitive.Viewport
        turnAnchor="bottom"
        className="flex min-h-0 flex-1 flex-col overflow-y-auto bg-background"
      >
        <div className="mx-auto flex w-full max-w-4xl flex-1 flex-col gap-6 px-4 py-6 sm:px-6">
          <EmptyThreadWelcome />

          <div className="flex flex-col gap-5">
            <ThreadPrimitive.Messages components={{ UserMessage, AssistantMessage }} />
          </div>

          <ThreadPrimitive.ViewportFooter className="sticky bottom-0 mt-auto border-t border-border bg-background/95 pb-3 pt-2">
            <ThreadPrimitive.ScrollToBottom asChild>
              <Button
                type="button"
                variant="outline"
                size="icon"
                className="mx-auto mb-2 hidden h-9 w-9 rounded-full bg-card shadow-md hover:bg-console-panel-muted data-[visible=true]:flex"
                aria-label="Scroll to bottom"
              >
                <ArrowDown className="h-4 w-4 text-console-primary" />
              </Button>
            </ThreadPrimitive.ScrollToBottom>
            <Composer />
          </ThreadPrimitive.ViewportFooter>
        </div>
      </ThreadPrimitive.Viewport>
    </ThreadPrimitive.Root>
  )
}

function EmptyThreadWelcome() {
  const isEmpty = useAuiState((state) => state.thread.messages.length === 0)
  return isEmpty ? <ThreadWelcome /> : null
}

function ThreadWelcome() {
  return (
    <div className="animate-fade-in flex flex-1 flex-col items-center justify-center gap-8 py-12 text-center">
      <div className="space-y-4">
        <span className="inline-flex items-center gap-2 rounded-full border border-border bg-console-panel-muted px-4 py-1.5 text-xs font-medium text-console-secondary shadow-sm">
          <Sparkles className="h-3.5 w-3.5" />
          Ready for evidence-backed review
        </span>
        <h1 className="text-2xl font-semibold tracking-normal text-console-ink">
          Architecture review
        </h1>
        <p className="mx-auto max-w-lg text-sm leading-6 text-console-muted">
          Ask about the ingested documents. Answers use retrieved context and show the available
          sources.
        </p>
      </div>
      <div className="grid w-full max-w-lg gap-3 sm:grid-cols-3">
        <WelcomeMetric icon={Database} label="Vector search" value="pgvector" />
        <WelcomeMetric icon={GitBranch} label="Graph context" value="Neo4j" />
        <WelcomeMetric icon={Braces} label="Code aware" value="Markdown + Python" />
      </div>
      <div className="grid w-full max-w-lg gap-2 sm:grid-cols-2">
        <PromptButton text="Summarize the architecture described in the ingested documents." />
        <PromptButton text="Which components participate in the ingestion flow?" />
        <PromptButton text="What external dependencies does the system have?" />
        <PromptButton text="What risks do you see in the local Kubernetes operation?" />
      </div>
    </div>
  )
}

function WelcomeMetric({
  icon: Icon,
  label,
  value,
}: {
  icon: typeof Database
  label: string
  value: string
}) {
  return (
    <div className="rounded-lg border border-border bg-card p-3.5 shadow-sm transition-colors hover:border-primary/40">
      <Icon className="mb-2 h-5 w-5 text-console-primary" />
      <p className="text-xs text-console-muted">{label}</p>
      <p className="mt-0.5 text-sm font-semibold text-console-ink">{value}</p>
    </div>
  )
}

function PromptButton({ text }: { text: string }) {
  return (
    <ThreadPrimitive.Suggestion prompt={text} method="replace" autoSend asChild>
      <Button
        type="button"
        variant="outline"
        className="h-auto justify-start whitespace-normal rounded-lg bg-card px-4 py-3 text-left text-sm text-console-muted shadow-sm transition-colors hover:border-primary/40 hover:bg-console-panel-muted hover:text-console-primary"
      >
        <MessageSquareText className="mr-2 h-4 w-4 shrink-0 text-console-primary/70" />
        {text}
      </Button>
    </ThreadPrimitive.Suggestion>
  )
}

const UserMessage: FC = () => {
  return (
    <MessagePrimitive.Root className="message-enter grid grid-cols-[minmax(0,1fr)_auto] gap-3">
      <div className="col-start-2 flex max-w-[80%] items-start gap-3">
        <div className="rounded-lg rounded-br-sm bg-primary px-4 py-3 text-sm leading-6 text-primary-foreground shadow-sm">
          <MessagePrimitive.Parts />
        </div>
        <span className="mt-1 flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-primary text-primary-foreground shadow-sm">
          <User className="h-4 w-4" />
        </span>
      </div>
    </MessagePrimitive.Root>
  )
}

function MarkdownTextPart() {
  const { text } = useMessagePartText()
  return <MarkdownText text={text} />
}

const AssistantMessage: FC = () => {
  return (
    <MessagePrimitive.Root className="message-enter group flex items-start gap-3">
      <span className="mt-1 flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-console-panel-muted text-console-primary shadow-sm">
        <Bot className="h-4 w-4" />
      </span>
      <div className="min-w-0 flex-1 space-y-2">
        <div className="max-w-none rounded-lg rounded-tl-sm border border-border bg-card px-5 py-3.5 text-sm leading-6 text-console-ink shadow-sm">
          <MessagePrimitive.Parts components={{ Text: MarkdownTextPart }} />
        </div>
        <AssistantActions />
      </div>
    </MessagePrimitive.Root>
  )
}

function AssistantActions() {
  const isRunning = useAuiState((state) => state.thread.isRunning)

  return (
    <AuiIf condition={() => !isRunning}>
      <ActionBarPrimitive.Root>
        <ActionBarPrimitive.Reload asChild>
          <Button
            type="button"
            variant="ghost"
            size="sm"
            className="h-8 gap-1.5 px-2.5 text-xs text-console-muted opacity-0 transition-colors hover:bg-console-panel-muted hover:text-console-primary group-hover:opacity-100"
          >
            <RefreshCw className="h-3.5 w-3.5" />
            Regenerate
          </Button>
        </ActionBarPrimitive.Reload>
      </ActionBarPrimitive.Root>
    </AuiIf>
  )
}

function Composer() {
  return (
    <ComposerPrimitive.Root className="rounded-lg border border-border bg-card p-2 shadow-md transition-shadow focus-within:ring-2 focus-within:ring-ring/25">
      <ComposerPrimitive.Input
        placeholder="Ask about architecture, dependencies, or risks..."
        rows={1}
        autoFocus
        className="max-h-36 min-h-12 w-full resize-none bg-transparent px-3 py-2.5 text-sm text-console-ink outline-none placeholder:text-console-muted"
      />
      <div className="flex items-center justify-between px-2 pb-1">
        <p className="text-xs text-console-muted">Answers are grounded in retrieved chunks</p>
        <div className="flex items-center gap-1">
          <AuiIf condition={(state) => !state.thread.isRunning}>
            <ComposerPrimitive.Send asChild>
              <Button
                type="button"
                size="icon"
                className="h-9 w-9 rounded-md bg-primary text-primary-foreground shadow-sm transition-colors hover:bg-console-primary-hover"
                aria-label="Send"
              >
                <ArrowUp className="h-4 w-4" />
              </Button>
            </ComposerPrimitive.Send>
          </AuiIf>
          <AuiIf condition={(state) => state.thread.isRunning}>
            <ComposerPrimitive.Cancel asChild>
              <Button
                type="button"
                size="icon"
                className="h-9 w-9 rounded-md bg-console-accent text-white shadow-sm transition-colors hover:bg-console-accent/90"
                aria-label="Stop"
              >
                <Square className="h-3 w-3 fill-current" />
              </Button>
            </ComposerPrimitive.Cancel>
          </AuiIf>
        </div>
      </div>
    </ComposerPrimitive.Root>
  )
}
