"use client"

import type { FC } from "react"
import {
  ActionBarPrimitive,
  AuiIf,
  ComposerPrimitive,
  MessagePrimitive,
  ThreadPrimitive,
  useAuiState,
} from "@assistant-ui/react"
import { ArrowDown, ArrowUp, RefreshCw, Square } from "lucide-react"
import { Button } from "@/components/ui/button"

export function ChatThread() {
  return (
    <ThreadPrimitive.Root className="flex h-full min-h-[520px] flex-1 flex-col bg-background">
      <div className="border-b px-4 py-3">
        <p className="text-sm font-medium">Review chat</p>
        <p className="text-xs text-muted-foreground">
          Ask about architecture, dependencies, operations, or risks.
        </p>
      </div>
      <ThreadPrimitive.Viewport
        turnAnchor="bottom"
        className="flex min-h-0 flex-1 flex-col overflow-y-auto"
      >
        <div className="mx-auto flex w-full max-w-3xl flex-1 flex-col gap-6 px-4 py-6">
          <EmptyThreadWelcome />

          <div className="flex flex-col gap-5">
            <ThreadPrimitive.Messages components={{ UserMessage, AssistantMessage }} />
          </div>

          <ThreadPrimitive.ViewportFooter className="sticky bottom-0 mt-auto bg-background pb-4 pt-2">
            <ThreadPrimitive.ScrollToBottom asChild>
              <Button
                type="button"
                variant="outline"
                size="icon"
                className="mx-auto mb-2 hidden rounded-full data-[visible=true]:flex"
                aria-label="Scroll to bottom"
              >
                <ArrowDown className="h-4 w-4" />
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
    <div className="flex flex-1 flex-col justify-center gap-5 py-10">
      <div className="space-y-2">
        <h1 className="text-2xl font-semibold tracking-normal">Architecture review</h1>
        <p className="max-w-2xl text-sm leading-6 text-muted-foreground">
          Ask about the ingested documents. Answers use retrieved context and show the available
          sources.
        </p>
      </div>
      <div className="grid gap-2 sm:grid-cols-2">
        <PromptButton text="Summarize the architecture described in the ingested documents." />
        <PromptButton text="Which components participate in the ingestion flow?" />
        <PromptButton text="What external dependencies does the system have?" />
        <PromptButton text="What risks do you see in the local Kubernetes operation?" />
      </div>
    </div>
  )
}

function PromptButton({ text }: { text: string }) {
  return (
    <ThreadPrimitive.Suggestion prompt={text} method="replace" autoSend asChild>
      <Button
        type="button"
        variant="outline"
        className="h-auto justify-start whitespace-normal rounded-md px-3 py-3 text-left text-sm"
      >
        {text}
      </Button>
    </ThreadPrimitive.Suggestion>
  )
}

const UserMessage: FC = () => {
  return (
    <MessagePrimitive.Root className="grid grid-cols-[minmax(0,1fr)_auto]">
      <div className="col-start-2 max-w-[85%] rounded-md bg-secondary px-3 py-2 text-sm leading-6">
        <MessagePrimitive.Parts />
      </div>
    </MessagePrimitive.Root>
  )
}

const AssistantMessage: FC = () => {
  return (
    <MessagePrimitive.Root className="group space-y-2">
      <div className="max-w-none text-sm leading-6">
        <MessagePrimitive.Parts />
      </div>
      <AssistantActions />
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
            className="h-8 px-2 text-xs text-muted-foreground opacity-0 transition-opacity group-hover:opacity-100"
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
    <ComposerPrimitive.Root className="rounded-md border bg-background p-2 shadow-sm">
      <ComposerPrimitive.Input
        placeholder="Ask about architecture, dependencies, or risks..."
        rows={1}
        autoFocus
        className="max-h-36 min-h-10 w-full resize-none bg-transparent px-2 py-2 text-sm outline-none placeholder:text-muted-foreground"
      />
      <div className="flex items-center justify-end">
        <AuiIf condition={(state) => !state.thread.isRunning}>
          <ComposerPrimitive.Send asChild>
            <Button type="button" size="icon" className="h-8 w-8 rounded-full" aria-label="Send">
              <ArrowUp className="h-4 w-4" />
            </Button>
          </ComposerPrimitive.Send>
        </AuiIf>
        <AuiIf condition={(state) => state.thread.isRunning}>
          <ComposerPrimitive.Cancel asChild>
            <Button type="button" size="icon" className="h-8 w-8 rounded-full" aria-label="Stop">
              <Square className="h-3 w-3 fill-current" />
            </Button>
          </ComposerPrimitive.Cancel>
        </AuiIf>
      </div>
    </ComposerPrimitive.Root>
  )
}
