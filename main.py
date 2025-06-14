import cv2
import mediapipe as mp
import multiprocessing as mproc
import numpy as np
import joblib
import tkinter as tk
from tkinter import font, messagebox
from PIL import Image, ImageTk
import sys
import os

# --- Worker Process Functions ---

def prever_letra_com_modelo(model, hand_landmarks):
    try:
        if not hand_landmarks.landmark:
            return "?"
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
        print(f"[Worker] Erro ao extrair features ou prever: {e}", file=sys.stderr)
        return "?"

def mediapipe_worker(jobs_queue, results_queue, model_path):
    print("[Worker] Processo iniciado.")
    model = None
    try:
        print(f"[Worker] Carregando o modelo de ML '{model_path}'...")
        model = joblib.load(model_path)
        print("[Worker] Modelo carregado com sucesso.")
    except FileNotFoundError:
        print(f"[Worker] ERRO CRÍTICO: Arquivo '{model_path}' não encontrado. Encerrando worker.", file=sys.stderr)
        results_queue.put(None)
        return
    except Exception as e:
        print(f"[Worker] ERRO ao carregar o modelo: {e}. Encerrando worker.", file=sys.stderr)
        results_queue.put(None)
        return

    mp_maos = mp.solutions.hands
    hands = mp_maos.Hands(
        static_image_mode=False,
        max_num_hands=1,
        min_detection_confidence=0.7,  # Mais rápido e confiável
        min_tracking_confidence=0.7
    )

    while True:
        image = jobs_queue.get()
        if image is None:
            break

        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = hands.process(image_rgb)

        processed_data = []
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                letter = prever_letra_com_modelo(model, hand_landmarks) if model else "?"
                processed_data.append({"landmarks": hand_landmarks, "letra": letter})

        results_queue.put(processed_data)

    hands.close()
    print("[Worker] Processo finalizado.")

