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

  it("accepts .toml files under size limit", () => {
    const result = validateFile("config.toml", 100)
    expect(result).toEqual({ valid: true })
  })

  it("accepts .json files under size limit", () => {
    const result = validateFile("data.json", 100)
    expect(result).toEqual({ valid: true })
  })

  it("accepts .txt files under size limit", () => {
    const result = validateFile("notes.txt", 100)
    expect(result).toEqual({ valid: true })
  })

  it("accepts .ts files under size limit", () => {
    const result = validateFile("component.ts", 100)
    expect(result).toEqual({ valid: true })
  })

  it("accepts .yml files under size limit", () => {
    const result = validateFile("config.yml", 100)
    expect(result).toEqual({ valid: true })
  })

  it("accepts .yaml files under size limit", () => {
    const result = validateFile("config.yaml", 100)
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
