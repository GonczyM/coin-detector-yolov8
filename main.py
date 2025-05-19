# main.py

import yaml
import time
from ultralytics import YOLO
from logger_config import setup_logger
from utils import konyvtarak_beallitasa
from detect import ermék_észlelése, predict_konyvtarak_kezeles
from image_processing import ermék_kivágása_és_előfeldolgozása
from classify import ermék_osztályozása, érték_kiszámítása_és_rendezés
from riport_generator import riport_mentese

def main(config_path='config.yaml'):
    logger = setup_logger()
    teljes_start = time.time()

    # 1. Konfiguráció betöltés
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
    except FileNotFoundError:
        logger.error(f"A konfigurációs fájl nem található: {config_path}")
        return None

    # 2. Modellek betöltése
    try:
        detect_model = YOLO(config['detect_model_eleresi_ut'])
        classify_model = YOLO(config['classify_model_eleresi_ut'])
    except Exception as e:
        logger.error(f"Hiba a YOLO modellek betöltésekor: {e}")
        return None

    # 3. Könyvtárak beállítása
    try:
        bemenet, kivagott, osztalyozott = konyvtarak_beallitasa(config)
    except Exception as e:
        logger.error(str(e))
        return None

    # 4. Érmék detektálása
    try:
        t0 = time.time()
        label_konyvtar = ermék_észlelése(bemenet, detect_model, config['batch_meret'], logger=logger)
        ido_detect = time.time() - t0
    except Exception as e:
        logger.error(f"Detektálás sikertelen: {e}")
        return None

    # 5. Kivágás és előfeldolgozás
    try:
        t1 = time.time()
        ermék_kivágása_és_előfeldolgozása(
            bemenet, label_konyvtar, kivagott,
            clahe_clip=config['clahe_clip_határ'],
            blur_meret=tuple(config['blur_kernel_meret']),
            num_workers=config.get('num_workers', 4),
            logger=logger
        )
        ido_preprocess = time.time() - t1
    except Exception as e:
        logger.error(f"Előfeldolgozás hiba: {e}")
        return None

    # 6. Osztályozás
    try:
        t2 = time.time()
        results = ermék_osztályozása(
            kivagott, classify_model,
            save=config.get('mentesi_osztalyozas', False),
            batch_meret=config['batch_meret'],
            logger=logger
        )
        ido_classify = time.time() - t2
    except Exception as e:
        logger.error(f"Osztályozás hiba: {e}")
        return None

    # 7. Érték összegzés + mentés
    try:
        osszes_ertek, szamlalok = érték_kiszámítása_és_rendezés(
            results,
            osztalyozott,
            config['erme_ertekek'],
            konfidencia_kuszob=config['konfidencia_kuszob'],
            bizonytalan_kuszob=config.get('bizonytalan_kuszob', 0.7),
            logger=logger
        )
    except Exception as e:
        logger.error(f"Érték számítás hiba: {e}")
        return None

    # 8. Riport generálása
    teljes_ido = time.time() - teljes_start
    riport_ut = riport_mentese(osszes_ertek, szamlalok, teljes_ido)
    logger.info(f"PDF riport elmentve ide: {riport_ut}")

    # 9. Predict könyvtárak tisztítása
    predict_konyvtarak_kezeles(max_dirs=config['max_predict_konyvtarak'], logger=logger)

    # 10. Képernyőn megjelenítéshez
    logger.info(f"Érmék összértéke: {osszes_ertek} Ft")
    for nev, db in szamlalok.items():
        logger.info(f"{db} db {nev}")

    logger.info(f"Részidők: észlelés: {ido_detect:.2f} mp, előfeldolgozás: {ido_preprocess:.2f} mp, osztályozás: {ido_classify:.2f} mp, összesen: {teljes_ido:.2f} mp")

    return {
        'ossz_ertek': osszes_ertek,
        'szamlalok': szamlalok,
        'ido_detect': ido_detect,
        'ido_preprocess': ido_preprocess,
        'ido_classify': ido_classify,
        'ido_teljes': teljes_ido,
        'riport_ut': riport_ut,
        'output_mappa': osztalyozott
    }

if __name__ == '__main__':
    main()