# --- Main Application Class ---

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
        self.root.attributes("-fullscreen", True)

        self.root.update_idletasks()
        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()

        self.video_width = int(self.screen_width * 0.5)
        self.video_height = int(self.screen_height * 0.7)
        self.process_w, self.process_h = 480, 360  # Resolução reduzida para processamento

        self.big_font_size = max(int(self.screen_height * 0.10), 60)
        self.word_font_size = max(int(self.screen_height * 0.04), 24)
        self.button_font_size = max(int(self.screen_height * 0.035), 20)
        self.splash_title_font_size = max(int(self.screen_height * 0.15), 70)
        self.splash_footer_font_size = max(int(self.screen_height * 0.02), 14)

        self.splash_title_font = font.Font(family="Courier", size=self.splash_title_font_size, weight="bold")
        self.splash_footer_font = font.Font(family="Segoe UI", size=self.splash_footer_font_size)
        self.big_font = font.Font(family="Segoe UI", size=self.big_font_size, weight="bold")
        self.word_font = font.Font(family="Segoe UI", size=self.word_font_size)
        self.button_font = font.Font(family="Segoe UI", size=self.button_font_size, weight="bold")

        self.latest_results = []
        self.last_detected_letter = ""
        self.captured_word = ""

        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_hands = mp.solutions.hands

        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            print("ERRO: Não foi possível abrir a câmera. Verifique se ela está conectada e não está em uso.", file=sys.stderr)
            messagebox.showerror("Erro de Câmera", "Não foi possível abrir a câmera. Verifique se ela está conectada e não está em uso.")
            self.root.destroy()
            return

        self._after_id = None

        self._create_splash_screen()
        self._create_main_screen()
        self.splash_frame.pack(fill=tk.BOTH, expand=True)

    def capture_letter(self):
        if self.last_detected_letter and self.last_detected_letter != "?":
            self.captured_word += self.last_detected_letter
            self.word_display.config(text=self.captured_word)

    def clear_word(self):
        self.captured_word = ""
        self.word_display.config(text="")

    def on_closing(self):
        print("[Main] Encerrando aplicação...")
        if self._after_id:
            self.root.after_cancel(self._after_id)
        self.jobs_queue.put(None)
        if self.cap and self.cap.isOpened():
            self.cap.release()
        self.root.destroy()

    def _create_splash_screen(self):
        self.splash_frame = tk.Frame(self.root, bg=self.COLOR_BG)
        center_frame = tk.Frame(self.splash_frame, bg=self.COLOR_BG)
        center_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        tk.Label(center_frame, text="Libr.IA", font=self.splash_title_font, fg=self.COLOR_ACCENT, bg=self.COLOR_BG).pack(pady=20)
        tk.Label(center_frame, text="Sistema de Reconhecimento de Sinais em Libras", font=self.splash_footer_font, fg=self.COLOR_TEXT, bg=self.COLOR_BG).pack(pady=10)

        start_button = tk.Button(
            center_frame, text="INICIAR APLICAÇÃO", command=self._show_main_app,
            font=self.button_font, bg=self.COLOR_ACCENT, fg=self.COLOR_TEXT,
            relief="flat", borderwidth=0, activebackground=self.COLOR_ACCENT_HOVER,
            activeforeground=self.COLOR_TEXT, pady=15, padx=30
        )
        start_button.pack(pady=30)

        tk.Label(self.splash_frame, text="Desenvolvido por import nome_da_equipe", font=self.splash_footer_font, fg=self.COLOR_TEXT, bg=self.COLOR_BG).pack(side=tk.BOTTOM, pady=20)

    def _show_main_app(self):
        self.splash_frame.pack_forget()
        self.main_app_frame.pack(fill=tk.BOTH, expand=True)
        self.update_frame()

    def _create_main_screen(self):
        self.main_app_frame = tk.Frame(self.root, bg=self.COLOR_BG)
        main_layout = tk.Frame(self.main_app_frame, bg=self.COLOR_BG, padx=40, pady=40)
        main_layout.pack(fill=tk.BOTH, expand=True)

        video_frame = tk.Frame(main_layout, bg=self.COLOR_BG)
        video_frame.pack(side=tk.LEFT, padx=(0, 40), pady=20)
        self.video_label = tk.Label(video_frame, bg=self.COLOR_BG, width=self.video_width, height=self.video_height)
        self.video_label.pack()

        control_frame = tk.Frame(main_layout, bg=self.COLOR_BG)
        control_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=40, pady=20)

        tk.Label(control_frame, text="LETRA DETECTADA", font=self.word_font, fg=self.COLOR_TEXT, bg=self.COLOR_BG).pack(pady=(0, 20), anchor="center")
        self.letter_display = tk.Label(control_frame, text="?", font=self.big_font, fg=self.COLOR_ACCENT, bg=self.COLOR_BG)
        self.letter_display.pack(pady=30, anchor="center")

        self.capture_button = tk.Button(
            control_frame, text="CAPTURAR LETRA", command=self.capture_letter,
            font=self.button_font, bg=self.COLOR_ACCENT, fg=self.COLOR_TEXT,
            relief="flat", borderwidth=0, activebackground=self.COLOR_ACCENT_HOVER,
            activeforeground=self.COLOR_TEXT, pady=20
        )
        self.capture_button.pack(pady=40, fill=tk.X)

        tk.Label(control_frame, text="PALAVRA FORMADA", font=self.word_font, fg=self.COLOR_TEXT, bg=self.COLOR_BG).pack(pady=(40, 20), anchor="center")
        self.word_display_frame = tk.Frame(control_frame, bg=self.COLOR_FRAME, relief="solid", borderwidth=2, bd=2)
        self.word_display_frame.pack(fill=tk.BOTH, expand=True)
        self.word_display = tk.Label(
            self.word_display_frame, text="", font=self.word_font, fg=self.COLOR_TEXT,
            bg=self.COLOR_FRAME, wraplength=int(self.screen_width * 0.35), justify="center"
        )
        self.word_display.pack(pady=30, padx=30, fill=tk.BOTH, expand=True)

        self.clear_word_button = tk.Button(
            control_frame, text="LIMPAR PALAVRA", command=self.clear_word,
            font=self.button_font, bg=self.COLOR_ACCENT, fg=self.COLOR_TEXT,
            relief="flat", borderwidth=0, activebackground=self.COLOR_ACCENT_HOVER,
            activeforeground=self.COLOR_TEXT, pady=10
        )
        self.clear_word_button.pack(pady=(10, 0), fill=tk.X)

        self.exit_button = tk.Button(
            control_frame, text="SAIR", command=self.on_closing,
            font=self.button_font, bg="#D32F2F", fg=self.COLOR_TEXT,
            relief="flat", borderwidth=0, activebackground="#E57373",
            activeforeground=self.COLOR_TEXT, pady=10
        )
        self.exit_button.pack(pady=(20, 0), fill=tk.X)

    def update_frame(self):
        if not self.cap.isOpened():
            print("Câmera não está aberta. Encerrando atualização de frame.", file=sys.stderr)
            if self._after_id:
                self.root.after_cancel(self._after_id)
            return

        success, image = self.cap.read()
        if not success:
            print("Não foi possível ler o frame da câmera.", file=sys.stderr)
            self._after_id = self.root.after(30, self.update_frame)
            return

        image = cv2.flip(image, 1)
        # Reduz a resolução para processamento rápido
        small_image = cv2.resize(image, (self.process_w, self.process_h))

        # Só envia se a fila estiver vazia
        if self.jobs_queue.qsize() == 0:
            self.jobs_queue.put(small_image.copy())

        # Processa os resultados do worker
        if not self.results_queue.empty():
            worker_output = self.results_queue.get()
            if worker_output is None:
                messagebox.showerror("Erro Crítico", "O processo de reconhecimento encontrou um erro grave (modelo não encontrado). A aplicação será encerrada.")
                self.on_closing()
                return
            self.latest_results = worker_output

        # Redimensiona para exibição grande
        display_image = cv2.resize(small_image, (self.video_width, self.video_height))

        self.last_detected_letter = "?"
        if self.latest_results:
            for hand_data in self.latest_results:
                self.last_detected_letter = hand_data.get("letra", "?") or "?"
                self.mp_drawing.draw_landmarks(
                    image=display_image,
                    landmark_list=hand_data["landmarks"],
                    connections=self.mp_hands.HAND_CONNECTIONS,
                    landmark_drawing_spec=self.mp_drawing.DrawingSpec(color=(234, 234, 234), thickness=4, circle_radius=8),
                    connection_drawing_spec=self.mp_drawing.DrawingSpec(color=(30, 136, 229), thickness=4)
                )

        self.letter_display.config(text=self.last_detected_letter)

        img_rgb = cv2.cvtColor(display_image, cv2.COLOR_BGR2RGB)
        img_pil = Image.fromarray(img_rgb)
        img_tk = ImageTk.PhotoImage(image=img_pil)

        self.video_label.imgtk = img_tk
        self.video_label.config(image=img_tk)

        self._after_id = self.root.after(30, self.update_frame)

# --- Main Execution Block ---

if __name__ == '__main__':
    mproc.set_start_method('spawn', force=True)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    model_file_name = 'modelo_mao_knn.pkl'
    model_absolute_path = os.path.join(script_dir, model_file_name)

    jobs_queue = mproc.Queue()
    results_queue = mproc.Queue()

    worker_process = mproc.Process(target=mediapipe_worker, args=(jobs_queue, results_queue, model_absolute_path))
    worker_process.start()

    root = tk.Tk()
    app = App(root, jobs_queue, results_queue)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)

    try:
        root.mainloop()
    except KeyboardInterrupt:
        app.on_closing()
    finally:
        worker_process.join(timeout=5)
        if worker_process.is_alive():
            print("[Main] Forçando o encerramento do processo worker.", file=sys.stderr)
            worker_process.terminate()
        print("[Main] Programa finalizado.")