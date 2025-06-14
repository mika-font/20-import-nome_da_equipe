import cv2
import mediapipe as mp
import multiprocessing as mproc
import numpy as np

#======================================================================
# FUNÇÃO DE DETECÇÃO (CORRIGIDA E MAIS ROBUSTA)
#======================================================================
def detectar_letra(hand_landmarks):
    lm = hand_landmarks.landmark

    def get_x(i): return lm[i].x
    def get_y(i): return lm[i].y
    def dist_x(a, b): return abs(get_x(a) - get_x(b))
    def dist_y(a, b): return abs(get_y(a) - get_y(b))

    # Estados dos dedos
    thumb_up    = get_y(mp.solutions.hands.HandLandmark.THUMB_TIP) < get_y(mp.solutions.hands.HandLandmark.THUMB_IP)
    index_up    = get_y(mp.solutions.hands.HandLandmark.INDEX_FINGER_TIP) < get_y(mp.solutions.hands.HandLandmark.INDEX_FINGER_PIP)
    middle_up   = get_y(mp.solutions.hands.HandLandmark.MIDDLE_FINGER_TIP) < get_y(mp.solutions.hands.HandLandmark.MIDDLE_FINGER_PIP)
    ring_up     = get_y(mp.solutions.hands.HandLandmark.RING_FINGER_TIP) < get_y(mp.solutions.hands.HandLandmark.RING_FINGER_PIP)
    pinky_up    = get_y(mp.solutions.hands.HandLandmark.PINKY_TIP) < get_y(mp.solutions.hands.HandLandmark.PINKY_PIP)

    #==============================
    # LETRA A: todos os dedos fechados, polegar ao lado (punho fechado)
    #==============================
    dedos_baixados = not index_up and not middle_up and not ring_up and not pinky_up

    # Polegar ao lado do indicador (em X), e na altura do MCP do indicador (em Y)
    thumb_lado_x = dist_x(mp.solutions.hands.HandLandmark.THUMB_TIP, mp.solutions.hands.HandLandmark.INDEX_FINGER_MCP) < 0.09
    thumb_lado_y = abs(get_y(mp.solutions.hands.HandLandmark.THUMB_TIP) - get_y(mp.solutions.hands.HandLandmark.INDEX_FINGER_MCP)) < 0.07

    # O polegar não pode estar abaixo do centro da palma (para não confundir com B)
    thumb_nao_abaixo = get_y(mp.solutions.hands.HandLandmark.THUMB_TIP) < get_y(mp.solutions.hands.HandLandmark.MIDDLE_FINGER_MCP)

    if dedos_baixados and thumb_lado_x and thumb_lado_y and thumb_nao_abaixo:
        return 'A'

    #==============================
    # LETRA B: 4 dedos levantados e juntos, polegar dobrado sobre a palma
    #==============================
    dedos_levantados = index_up and middle_up and ring_up and pinky_up

    polegar_abaixo = get_y(mp.solutions.hands.HandLandmark.THUMB_TIP) > get_y(mp.solutions.hands.HandLandmark.MIDDLE_FINGER_MCP)
    polegar_proximo_palma = dist_x(mp.solutions.hands.HandLandmark.THUMB_TIP, mp.solutions.hands.HandLandmark.MIDDLE_FINGER_MCP) < 0.13

    dedos = [
        mp.solutions.hands.HandLandmark.INDEX_FINGER_TIP,
        mp.solutions.hands.HandLandmark.MIDDLE_FINGER_TIP,
        mp.solutions.hands.HandLandmark.RING_FINGER_TIP,
        mp.solutions.hands.HandLandmark.PINKY_TIP
    ]
    alinhados_y = all(dist_y(dedos[i], dedos[i + 1]) < 0.09 for i in range(3))
    proximos_x = all(dist_x(dedos[i], dedos[i + 1]) < 0.13 for i in range(3))

    if dedos_levantados and polegar_abaixo and polegar_proximo_palma and alinhados_y and proximos_x:
        return 'B'

    #==============================
    # LETRA V: apenas indicador e médio levantados, bem separados
    #==============================
    v_forma = index_up and middle_up and not ring_up and not pinky_up and not thumb_up

    dist_v = dist_x(mp.solutions.hands.HandLandmark.INDEX_FINGER_TIP,
                    mp.solutions.hands.HandLandmark.MIDDLE_FINGER_TIP)

    # Aumenta o threshold para garantir separação clara
    if v_forma and dist_v > 0.13:
        return 'V'

    return None


