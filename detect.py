# detect.py

import os
import glob
import shutil
from ultralytics import YOLO
import time
from utils import TAMOGATOTT_KITERJESZTESEK

class PredictKonyvtarNemTalalhatoError(Exception):
    pass

def predict_konyvtarak_kezeles(base_dir='runs/detect', max_dirs=5, logger=None):
    predict_dirs = sorted(glob.glob(os.path.join(base_dir, 'predict*')), key=os.path.getctime)
    if len(predict_dirs) > max_dirs:
        for old_dir in predict_dirs[:-max_dirs]:
            shutil.rmtree(old_dir, ignore_errors=True)
            if logger:
                logger.info(f"Régi predict könyvtár törölve: {old_dir}")

def legfrissebb_predict_konyvtar(base_dir='runs/detect'):
    predict_dirs = glob.glob(os.path.join(base_dir, 'predict*'))
    if not predict_dirs:
        raise PredictKonyvtarNemTalalhatoError("Nem található 'predict' könyvtár.")
    return max(predict_dirs, key=os.path.getctime)

def ermék_észlelése(bemeneti_konyvtar, detect_model, batch_meret, logger=None):
    start_time = time.time()
    try:
        detect_model.predict(
            bemeneti_konyvtar,
            save=True, save_txt=True,
            show_labels=False, show_conf=False,
            stream=False, verbose=False,
            batch=batch_meret
        )
        label_folder = os.path.join(legfrissebb_predict_konyvtar(), 'labels')
        if logger:
            logger.info(f"Érmék észlelése {time.time() - start_time:.2f} mp alatt kész.")
        return label_folder
    except Exception as e:
        if logger: logger.error(f"Hiba észlelés közben: {e}")
        raise
