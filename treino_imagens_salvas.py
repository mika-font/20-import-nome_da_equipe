import cv2
import mediapipe as mp
import os
import csv

mp_hands = mp.solutions.hands

dataset_dir = 'dataset'
saida_csv = 'dados_mao.csv'

with open(saida_csv, 'w', newline='') as f:
    writer = csv.writer(f)
    # Cabeçalho opcional
    header = []
    for i in range(21):
        header += [f'x{i}', f'y{i}', f'z{i}']
    header.append('letra')
    writer.writerow(header)

    with mp_hands.Hands(static_image_mode=True, max_num_hands=1) as hands:
        for letra in os.listdir(dataset_dir):
            pasta_letra = os.path.join(dataset_dir, letra)
            if not os.path.isdir(pasta_letra):
                continue
            for img_nome in os.listdir(pasta_letra):
                img_path = os.path.join(pasta_letra, img_nome)
                img = cv2.imread(img_path)
                if img is None:
                    continue
                img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                results = hands.process(img_rgb)
                if results.multi_hand_landmarks:
                    for hand_landmarks in results.multi_hand_landmarks:
                        # Pega o landmark do pulso (landmark 0)
                        wrist = hand_landmarks.landmark[0]
                        row = []
                        for lm in hand_landmarks.landmark:
                            # Torna relativo ao pulso
                            row += [lm.x - wrist.x, lm.y - wrist.y, lm.z - wrist.z]
                        row.append(letra)
                        writer.writerow(row)