import cv2
import mediapipe as mp
import multiprocessing as mproc
import time
import numpy as np

#======================================================================
# PROCESSO TRABALHADOR (NÃO PRECISA DE MUDANÇAS)
#======================================================================
def mediapipe_worker(jobs_queue, results_queue):
    print("[Worker] Processo iniciado.")
    
    mp_maos = mp.solutions.hands
    maos = mp_maos.Hands(static_image_mode=False,
                           max_num_hands=1, 
                           min_detection_confidence=0.7, 
                           min_tracking_confidence=0.5)

    while True:
        imagem = jobs_queue.get()
        if imagem is None:
            break
            
        altura, largura, _ = imagem.shape
        imagem_rgb = cv2.cvtColor(imagem, cv2.COLOR_BGR2RGB)
        resultados = maos.process(imagem_rgb)

        all_hands_pixel_coords = []
        if resultados.multi_hand_landmarks:
            for hand_landmarks in resultados.multi_hand_landmarks:
                coords_de_uma_mao = []
                for lm in hand_landmarks.landmark:
                    px = int(lm.x * largura)
                    py = int(lm.y * altura)
                    coords_de_uma_mao.append((px, py))
                all_hands_pixel_coords.append(coords_de_uma_mao)
        
        results_queue.put(all_hands_pixel_coords)
            
    maos.close()
    print("[Worker] Processo finalizado.")


#======================================================================
# PROCESSO PRINCIPAL (VISUALIZADOR E GERENCIADOR)
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

    latest_hand_coords = []
    
    while True:
        sucesso, imagem = cap.read()
        if not sucesso:
            break
        
        # <<-- CORREÇÃO AQUI -->>
        # 1. VIRA A IMAGEM PRIMEIRO
        imagem = cv2.flip(imagem, 1)

        # 2. Envia a imagem JÁ VIRADA para o trabalhador
        if jobs_queue.qsize() < 1:
            jobs_queue.put(imagem)

        if not results_queue.empty():
            latest_hand_coords = results_queue.get()
        
        # Agora as coordenadas recebidas já correspondem à imagem virada
        if latest_hand_coords:
            for hand_in_pixels in latest_hand_coords:
                # Desenha o esqueleto
                for connection in mp_maos.HAND_CONNECTIONS:
                    start_idx, end_idx = connection
                    if start_idx < len(hand_in_pixels) and end_idx < len(hand_in_pixels):
                        cv2.line(imagem, hand_in_pixels[start_idx], hand_in_pixels[end_idx], (0, 0, 255), 2)
                for landmark_pixel in hand_in_pixels:
                    cv2.circle(imagem, landmark_pixel, 4, (0, 255, 0), -1)

                # Desenha o contorno e o círculo envolvente
                if len(hand_in_pixels) > 2:
                    pontos_np = np.array(hand_in_pixels, dtype=np.int32)
                    casco_convexo = cv2.convexHull(pontos_np)
                    cv2.drawContours(imagem, [casco_convexo], 0, (255, 255, 0), 2)

                    (x, y), raio = cv2.minEnclosingCircle(casco_convexo)
                    cv2.circle(imagem, (int(x), int(y)), int(raio), (0, 255, 255), 2)

        cv2.imshow('Visualizador - Projeto Libras', imagem)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Encerramento limpo
    print("[Main] Encerrando...")
    jobs_queue.put(None)
    worker_process.join() 
    cap.release()
    cv2.destroyAllWindows()
    print("[Main] Programa finalizado.")