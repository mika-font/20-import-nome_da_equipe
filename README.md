# Import-nome_da_equipe

---

### *Membros da Equipe:* 

* **Evandro Luz Dorneles** - Dataset e Treinamento
* **Franchesco Parnoff Cagliari** - Interface
* **Gabriel Lorenson Schirmer** - Integração Câmera/Interface
* **Kauê Fucherberger Bonfá** - Dataset e Treinamento
* **Mikael Fontoura do Nascimento** - Modelo de Negócios, Organização e Interface

---

### *Tema / Área do problema:*

Inteligência Artificial Aplicada à Interpretação de Libras para Acessibilidade e Inclusão.

---

### *Solução:*

**Libr.IA** é uma aplicação desktop integrada à IA para leitura e interpretação de linguagem de sinais, traduzindo em tempo real os gestos da Libras utilizando a câmera do computador e imprimindo o texto na tela da interface.

---

### *Tecnologias:*

* **Python** — Linguagem principal para desenvolvimento dos algoritmos de IA, processamento de vídeo e lógica da aplicação.
* **TensorFlow / Keras** — Frameworks para construção, treinamento e inferência de modelos de Machine Learning/Deep Learning.
* **OpenCV (cv2)** — Manipulação de imagens e vídeo, acesso à câmera e pré-processamento de frames.
* **Tkinter / PIL** — Interface gráfica simples e funcional.
* **NumPy** — Operações numéricas de alta performance.
* **Scikit-learn** — Aprendizado de máquina.

---

### **Instruções de Instalação:** 

Para instalar o programa no computador é necessário seguir as seguintes etapas:

**Ambiente Linux**

1. Acesse o terminal e atualize os pacotes do Linux:

```bash
sudo apt upgrade
sudo apt update
```

2. Instale os pacotes do python:

```bash
sudo apt install python3-pip python3-venv
```

3. Clone o repositório e acesse a pasta do projeto:
    ```bash
    git clone https://github.com/mika-font/20-import-nome_da_equipe.git
    cd 20-import-nome_da_equipe
    ```

4. **Execute o programa:**
    ```bash
    ./atualizar_dataset.sh # criar os dois arquivos do modelo da mão (só precisa abrir uma vez)
    ```

5. **Após isso, execute o programa:**
    ```bash
    ./run.sh
    ```

**Ambiente Windows 11**

1. Instale o Python:
    - Baixe e instale pelo site oficial: https://www.python.org/downloads/
    - Ou pelo terminal (PowerShell):
        ```powershell
        winget install Python.Python.3
        ```

2. Clone o repositório e acesse a pasta do projeto:
    ```powershell
    git clone https://github.com/mika-font/20-import-nome_da_equipe.git
    cd 20-import-nome_da_equipe
    ```

3. Crie e ative um ambiente virtual:
    ```powershell
    python -m venv venv
    .\venv\Scripts\activate
    ```

4. Instale as dependências:
    ```powershell
    pip install -r requirements.txt
    ```
    > Caso não exista o arquivo `requirements.txt`, instale manualmente:
    ```powershell
    pip install tensorflow opencv-python mediapipe numpy scikit-learn pillow
    ```

5. Execute o programa:
    ```powershell
    python main.py
    ```

---
