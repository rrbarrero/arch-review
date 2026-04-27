import { IngestForm } from "@/components/ingest-form"
import { ChatRuntimeProvider } from "@/components/chat/chat-runtime-provider"
import { ChatThread } from "@/components/chat/thread"

export function ArchReviewWorkspace() {
  return (
    <main className="flex min-h-screen bg-background text-foreground">
      <div className="grid min-h-screen w-full grid-cols-1 lg:grid-cols-[380px_minmax(0,1fr)]">
        <aside className="border-b bg-muted/30 p-4 lg:border-b-0 lg:border-r">
          <div className="mx-auto flex max-w-lg flex-col gap-4 lg:mx-0">
            <div className="space-y-1 px-1">
              <p className="text-sm font-medium">Arch Review</p>
              <h1 className="text-xl font-semibold tracking-normal">Technical sources</h1>
              <p className="text-sm leading-6 text-muted-foreground">
                Upload Markdown or Python files and use the chat to query the generated context.
              </p>
            </div>
            <IngestForm />
          </div>
        </aside>

        <section className="min-h-[640px] p-4">
          <div className="flex h-full min-h-[calc(100vh-2rem)] overflow-hidden rounded-md border bg-background shadow-sm">
          <ChatRuntimeProvider>
            <ChatThread />
          </ChatRuntimeProvider>
          </div>
        </section>
      </div>
    </main>
  )
}
