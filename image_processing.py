# image_processing.py

import os
import cv2
import time
from multiprocessing import Pool
from tqdm import tqdm
from utils import TAMOGATOTT_KITERJESZTESEK

def egy_kep_feldolgozasa(args):
    kep_fajl, bemenet, label_konyvtar, kimenet, clahe_clip, blur_meret, logger = args
    try:
        kep_ut = os.path.join(bemenet, kep_fajl)
        label_ut = os.path.join(label_konyvtar, kep_fajl.rsplit('.', 1)[0] + '.txt')

        if not os.path.exists(label_ut):
            return

        kep = cv2.imread(kep_ut)
        if kep is None:
            logger.warning(f"Nem sikerült betölteni a képet: {kep_ut}")
            return

        h, w = kep.shape[:2]
        with open(label_ut, "r") as f:
            sorok = f.readlines()

        for i, sor in enumerate(sorok):
            try:
                _, x, y, bw, bh = map(float, sor.split())
                x1, y1 = max(0, int((x - bw/2) * w)), max(0, int((y - bh/2) * h))
                x2, y2 = min(w, int((x + bw/2) * w)), min(h, int((y + bh/2) * h))
                if x1 >= x2 or y1 >= y2:
                    continue

                roi = kep[y1:y2, x1:x2]
                hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
                clahe = cv2.createCLAHE(clipLimit=clahe_clip, tileGridSize=(8, 8))
                hsv[:, :, 2] = clahe.apply(hsv[:, :, 2])
                feldolgozott = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
                feldolgozott = cv2.GaussianBlur(feldolgozott, blur_meret, 0)

                fajlnev = f"feldolgozott_erme_{kep_fajl.rsplit('.', 1)[0]}_{i}.jpg"
                cv2.imwrite(os.path.join(kimenet, fajlnev), feldolgozott)
            except Exception as e:
                logger.error(f"Részfeldolgozás hiba: {e}")
                continue
    except Exception as e:
        logger.error(f"{kep_fajl} feldolgozása közben: {e}")

def ermék_kivágása_és_előfeldolgozása(bemenet, labels, kimenet, clahe_clip=2.0, blur_meret=(5, 5), num_workers=4, logger=None):
    start_time = time.time()
    os.makedirs(kimenet, exist_ok=True)

    kepek = [f for f in os.listdir(bemenet) if any(f.lower().endswith(ext) for ext in TAMOGATOTT_KITERJESZTESEK)]
    args_list = [(f, bemenet, labels, kimenet, clahe_clip, blur_meret, logger) for f in kepek]

    with Pool(num_workers) as pool:
        list(tqdm(pool.imap(egy_kep_feldolgozasa, args_list), total=len(args_list), desc="Képfeldolgozás"))

    if logger:
        logger.info(f"Kivágás + előfeldolgozás: {time.time() - start_time:.2f} mp")
