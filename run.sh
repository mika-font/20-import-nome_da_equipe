#!/bin/bash

# Este script automatiza a configuração do ambiente e a execução do programa principal.

# --- Configurações ---
PYTHON_CMD="python3"  # Use "python3" para garantir compatibilidade no Linux
VENV_DIR=".venv"      # Nome do diretório do ambiente virtual
REQ_FILE="requirements.txt"
MAIN_SCRIPT="main.py"

# Cores para o terminal
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # Sem Cor

echo -e "${YELLOW}Iniciando script de configuração e execução...${NC}"

# Passo 1: Verificar e criar o ambiente virtual, se necessário
if [ ! -d "$VENV_DIR" ]; then
    echo "Ambiente virtual '$VENV_DIR' não encontrado. Criando..."
    $PYTHON_CMD -m venv $VENV_DIR
    if [ $? -ne 0 ]; then
        echo "Erro ao criar o ambiente virtual. Verifique se o pacote 'python3-venv' está instalado."
        exit 1
    fi
    echo -e "${GREEN}Ambiente virtual criado com sucesso!${NC}"
else
    echo "Ambiente virtual '$VENV_DIR' já existe."
fi

# Passo 2: Ativar o ambiente virtual
source $VENV_DIR/bin/activate
echo "Ambiente virtual ativado."

# Passo 3: Instalar as dependências do requirements.txt
echo "Instalando dependências..."
$PYTHON_CMD -m pip install -r $REQ_FILE
if [ $? -ne 0 ]; then
    echo "Erro ao instalar as dependências. Verifique o arquivo '$REQ_FILE'."
    exit 1
fi
echo -e "${GREEN}Dependências instaladas com sucesso!${NC}"

# Passo 4: Executar o programa principal
echo -e "${YELLOW}===============================================${NC}"
echo -e "${YELLOW}Iniciando o programa principal: $MAIN_SCRIPT ${NC}"
echo -e "${YELLOW}Pressione 'q' na janela do programa para sair.${NC}"
echo -e "${YELLOW}===============================================${NC}"

$PYTHON_CMD $MAIN_SCRIPT

# O script termina quando o programa Python for fechado.
echo -e "${GREEN}Programa finalizado.${NC}"
