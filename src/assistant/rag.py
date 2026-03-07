"""
Modulo RAG (Retrieval-Augmented Generation) para o Assistente Medico Virtual.
Implementa chunking semantico de protocolos medicos e indexacao no ChromaDB.
"""

import re
from pathlib import Path
from typing import Optional

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer


# Configuracoes padrao
DEFAULT_EMBEDDING_MODEL = "intfloat/multilingual-e5-base"
DEFAULT_CHUNK_SIZE = 1500
DEFAULT_CHUNK_OVERLAP = 200
DEFAULT_COLLECTION_NAME = "protocolos_medicos"


class SemanticChunker:
    """Chunker semantico que divide documentos Markdown por secoes."""

    def __init__(
        self,
        max_chunk_size: int = DEFAULT_CHUNK_SIZE,
        chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
    ):
        self.max_chunk_size = max_chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_markdown(self, text: str, source: str) -> list[dict]:
        """
        Divide um documento Markdown em chunks semanticos.

        Args:
            text: Conteudo do documento Markdown
            source: Nome do arquivo fonte (para metadados)

        Returns:
            Lista de dicts com 'content', 'metadata'
        """
        chunks = []

        # Dividir por headers (## ou ###)
        # Regex captura o header e seu conteudo ate o proximo header
        sections = self._split_by_headers(text)

        for section in sections:
            section_title = section.get("title", "")
            section_content = section.get("content", "").strip()

            if not section_content:
                continue

            # Se a secao for maior que max_chunk_size, subdividir
            if len(section_content) > self.max_chunk_size:
                sub_chunks = self._split_large_section(
                    section_content, section_title
                )
                for i, sub_chunk in enumerate(sub_chunks):
                    chunks.append({
                        "content": sub_chunk,
                        "metadata": {
                            "source": source,
                            "section": section_title,
                            "chunk_index": i,
                            "total_chunks": len(sub_chunks),
                        },
                    })
            else:
                # Incluir titulo da secao no chunk para contexto
                content = f"## {section_title}\n\n{section_content}" if section_title else section_content
                chunks.append({
                    "content": content,
                    "metadata": {
                        "source": source,
                        "section": section_title,
                        "chunk_index": 0,
                        "total_chunks": 1,
                    },
                })

        return chunks

    def _split_by_headers(self, text: str) -> list[dict]:
        """Divide texto por headers Markdown (## ou ###)."""
        # Pattern para capturar headers de nivel 2 ou 3
        pattern = r"^(#{2,3})\s+(.+)$"

        sections = []
        current_section = {"title": "", "content": ""}
        lines = text.split("\n")

        for line in lines:
            match = re.match(pattern, line)
            if match:
                # Salvar secao anterior se tiver conteudo
                if current_section["content"].strip():
                    sections.append(current_section)
                # Iniciar nova secao
                current_section = {
                    "title": match.group(2).strip(),
                    "content": "",
                }
            else:
                current_section["content"] += line + "\n"

        # Adicionar ultima secao
        if current_section["content"].strip():
            sections.append(current_section)

        return sections

    def _split_large_section(
        self, content: str, section_title: str
    ) -> list[str]:
        """Divide secoes grandes em chunks menores com overlap."""
        chunks = []
        start = 0

        while start < len(content):
            end = start + self.max_chunk_size

            # Tentar quebrar em um limite de paragrafo ou sentenca
            if end < len(content):
                # Procurar quebra de paragrafo
                newline_pos = content.rfind("\n\n", start, end)
                if newline_pos > start + self.max_chunk_size // 2:
                    end = newline_pos
                else:
                    # Procurar fim de sentenca
                    sentence_end = max(
                        content.rfind(". ", start, end),
                        content.rfind(".\n", start, end),
                    )
                    if sentence_end > start + self.max_chunk_size // 2:
                        end = sentence_end + 1

            chunk_content = content[start:end].strip()

            # Adicionar contexto da secao no primeiro chunk
            if start == 0 and section_title:
                chunk_content = f"## {section_title}\n\n{chunk_content}"

            if chunk_content:
                chunks.append(chunk_content)

            # Proximo chunk com overlap
            start = end - self.chunk_overlap
            if start < 0:
                start = 0

            # Evitar loop infinito
            if start >= len(content) - self.chunk_overlap:
                break

        return chunks