#======================================================================
# PROCESSO TRABALHADOR (COM REDE DE SEGURANÇA TRY/EXCEPT)
#======================================================================
def mediapipe_worker(jobs_queue, results_queue):
    print("[Worker] Processo iniciado.")
    mp_maos = mp.solutions.hands
    maos = mp_maos.Hands(static_image_mode=False, max_num_hands=1, min_detection_confidence=0.7, min_tracking_confidence=0.5)

    while True:
        imagem = jobs_queue.get()
        if imagem is None:
            break

        altura, largura, _ = imagem.shape
        imagem_rgb = cv2.cvtColor(imagem, cv2.COLOR_BGR2RGB)
        resultados = maos.process(imagem_rgb)

        dados_resultado = []
        if resultados.multi_hand_landmarks:
            for hand_landmarks in resultados.multi_hand_landmarks:
                letra = None
                # ADIÇÃO DE ROBUSTEZ: Se a detecção falhar, o programa não quebra
                try:
                    letra = detectar_letra(hand_landmarks)
                except Exception as e:
                    print(f"[Worker] Erro na função de detecção: {e}")

                coords_de_uma_mao = []
                for lm in hand_landmarks.landmark:
                    px, py = int(lm.x * largura), int(lm.y * altura)
                    coords_de_uma_mao.append((px, py))

                dados_resultado.append({"coords": coords_de_uma_mao, "letra": letra})

        results_queue.put(dados_resultado)

    maos.close()
    print("[Worker] Processo finalizado.")

#======================================================================
# PROCESSO PRINCIPAL (SEM ALTERAÇÕES NECESSÁRIAS AQUI)
#======================================================================
if __name__ == '__main__':
    mproc.set_start_method('spawn', force=True)

    jobs_queue = mproc.Queue()
    results_queue = mproc.Queue()

    worker_process = mproc.Process(target=mediapipe_worker, args=(jobs_queue, results_queue))
    worker_process.start()

    print("[Main] Processo principal iniciado.")
    mp_maos = mp.solutions.hands
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("[Main] Erro: Câmera não pôde ser aberta.")
        jobs_queue.put(None)
        worker_process.join()
        exit()

    latest_results = []
    while True:
        sucesso, imagem = cap.read()
        if not sucesso:
            break

        imagem = cv2.flip(imagem, 1)

        if jobs_queue.qsize() < 1:
            jobs_queue.put(imagem)

        if not results_queue.empty():
            latest_results = results_queue.get()

        if latest_results:
            for hand_data in latest_results:
                hand_in_pixels = hand_data["coords"]
                letra_detectada = hand_data["letra"]

                for connection in mp_maos.HAND_CONNECTIONS:
                    start_idx, end_idx = connection
                    if start_idx < len(hand_in_pixels) and end_idx < len(hand_in_pixels):
                        cv2.line(imagem, hand_in_pixels[start_idx], hand_in_pixels[end_idx], (0, 0, 255), 2)
                for landmark_pixel in hand_in_pixels:
                    cv2.circle(imagem, landmark_pixel, 4, (0, 255, 0), -1)
                
                if letra_detectada:
                    # Posiciona o texto acima do pulso
                    pulso_pos_x, pulso_pos_y = hand_in_pixels[0]
                    cv2.putText(imagem, letra_detectada, (pulso_pos_x - 30, pulso_pos_y - 40), 
                                cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 0, 0), 3, cv2.LINE_AA)

        cv2.imshow('Visualizador - Projeto Libras', imagem)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    print("[Main] Encerrando...")
    jobs_queue.put(None)
    worker_process.join()
    cap.release()
    cv2.destroyAllWindows()
    print("[Main] Programa finalizado.")