-- migrate:up
ALTER TABLE chunks ADD COLUMN level INTEGER NOT NULL DEFAULT 0;
ALTER TABLE chunks ADD COLUMN parent_ids TEXT[] NOT NULL DEFAULT '{}';
CREATE INDEX IF NOT EXISTS idx_chunks_level ON chunks(level);

-- migrate:down
DROP INDEX IF EXISTS idx_chunks_level;
ALTER TABLE chunks DROP COLUMN IF EXISTS parent_ids;
ALTER TABLE chunks DROP COLUMN IF EXISTS level;