class ProtocolIndexer:
    """Indexador de protocolos medicos no ChromaDB."""

    def __init__(
        self,
        persist_directory: str = "chroma_db",
        collection_name: str = DEFAULT_COLLECTION_NAME,
        embedding_model: str = DEFAULT_EMBEDDING_MODEL,
    ):
        self.persist_directory = Path(persist_directory)
        self.collection_name = collection_name
        self.embedding_model_name = embedding_model

        # Inicializar embedding model
        print(f"Carregando modelo de embeddings: {embedding_model}")
        self.embedding_model = SentenceTransformer(embedding_model)

        # Inicializar ChromaDB
        self.persist_directory.mkdir(parents=True, exist_ok=True)
        self.client = chromadb.PersistentClient(
            path=str(self.persist_directory),
            settings=Settings(anonymized_telemetry=False),
        )

        # Criar ou obter collection
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"embedding_model": embedding_model},
        )

        # Chunker
        self.chunker = SemanticChunker()

    def _generate_embeddings(self, texts: list[str]) -> list[list[float]]:
        """Gera embeddings para uma lista de textos."""
        # Para o modelo E5, adicionar prefixo "passage: " para documentos
        prefixed_texts = [f"passage: {text}" for text in texts]
        embeddings = self.embedding_model.encode(
            prefixed_texts,
            show_progress_bar=True,
            convert_to_numpy=True,
        )
        return embeddings.tolist()

    def index_document(self, filepath: Path, doc_type: str = "protocolo") -> int:
        """
        Indexa um documento Markdown no ChromaDB.

        Args:
            filepath: Caminho para o arquivo .md
            doc_type: Tipo do documento (protocolo, emergencia, etc.)

        Returns:
            Numero de chunks indexados
        """
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        source = filepath.stem  # Nome do arquivo sem extensao
        chunks = self.chunker.chunk_markdown(content, source)

        if not chunks:
            print(f"  Aviso: Nenhum chunk gerado para {source}")
            return 0

        # Preparar dados para ChromaDB
        ids = [f"{source}_{i}" for i in range(len(chunks))]
        documents = [chunk["content"] for chunk in chunks]
        metadatas = [
            {**chunk["metadata"], "doc_type": doc_type}
            for chunk in chunks
        ]

        # Gerar embeddings
        embeddings = self._generate_embeddings(documents)

        # Inserir no ChromaDB
        self.collection.upsert(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
        )

        return len(chunks)

    def index_directory(
        self,
        directory: Path,
        doc_type: str = "protocolo",
        pattern: str = "*.md",
    ) -> dict:
        """
        Indexa todos os documentos Markdown de um diretorio.

        Args:
            directory: Diretorio com arquivos .md
            doc_type: Tipo dos documentos
            pattern: Padrao glob para arquivos

        Returns:
            Dict com estatisticas de indexacao
        """
        files = list(directory.glob(pattern))
        total_chunks = 0
        indexed_files = 0

        print(f"\nIndexando {len(files)} arquivos de {directory}...")

        for filepath in sorted(files):
            if filepath.name.startswith(".") or filepath.name == "index.json":
                continue

            chunks = self.index_document(filepath, doc_type)
            print(f"  {filepath.name}: {chunks} chunks")
            total_chunks += chunks
            indexed_files += 1

        return {
            "directory": str(directory),
            "doc_type": doc_type,
            "files_indexed": indexed_files,
            "total_chunks": total_chunks,
        }

    def get_stats(self) -> dict:
        """Retorna estatisticas da collection."""
        return {
            "collection_name": self.collection_name,
            "total_documents": self.collection.count(),
            "embedding_model": self.embedding_model_name,
            "persist_directory": str(self.persist_directory),
        }

    def clear_collection(self):
        """Limpa todos os documentos da collection."""
        # Deletar e recriar collection
        self.client.delete_collection(self.collection_name)
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"embedding_model": self.embedding_model_name},
        )
        print(f"Collection '{self.collection_name}' limpa.")


class ProtocolRetriever:
    """Recuperador de protocolos medicos do ChromaDB."""

    def __init__(
        self,
        persist_directory: str = "chroma_db",
        collection_name: str = DEFAULT_COLLECTION_NAME,
        embedding_model: str = DEFAULT_EMBEDDING_MODEL,
    ):
        self.persist_directory = Path(persist_directory)
        self.embedding_model_name = embedding_model

        # Carregar embedding model
        self.embedding_model = SentenceTransformer(embedding_model)

        # Conectar ao ChromaDB
        self.client = chromadb.PersistentClient(
            path=str(self.persist_directory),
            settings=Settings(anonymized_telemetry=False),
        )
        self.collection = self.client.get_collection(name=collection_name)

    def _generate_query_embedding(self, query: str) -> list[float]:
        """Gera embedding para uma query."""
        # Para o modelo E5, adicionar prefixo "query: " para consultas
        prefixed_query = f"query: {query}"
        embedding = self.embedding_model.encode(
            prefixed_query,
            convert_to_numpy=True,
        )
        return embedding.tolist()

    def search(
        self,
        query: str,
        n_results: int = 5,
        doc_type: Optional[str] = None,
    ) -> list[dict]:
        """
        Busca protocolos relevantes para uma query.

        Args:
            query: Pergunta ou termo de busca
            n_results: Numero maximo de resultados
            doc_type: Filtrar por tipo de documento (opcional)

        Returns:
            Lista de resultados com conteudo, metadados e distancia
        """
        query_embedding = self._generate_query_embedding(query)

        # Construir filtro se necessario
        where_filter = None
        if doc_type:
            where_filter = {"doc_type": doc_type}

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=where_filter,
            include=["documents", "metadatas", "distances"],
        )

        # Formatar resultados
        formatted_results = []
        for i in range(len(results["ids"][0])):
            formatted_results.append({
                "id": results["ids"][0][i],
                "content": results["documents"][0][i],
                "metadata": results["metadatas"][0][i],
                "distance": results["distances"][0][i],
            })

        return formatted_results

    def get_context_for_query(
        self,
        query: str,
        n_results: int = 3,
        max_context_length: int = 4000,
    ) -> str:
        """
        Recupera contexto formatado para usar em prompts LLM.

        Args:
            query: Pergunta do usuario
            n_results: Numero de documentos a recuperar
            max_context_length: Tamanho maximo do contexto

        Returns:
            String formatada com contexto dos protocolos
        """
        results = self.search(query, n_results=n_results)

        context_parts = []
        total_length = 0

        for result in results:
            source = result["metadata"].get("source", "Desconhecido")
            section = result["metadata"].get("section", "")
            content = result["content"]

            # Formatar entrada
            entry = f"[Fonte: {source}]"
            if section:
                entry += f" [Seção: {section}]"
            entry += f"\n{content}\n"

            # Verificar limite de tamanho
            if total_length + len(entry) > max_context_length:
                break

            context_parts.append(entry)
            total_length += len(entry)

        return "\n---\n".join(context_parts)
