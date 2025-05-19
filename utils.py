# utils.py

import os
import shutil

TAMOGATOTT_KITERJESZTESEK = ['.jpg', '.jpeg', '.png', '.tif']

def egyedi_konyvtarnev_generalasa(alap_konyvtar):
    if not os.path.exists(alap_konyvtar):
        return alap_konyvtar
    i = 1
    while True:
        uj_konyvtar = f"{alap_konyvtar}_{i}"
        if not os.path.exists(uj_konyvtar):
            return uj_konyvtar
        i += 1

def konyvtarak_beallitasa(config):
    bemeneti_kep_konyvtar = config['bemeneti_kep_konyvtar']
    alap_kivagott_konyvtar = config['kivagott_ermék_konyvtar']
    alap_osztalyozott_konyvtar = config['osztalyozott_kepek_konyvtar']
    feluliras = config['feluliras']

    if feluliras:
        kivagott = alap_kivagott_konyvtar
        osztalyozott = alap_osztalyozott_konyvtar
        for dir_path in [kivagott, osztalyozott]:
            if os.path.exists(dir_path):
                shutil.rmtree(dir_path, ignore_errors=True)
    else:
        kivagott = egyedi_konyvtarnev_generalasa(alap_kivagott_konyvtar)
        osztalyozott = egyedi_konyvtarnev_generalasa(alap_osztalyozott_konyvtar)

    os.makedirs(kivagott, exist_ok=True)
    os.makedirs(osztalyozott, exist_ok=True)

    if not os.path.exists(bemeneti_kep_konyvtar):
        raise FileNotFoundError(f"A bemeneti könyvtár nem létezik: {bemeneti_kep_konyvtar}")

    return bemeneti_kep_konyvtar, kivagott, osztalyozott
