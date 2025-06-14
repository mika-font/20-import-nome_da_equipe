import cv2
import mediapipe as mp
import multiprocessing as mproc
import numpy as np
import joblib
import tkinter as tk
from tkinter import font
from PIL import Image, ImageTk

def prever_letra_com_modelo(model, hand_landmarks):
    """
    Extrai as características da mão e usa o modelo KNN para prever a letra.
    """
    try:
        wrist = hand_landmarks.landmark[0]
        features = []
        for lm in hand_landmarks.landmark:
            features.extend([lm.x - wrist.x, lm.y - wrist.y, lm.z - wrist.z])

        if len(features) == 63:
            prediction = model.predict([features])
            return prediction[0]
        else:
            return "?"
    except Exception as e:
        print(f"[Worker] Erro ao extrair features ou prever: {e}")
        return "?"

def mediapipe_worker(jobs_queue, results_queue):
    print("[Worker] Processo iniciado.")
    
    try:
        print("[Worker] Carregando o modelo de ML 'modelo_mao_knn.pkl'...")
        model = joblib.load('modelo_mao_knn.pkl')
        print("[Worker] Modelo carregado com sucesso.")
    except FileNotFoundError:
        print("[Worker] ERRO CRÍTICO: Arquivo 'modelo_mao_knn.pkl' não encontrado.")
        results_queue.put([]) # Envia lista vazia em caso de erro
        return

    mp_maos = mp.solutions.hands
    maos = mp_maos.Hands(
        static_image_mode=False, 
        max_num_hands=1, 
        min_detection_confidence=0.7, 
        min_tracking_confidence=0.5
    )

    while True:
        imagem = jobs_queue.get()
        if imagem is None:
            break

        imagem_rgb = cv2.cvtColor(imagem, cv2.COLOR_BGR2RGB)
        resultados = maos.process(imagem_rgb)

        dados_resultado = []
        if resultados.multi_hand_landmarks:
            for hand_landmarks in resultados.multi_hand_landmarks:
                letra = prever_letra_com_modelo(model, hand_landmarks)
                
                # ### CORREÇÃO 1 ###
                # Agora enviamos o objeto 'hand_landmarks' original, que a função de desenho precisa.
                # Não precisamos mais das coordenadas em pixels ('coords'), pois a função de desenho cuida disso.
                dados_resultado.append({"landmarks": hand_landmarks, "letra": letra})
        
        # Envia os dados para a fila. Se nenhuma mão for detectada, envia uma lista vazia.
        results_queue.put(dados_resultado)

    maos.close()
    print("[Worker] Processo finalizado.")

