import { IngestForm } from "@/components/ingest-form"
import { ChatRuntimeProvider } from "@/components/chat/chat-runtime-provider"
import { ChatThread } from "@/components/chat/thread"

export function ArchReviewWorkspace() {
  return (
    <main className="min-h-screen bg-background text-foreground">
      <div className="grid min-h-screen w-full grid-cols-1 lg:grid-cols-[392px_minmax(0,1fr)]">
        <aside className="flex max-h-screen flex-col overflow-y-auto border-b border-border bg-console-panel-muted p-4 lg:border-b-0 lg:border-r">
          <div className="mx-auto flex w-full max-w-lg flex-col gap-4 lg:mx-0">
            <IngestForm />
          </div>
        </aside>

        <section className="flex min-h-0 flex-1 flex-col p-3 lg:p-4">
          <div className="flex flex-1 overflow-hidden rounded-lg border border-border bg-card shadow-sm">
            <ChatRuntimeProvider>
              <ChatThread />
            </ChatRuntimeProvider>
          </div>
        </section>
      </div>
    </main>
  )
}
