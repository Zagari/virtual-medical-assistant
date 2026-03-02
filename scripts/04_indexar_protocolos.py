#!/usr/bin/env python3
"""
Script 04 - Indexar Protocolos no ChromaDB
==========================================
Realiza chunking semantico dos protocolos medicos e indexa no ChromaDB
para uso no sistema RAG do assistente.

Uso:
    python scripts/04_indexar_protocolos.py [--clear]

Opcoes:
    --clear     Limpa a collection antes de indexar

Fontes indexadas:
    - data/linhas_de_cuidado/extracted/   (14 Linhas de Cuidado)
    - data/synthetic/protocolos_complementares/  (5 protocolos de emergencia)

Saida:
    chroma_db/   (banco vetorial persistente)
"""

import argparse
import sys
import time
from pathlib import Path

# Adicionar raiz do projeto ao path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.assistant.rag import ProtocolIndexer


def main():
    parser = argparse.ArgumentParser(
        description="Indexa protocolos médicos no ChromaDB para RAG."
    )
    parser.add_argument(
        "--clear",
        action="store_true",
        help="Limpa a collection antes de indexar",
    )
    args = parser.parse_args()

    print("=" * 60)
    print("SCRIPT 04 - Indexação de Protocolos no ChromaDB")
    print("=" * 60)

    start_time = time.time()

    # Diretorios de entrada
    linhas_cuidado_dir = PROJECT_ROOT / "data" / "linhas_de_cuidado" / "extracted"
    protocolos_emerg_dir = PROJECT_ROOT / "data" / "synthetic" / "protocolos_complementares"
    chroma_dir = PROJECT_ROOT / "chroma_db"

    # Verificar pre-condicoes
    if not linhas_cuidado_dir.exists():
        print(f"ERRO: Diretório não encontrado: {linhas_cuidado_dir}")
        print("Execute a extração dos PDFs primeiro.")
        sys.exit(1)

    if not protocolos_emerg_dir.exists():
        print(f"ERRO: Diretório não encontrado: {protocolos_emerg_dir}")
        print("Execute scripts/01_gerar_dados_sinteticos.py primeiro.")
        sys.exit(1)

    # Contar arquivos
    n_linhas = len(list(linhas_cuidado_dir.glob("*.md")))
    n_emerg = len([f for f in protocolos_emerg_dir.glob("*.md") if f.name != "index.json"])

    print(f"\nFontes de dados:")
    print(f"  - Linhas de Cuidado: {n_linhas} arquivos em {linhas_cuidado_dir}")
    print(f"  - Protocolos Emergência: {n_emerg} arquivos em {protocolos_emerg_dir}")
    print(f"  - Saída: {chroma_dir}")

    # Inicializar indexador
    print("\n" + "-" * 60)
    indexer = ProtocolIndexer(
        persist_directory=str(chroma_dir),
        collection_name="protocolos_medicos",
        embedding_model="intfloat/multilingual-e5-base",
    )

    # Limpar collection se solicitado
    if args.clear:
        print("\nLimpando collection existente...")
        indexer.clear_collection()

    # Indexar Linhas de Cuidado
    print("\n" + "-" * 60)
    stats_linhas = indexer.index_directory(
        linhas_cuidado_dir,
        doc_type="linha_cuidado",
        pattern="*.md",
    )

    # Indexar Protocolos de Emergência
    print("\n" + "-" * 60)
    stats_emerg = indexer.index_directory(
        protocolos_emerg_dir,
        doc_type="emergencia",
        pattern="*.md",
    )

    # Estatisticas finais
    elapsed = time.time() - start_time
    final_stats = indexer.get_stats()

    print("\n" + "=" * 60)
    print("RESUMO DA INDEXAÇÃO")
    print("=" * 60)
    print(f"\nLinhas de Cuidado:")
    print(f"  - Arquivos indexados: {stats_linhas['files_indexed']}")
    print(f"  - Chunks gerados: {stats_linhas['total_chunks']}")

    print(f"\nProtocolos de Emergência:")
    print(f"  - Arquivos indexados: {stats_emerg['files_indexed']}")
    print(f"  - Chunks gerados: {stats_emerg['total_chunks']}")

    print(f"\nTotal na Collection:")
    print(f"  - Documentos: {final_stats['total_documents']}")
    print(f"  - Modelo de embeddings: {final_stats['embedding_model']}")
    print(f"  - Persistido em: {final_stats['persist_directory']}")

    print(f"\nTempo total: {elapsed:.1f} segundos")
    print("\n" + "=" * 60)
    print("Concluído! Banco vetorial pronto para RAG.")
    print("Próximo passo: python scripts/05_avaliar_baseline.py")
    print("=" * 60)


if __name__ == "__main__":
    main()
