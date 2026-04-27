const MAX_FILE_SIZE = 500 * 1024
const ALLOWED_EXTENSIONS: readonly string[] = [".md", ".py", ".toml", ".json", ".txt", ".ts", ".yml", ".yaml"]

function extension(filename: string): string {
  const dot = filename.lastIndexOf(".")
  return dot !== -1 ? filename.slice(dot).toLowerCase() : ""
}

export type FileValidation = { valid: true } | { valid: false; error: string }

export function validateFile(filename: string, size: number): FileValidation {
  const ext = extension(filename)
  if (!ALLOWED_EXTENSIONS.includes(ext)) {
    return { valid: false, error: `"${filename}": extensión no soportada "${ext}"` }
  }
  if (size > MAX_FILE_SIZE) {
    return {
      valid: false,
      error: `"${filename}": demasiado grande (${size} bytes, máx ${MAX_FILE_SIZE})`,
    }
  }
  return { valid: true }
}
