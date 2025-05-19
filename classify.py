# classify.py

import os
import shutil
import time
import csv

def ermék_osztályozása(konyvtar, classify_model, save=False, batch_meret=1, logger=None):
    start_time = time.time()
    try:
        results = list(classify_model.predict(konyvtar, save=save, stream=True, verbose=False, batch=batch_meret))
        if logger: logger.info(f"Érmék osztályozása: {time.time() - start_time:.2f} mp")
        return results
    except Exception as e:
        if logger: logger.error(f"Hiba az osztályozás során: {e}")
        raise

def érték_kiszámítása_és_rendezés(results, oszt_konyvtar, ertekek, csv_ut='exports/classification_results.csv',
                                   konfidencia_kuszob=0.5, bizonytalan_kuszob=0.7, logger=None):
    start_time = time.time()
    osszes = 0
    szamlalok = {}
    bizonytalan_mappa = os.path.join(oszt_konyvtar, 'bizonytalan')
    os.makedirs(bizonytalan_mappa, exist_ok=True)
    os.makedirs(os.path.dirname(csv_ut), exist_ok=True)

    with open(csv_ut, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['filename', 'predicted_class', 'confidence'])

        for res in results:
            idx = res.probs.top1
            conf = res.probs.top1conf.item()
            nev = res.names[idx] if conf >= konfidencia_kuszob else 'ismeretlen'
            if conf < bizonytalan_kuszob and nev != 'ismeretlen':
                nev = 'bizonytalan'

            kepnev = os.path.basename(res.path)
            cel_mappa = bizonytalan_mappa if nev == 'bizonytalan' else os.path.join(oszt_konyvtar, nev)
            os.makedirs(cel_mappa, exist_ok=True)
            shutil.copy(res.path, os.path.join(cel_mappa, kepnev))

            writer.writerow([kepnev, nev, round(conf, 3)])
            if nev in ertekek:
                osszes += ertekek[nev]
            szamlalok[nev] = szamlalok.get(nev, 0) + 1

    if logger:
        logger.info(f"Értékösszesítés + CSV export: {time.time() - start_time:.2f} mp")
    return osszes, szamlalok
