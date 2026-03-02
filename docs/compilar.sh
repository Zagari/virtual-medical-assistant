#!/bin/zsh
# ============================================================================
# Script de Compilação do Relatório Tech Challenge FIAP - Fase 3
# Sistema: macOS / Linux
# ============================================================================

echo "====================================="
echo "  Compilando Relatório Tech Challenge"
echo "  FIAP - Pós IA para Devs - Fase 3"
echo "====================================="
echo ""

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

DOC_NAME="relatorio_tecnico"

if ! command -v pdflatex &> /dev/null; then
    echo -e "${RED}ERRO: pdflatex não encontrado!${NC}"
    echo ""
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo "  macOS: brew install --cask mactex"
    else
        echo "  Ubuntu/Debian: sudo apt install texlive-full"
    fi
    exit 1
fi

setopt null_glob 2>/dev/null
echo -e "${YELLOW}[1/5] Limpando arquivos temporários...${NC}"
rm -f *.aux *.log *.out *.toc *.lof *.lot *.bcf *.run.xml *.bbl *.blg *.acn *.acr *.alg *.glg *.glo *.gls *.ist *.lol 2>/dev/null
rm -f chapters/*.aux lib/*.aux 2>/dev/null
echo "      Limpeza concluída"
setopt no_null_glob 2>/dev/null

echo -e "${YELLOW}[2/5] Primeira compilação (pdflatex)...${NC}"
pdflatex -interaction=nonstopmode ${DOC_NAME}.tex > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo -e "${RED}      Erro na primeira compilação${NC}"
    echo "      Verifique ${DOC_NAME}.log para detalhes"
    exit 1
fi
echo "      Primeira compilação concluída"

echo -e "${YELLOW}[3/5] Gerando glossário e abreviaturas...${NC}"
if command -v makeglossaries &> /dev/null; then
    makeglossaries ${DOC_NAME} > /dev/null 2>&1
    echo "      Glossário gerado"
else
    echo -e "${YELLOW}      makeglossaries não encontrado (glossário pode ficar vazio)${NC}"
fi

echo -e "${YELLOW}[4/5] Segunda compilação (pdflatex)...${NC}"
pdflatex -interaction=nonstopmode ${DOC_NAME}.tex > /dev/null 2>&1
echo "      Segunda compilação concluída"

echo -e "${YELLOW}[5/5] Terceira compilação final (pdflatex)...${NC}"
pdflatex -interaction=nonstopmode ${DOC_NAME}.tex > /dev/null 2>&1
echo "      Compilação final concluída"

echo ""
echo "====================================="

if [ -f ${DOC_NAME}.pdf ]; then
    echo -e "${GREEN}Compilação concluída com sucesso!${NC}"
    echo -e "${CYAN}Arquivo:${NC} ${DOC_NAME}.pdf"

    if command -v pdfinfo &> /dev/null; then
        PAGES=$(pdfinfo ${DOC_NAME}.pdf 2>/dev/null | grep "Pages:" | awk '{print $2}')
        echo -e "${CYAN}Páginas:${NC} $PAGES"
    fi
    SIZE=$(du -h ${DOC_NAME}.pdf | cut -f1)
    echo -e "${CYAN}Tamanho:${NC} $SIZE"

    if [[ "$OSTYPE" == "darwin"* ]]; then
        open ${DOC_NAME}.pdf
    fi
else
    echo -e "${RED}Erro: PDF não foi gerado!${NC}"
    tail -20 ${DOC_NAME}.log
    exit 1
fi

echo ""
