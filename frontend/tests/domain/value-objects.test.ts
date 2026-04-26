import { describe, it, expect } from "vitest"
import { validateFile } from "@/domain/value-objects"

describe("validateFile", () => {
  it("accepts .md files under size limit", () => {
    const result = validateFile("readme.md", 100)
    expect(result).toEqual({ valid: true })
  })

  it("accepts .py files under size limit", () => {
    const result = validateFile("script.py", 100)
    expect(result).toEqual({ valid: true })
  })

  it("rejects unsupported extensions", () => {
    const result = validateFile("data.pdf", 100)
    expect(result).toEqual({ valid: false, error: expect.stringContaining("data.pdf") })
  })

  it("rejects files over size limit", () => {
    const result = validateFile("big.md", 600 * 1024)
    expect(result).toEqual({ valid: false, error: expect.stringContaining("big.md") })
  })
})
