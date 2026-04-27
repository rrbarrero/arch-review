import { IngestForm } from "@/components/ingest-form"
import { ChatRuntimeProvider } from "@/components/chat/chat-runtime-provider"
import { ChatThread } from "@/components/chat/thread"

export function ArchReviewWorkspace() {
  return (
    <main className="min-h-screen bg-[linear-gradient(135deg,#fbfdfe_0%,#e6f3f2_42%,#fff8f6_100%)] text-foreground">
      <div className="grid min-h-screen w-full grid-cols-1 lg:grid-cols-[420px_minmax(0,1fr)]">
        <aside className="flex max-h-screen flex-col overflow-y-auto border-b border-pearl-aqua-700 bg-white/80 p-4 backdrop-blur-sm lg:border-b-0 lg:border-r">
          <div className="mx-auto flex w-full max-w-lg flex-col gap-5 lg:mx-0">
            <IngestForm />
          </div>
        </aside>

        <section className="flex min-h-0 flex-1 flex-col p-3 lg:p-5">
          <div className="flex flex-1 overflow-hidden rounded-lg border border-pearl-aqua-700 bg-white shadow-lg shadow-pearl-aqua-700/20 transition-shadow hover:shadow-xl hover:shadow-pearl-aqua-700/30">
            <ChatRuntimeProvider>
              <ChatThread />
            </ChatRuntimeProvider>
          </div>
        </section>
      </div>
    </main>
  )
}