class App:
    def __init__(self, root, jobs_queue, results_queue):
        self.root = root
        self.jobs_queue = jobs_queue
        self.results_queue = results_queue

        self.COLOR_BG = "#212121"
        self.COLOR_FRAME = "#2E2E2E"
        self.COLOR_TEXT = "#EAEAEA"
        self.COLOR_ACCENT = "#1E88E5"
        self.COLOR_ACCENT_HOVER = "#42A5F5"

        self.root.title("Libr.IA")
        self.root.configure(background=self.COLOR_BG)
        self.root.minsize(900, 550)

        self.splash_title_font = font.Font(family="Courier", size=80, weight="bold")
        self.splash_footer_font = font.Font(family="Segoe UI", size=9)
        self.big_font = font.Font(family="Segoe UI", size=48, weight="bold")
        self.word_font = font.Font(family="Segoe UI", size=14)
        self.button_font = font.Font(family="Segoe UI", size=12, weight="bold")

        self.latest_results = []
        self.last_detected_letter = ""
        self.captured_word = ""

        self.mp_maos = mp.solutions.hands
        # Verifica se a câmera abre corretamente
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            print("ERRO: Não foi possível abrir a câmera.")
            self.root.destroy()
            return

        self._criar_tela_principal()
        self._criar_tela_splash()

        self.splash_frame.pack(fill=tk.BOTH, expand=True)

    def _criar_tela_splash(self):
        self.splash_frame = tk.Frame(self.root, bg=self.COLOR_BG)
        title_label = tk.Label(self.splash_frame, text="Libr.IA", font=self.splash_title_font, fg=self.COLOR_ACCENT, bg=self.COLOR_BG)
        title_label.pack(side=tk.TOP, pady=(100, 0))
        start_button = tk.Button(
            self.splash_frame, text="INICIAR", command=self.iniciar_app,
            font=self.button_font, bg=self.COLOR_ACCENT, fg=self.COLOR_TEXT,
            relief="flat", borderwidth=0, activebackground=self.COLOR_ACCENT_HOVER,
            activeforeground=self.COLOR_TEXT, padx=30, pady=10
        )
        start_button.pack(expand=True)
        footer_label = tk.Label(self.splash_frame, text="import nome_do_time", font=self.splash_footer_font, fg=self.COLOR_TEXT, bg=self.COLOR_BG)
        footer_label.pack(side=tk.BOTTOM, pady=20)

    def _criar_tela_principal(self):
        self.main_app_frame = tk.Frame(self.root, bg=self.COLOR_BG)
        main_layout = tk.Frame(self.main_app_frame, bg=self.COLOR_BG, padx=20, pady=20)
        main_layout.pack(fill=tk.BOTH, expand=True)

        video_frame = tk.Frame(main_layout, bg=self.COLOR_BG)
        video_frame.pack(side=tk.LEFT, padx=(0, 20))
        self.video_label = tk.Label(video_frame, bg=self.COLOR_BG)
        self.video_label.pack()

        control_frame = tk.Frame(main_layout, bg=self.COLOR_BG)
        control_frame.pack(side=tk.RIGHT, fill=tk.Y, expand=True)

        tk.Label(control_frame, text="LETRA DETECTADA", font=self.word_font, fg=self.COLOR_TEXT, bg=self.COLOR_BG).pack(pady=(0, 5), anchor="center")
        self.letter_display = tk.Label(control_frame, text="?", font=self.big_font, fg=self.COLOR_ACCENT, bg=self.COLOR_BG)
        self.letter_display.pack(pady=10, anchor="center")
        
        self.capture_button = tk.Button(control_frame, text="CAPTURAR LETRA", command=self.capture_letter, font=self.button_font, bg=self.COLOR_ACCENT, fg=self.COLOR_TEXT, relief="flat", borderwidth=0, activebackground=self.COLOR_ACCENT_HOVER, activeforeground=self.COLOR_TEXT, pady=10)
        self.capture_button.pack(pady=20, fill=tk.X)

        tk.Label(control_frame, text="PALAVRA FORMADA", font=self.word_font, fg=self.COLOR_TEXT, bg=self.COLOR_BG).pack(pady=(20, 5), anchor="center")
        self.word_display_frame = tk.Frame(control_frame, bg=self.COLOR_FRAME, relief="solid", borderwidth=1, bd=1)
        self.word_display_frame.pack(fill=tk.BOTH, expand=True)
        self.word_display = tk.Label(self.word_display_frame, text="", font=self.word_font, fg=self.COLOR_TEXT, bg=self.COLOR_FRAME, wraplength=180, justify="center")
        self.word_display.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

    def iniciar_app(self):
        self.splash_frame.pack_forget()
        self.main_app_frame.pack(fill=tk.BOTH, expand=True)
        self.update_frame()

    def capture_letter(self):
        if self.last_detected_letter and self.last_detected_letter not in ["?", "ERRO"]:
            self.captured_word += self.last_detected_letter
            self.word_display.config(text=self.captured_word)

    def update_frame(self):
        sucesso, imagem = self.cap.read()
        if not sucesso:
            self.root.after(15, self.update_frame)
            return

        imagem = cv2.flip(imagem, 1)

        if self.jobs_queue.qsize() < 1:
            self.jobs_queue.put(imagem.copy())

        if not self.results_queue.empty():
            self.latest_results = self.results_queue.get()

        self.last_detected_letter = "?"
        if self.latest_results:
            # ### CORREÇÃO 2 ###
            # Simplificamos todo o bloco de desenho.
            # Agora iteramos sobre os resultados e usamos o objeto "landmarks" diretamente.
            for hand_data in self.latest_results:
                self.last_detected_letter = hand_data["letra"] or "?"
                
                # A função de desenho do MediaPipe é a forma mais limpa de fazer isso.
                mp.solutions.drawing_utils.draw_landmarks(
                    image=imagem,
                    landmark_list=hand_data["landmarks"], # Usando o objeto correto
                    connections=self.mp_maos.HAND_CONNECTIONS,
                    landmark_drawing_spec=mp.solutions.drawing_utils.DrawingSpec(color=(234, 234, 234), thickness=2, circle_radius=4),
                    connection_drawing_spec=mp.solutions.drawing_utils.DrawingSpec(color=(30, 136, 229), thickness=2)
                )

        self.letter_display.config(text=self.last_detected_letter)

        img_rgb = cv2.cvtColor(imagem, cv2.COLOR_BGR2RGB)
        img_pil = Image.fromarray(img_rgb)
        img_tk = ImageTk.PhotoImage(image=img_pil)

        self.video_label.imgtk = img_tk
        self.video_label.config(image=img_tk)

        self.root.after(15, self.update_frame)

    def on_closing(self):
        print("[Main] Encerrando...")
        self.jobs_queue.put(None)
        if self.cap.isOpened(): self.cap.release()
        self.root.destroy()

if __name__ == '__main__':
    mproc.set_start_method('spawn', force=True)
    
    jobs_queue = mproc.Queue()
    results_queue = mproc.Queue()
    
    worker_process = mproc.Process(target=mediapipe_worker, args=(jobs_queue, results_queue))
    worker_process.start()

    root = tk.Tk()
    app = App(root, jobs_queue, results_queue)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()

    worker_process.join()
    print("[Main] Programa finalizado.")