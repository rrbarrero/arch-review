import { render, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { describe, expect, it, vi } from "vitest"
import { IngestForm } from "@/components/ingest-form"

const ingest = vi.fn()

vi.mock("@/hooks/use-ingest", () => ({
  useIngest: () => ({ ingest }),
}))

describe("IngestForm", () => {
  it("wires the visual drop area to the hidden file input and resets it after selection", async () => {
    const user = userEvent.setup()
    const file = new File(["# ADR"], "adr.md", { type: "text/markdown" })

    render(<IngestForm />)

    const input = screen.getByLabelText(/choose or drag files/i) as HTMLInputElement

    await user.upload(input, file)

    expect(ingest).toHaveBeenCalledWith([file])
    expect(input.value).toBe("")
  })
})
