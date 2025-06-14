#!/bin/bash

# Este script automatiza a extração de dados e o treinamento do modelo de ML.

# --- Configurações ---
PYTHON_CMD="python3"
VENV_DIR=".venv"
REQ_FILE="requirements.txt"
SCRIPT_EXTRACAO="treino_imagens_salvas.py"
SCRIPT_TREINAMENTO="treinamento.py"

# Cores para o terminal
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # Sem Cor

echo -e "${YELLOW}Iniciando o script de preparação e treinamento...${NC}"

# --- Passo 1: Configuração do Ambiente Virtual ---
echo -e "\n${GREEN}--- Configurando Ambiente Virtual ---${NC}"
if [ ! -d "$VENV_DIR" ]; then
    echo "Ambiente virtual '$VENV_DIR' não encontrado. Criando..."
    $PYTHON_CMD -m venv $VENV_DIR
    if [ $? -ne 0 ]; then
        echo -e "${RED}Erro ao criar o ambiente virtual. Verifique se 'python3-venv' está instalado.${NC}"
        exit 1
    fi
    echo "Ambiente virtual criado com sucesso."
else
    echo "Ambiente virtual '$VENV_DIR' já existe."
fi

# Ativa o ambiente virtual
source $VENV_DIR/bin/activate
echo "Ambiente virtual ativado."

# --- Passo 2: Instalação das Dependências ---
echo -e "\n${GREEN}--- Instalando Dependências de Python ---${NC}"
$PYTHON_CMD -m pip install -r $REQ_FILE
if [ $? -ne 0 ]; then
    echo -e "${RED}Erro ao instalar as dependências de '$REQ_FILE'. Verifique o arquivo e sua conexão.${NC}"
    exit 1
fi
echo "Dependências instaladas com sucesso."

# --- Passo 3: Execução dos Scripts ---
echo -e "\n${GREEN}--- Iniciando Processo de Treinamento ---${NC}"

# Executa o primeiro script para extrair os dados das imagens
echo -e "\n${YELLOW}==> Etapa 1/2: Executando '$SCRIPT_EXTRACAO' para gerar 'dados_mao.csv'...${NC}"
$PYTHON_CMD $SCRIPT_EXTRACAO
if [ $? -ne 0 ]; then
    echo -e "${RED}Erro ao executar o script de extração de dados. O processo será interrompido.${NC}"
    exit 1
fi
echo "Extração de dados concluída."

# Executa o segundo script para treinar o modelo
echo -e "\n${YELLOW}==> Etapa 2/2: Executando '$SCRIPT_TREINAMENTO' para gerar 'modelo_mao_knn.pkl'...${NC}"
$PYTHON_CMD $SCRIPT_TREINAMENTO
if [ $? -ne 0 ]; then
    echo -e "${RED}Erro ao executar o script de treinamento.${NC}"
    exit 1
fi

# --- Conclusão ---
echo -e "\n${GREEN}=====================================================${NC}"
echo -e "${GREEN}PROCESSO FINALIZADO COM SUCESSO!${NC}"
echo "O arquivo de dados ${YELLOW}dados_mao.csv${NC} foi gerado."
echo "O modelo treinado foi salvo como ${YELLOW}modelo_mao_knn.pkl${NC}."
echo -e "${GREEN}=====================================================${NC}"

# Opcional: Desativar o ambiente virtual no final
deactivate
