#!/bin/bash

# Este script automatiza a configuração do ambiente e a execução do programa principal.
# Versão avançada: Tenta instalar dependências de sistema automaticamente com permissão do usuário.

# --- Configurações ---
PYTHON_CMD="python3"
VENV_DIR=".venv"
REQ_FILE="requirements.txt"
MAIN_SCRIPT="predicao.py"

# Cores para o terminal
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # Sem Cor

echo -e "${YELLOW}Iniciando script de configuração e execução...${NC}"

# Passo 1: Ambiente virtual
if [ ! -d "$VENV_DIR" ]; then
    echo "Ambiente virtual '$VENV_DIR' não encontrado. Criando..."
    $PYTHON_CMD -m venv $VENV_DIR
    if [ $? -ne 0 ]; then
        echo -e "${RED}Erro ao criar o ambiente virtual. Verifique se 'python3-venv' está instalado.${NC}"
        exit 1
    fi
    echo -e "${GREEN}Ambiente virtual criado com sucesso!${NC}"
else
    echo "Ambiente virtual '$VENV_DIR' já existe."
fi

# Passo 2: Ativar ambiente virtual
source $VENV_DIR/bin/activate
echo "Ambiente virtual ativado."

# Passo 3: Verificar e instalar dependências de sistema (tkinter)
echo "Verificando a dependência do sistema: tkinter..."
$PYTHON_CMD -c "import tkinter" &> /dev/null
if [ $? -ne 0 ]; then
    echo -e "${YELLOW}AVISO: O módulo 'tkinter' não foi encontrado.${NC}"
    
    INSTALL_CMD=""
    # Detecta o gerenciador de pacotes do sistema
    if command -v apt-get &> /dev/null; then
        INSTALL_CMD="sudo apt-get install -y python3-tk"
    elif command -v dnf &> /dev/null; then
        INSTALL_CMD="sudo dnf install -y python3-tkinter"
    else
        echo -e "${RED}Não foi possível detectar o gerenciador de pacotes (apt, dnf).${NC}"
        echo "Por favor, instale 'python3-tk' ou 'python3-tkinter' manualmente e execute o script novamente."
        exit 1
    fi

    echo "Esta aplicação precisa do tkinter, que pode ser instalado com o seguinte comando:"
    echo -e "  ${GREEN}$INSTALL_CMD${NC}"
    
    # Pede permissão ao usuário para executar o comando
    read -p "Deseja que o script tente executar este comando para você? (s/n) " choice
    case "$choice" in 
      s|S|sim|Sim ) 
        echo "Tentando instalar o tkinter. Você pode precisar digitar sua senha de administrador..."
        # Executa o comando de instalação
        $INSTALL_CMD
        if [ $? -ne 0 ]; then
            echo -e "${RED}A instalação automática falhou. Por favor, tente executar o comando acima em seu terminal manualmente.${NC}"
            exit 1
        fi
        echo -e "${GREEN}Tkinter instalado com sucesso!${NC}"
        ;;
      * )
        echo "Instalação cancelada. Por favor, instale o tkinter manualmente e execute o script novamente."
        exit 1
        ;;
    esac
else
    echo -e "${GREEN}Tkinter já está instalado.${NC}"
fi

# Passo 4: Instalar dependências do Python
echo "Instalando dependências de '$REQ_FILE'..."
$PYTHON_CMD -m pip install -r $REQ_FILE
if [ $? -ne 0 ]; then
    echo -e "${RED}Erro ao instalar as dependências de Python.${NC}"
    exit 1
fi
echo -e "${GREEN}Dependências de Python instaladas com sucesso!${NC}"

# Passo 5: Executar o programa principal
echo -e "${YELLOW}===============================================${NC}"
# ### ALTERAÇÃO ###: A mensagem agora usa a variável correta para ser consistente.
echo -e "${YELLOW}Iniciando o programa principal: $MAIN_SCRIPT${NC}"
echo -e "${YELLOW}Pressione a tecla de fechar na janela do programa para sair.${NC}"
echo -e "${YELLOW}===============================================${NC}"

# ### ALTERAÇÃO PRINCIPAL ###: Agora executa o script definido na variável MAIN_SCRIPT.
$PYTHON_CMD $MAIN_SCRIPT

echo -e "${GREEN}Programa finalizado.${NC}"
