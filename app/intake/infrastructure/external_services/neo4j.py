from collections.abc import Sequence
from uuid import uuid4

from neo4j import AsyncGraphDatabase

from app.intake.domain.entities.chunk import DocumentChunk
from app.intake.domain.value_objects import ChunkStatus
from app.settings import Settings


class Neo4jGraphService:
    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or Settings()

    async def create_nodes(self, chunks: Sequence[DocumentChunk], document_id: str) -> list[DocumentChunk]:
        driver = AsyncGraphDatabase.driver(
            self._settings.neo4j_uri,
            auth=(self._settings.neo4j_user, self._settings.neo4j_password),
        )

        result = list(chunks)
        try:
            async with driver.session(database="neo4j") as session:
                await session.execute_write(self._create_document_node, document_id)
                for chunk in result:
                    node_id = await session.execute_write(self._create_chunk_node, chunk, document_id)
                    chunk.graph_node_id = node_id
                    chunk.status = ChunkStatus.GRAPH_PROCESSED
        finally:
            await driver.close()

        return result

    @staticmethod
    async def _create_document_node(tx, document_id: str) -> None:
        await tx.run(
            """
            MERGE (d:Document {id: $id})
            SET d.id = $id
            """,
            id=document_id,
        )

    @staticmethod
    async def _create_chunk_node(tx, chunk: DocumentChunk, document_id: str) -> str:
        node_id = str(uuid4())
        await tx.run(
            """
            CREATE (c:Chunk {
                id: $node_id,
                chunk_id: $chunk_id,
                content: $content,
                position: $position,
                level: $level
            })
            WITH c
            MATCH (d:Document {id: $document_id})
            CREATE (c)-[:PART_OF]->(d)
            """,
            node_id=node_id,
            chunk_id=chunk.id,
            content=chunk.content,
            position=chunk.position,
            level=chunk.level,
            document_id=document_id,
        )
        return node_id

    @staticmethod
    async def create_relationships(tx, chunks: Sequence[DocumentChunk]) -> None:
        for i in range(len(chunks) - 1):
            if chunks[i].graph_node_id and chunks[i + 1].graph_node_id:
                await tx.run(
                    """
                    MATCH (a:Chunk {id: $a_id})
                    MATCH (b:Chunk {id: $b_id})
                    CREATE (a)-[:NEXT]->(b)
                    """,
                    a_id=chunks[i].graph_node_id,
                    b_id=chunks[i + 1].graph_node_id,
                )
