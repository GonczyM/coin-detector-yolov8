# gui.py

import tkinter as tk
from tkinter import filedialog, messagebox
import os
import subprocess
import yaml
import platform
import threading
from main import main as run_pipeline
from ultralytics import YOLO
from logger_config import setup_logger

LAST_CONFIG_FILE = "last_config.txt"

class ErmeFelismeroApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Pénzérme felismerő rendszer")
        self.geometry("600x500")
        self.config(padx=10, pady=10)

        self.logger = setup_logger()
        self.result = None
        self.detect_model = None
        self.classify_model = None

        # OE logó és verzió
        self.oe_label = tk.Label(self, text="OE", font=("Arial", 8), fg="gray")
        self.oe_label.place(x=560, y=480)
        self.bind("<Configure>", self.update_oe_position)

        # Konfig fájl kiválasztó
        tk.Label(self, text="Konfigurációs fájl:").pack()
        self.config_path_var = tk.StringVar()
        tk.Entry(self, textvariable=self.config_path_var, width=60).pack()
        tk.Button(self, text="Tallózás", command=self.browse_config).pack(pady=5)
        self.load_last_config()

        # Gombok
        button_frame = tk.Frame(self)
        button_frame.pack(pady=10)

        tk.Button(button_frame, text="📥 Input könyvtár megnyitása", command=self.open_input_folder).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="🧾 Riport megnyitása", command=self.open_pdf_report).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="📂 Output könyvtár megnyitása", command=self.open_output_folder).pack(side=tk.LEFT, padx=5)

        # Indító gomb
        tk.Button(self, text="Feldolgozás indítása", command=self.run_pipeline_thread, bg="green", fg="white").pack(pady=10)

        # Statisztikai kijelző
        self.stats_text = tk.Text(self, height=14, width=75, wrap="word", state="disabled", bg="#f0f0f0")
        self.stats_text.pack(pady=10)

        # Státuszbár
        self.statusbar = tk.Label(self, text="Verzió: 2.1", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.statusbar.pack(side=tk.BOTTOM, fill=tk.X)

    def update_oe_position(self, event=None):
        width = self.winfo_width()
        height = self.winfo_height()
        self.oe_label.place(x=width - 30, y=height - 25)

    def browse_config(self):
        filename = filedialog.askopenfilename(filetypes=[("YAML fájlok", "*.yaml")])
        if filename:
            self.config_path_var.set(filename)
            with open(LAST_CONFIG_FILE, "w") as f:
                f.write(filename)

    def load_last_config(self):
        if os.path.exists(LAST_CONFIG_FILE):
            with open(LAST_CONFIG_FILE, "r") as f:
                self.config_path_var.set(f.read().strip())

    def run_pipeline_thread(self):
        thread = threading.Thread(target=self.run_system_thread)
        thread.start()

    def run_system_thread(self):
        config_path = self.config_path_var.get()
        if not config_path:
            self.safe_show_error("Hiba", "Kérlek válassz konfigurációs fájlt.")
            return

        self.update_status("Feldolgozás folyamatban...")

        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)

            if not self.detect_model:
                self.detect_model = YOLO(config['detect_model_eleresi_ut'])
            if not self.classify_model:
                self.classify_model = YOLO(config['classify_model_eleresi_ut'])

            self.result = run_pipeline(config_path=config_path)
            if not self.result:
                raise Exception("A feldolgozás nem adott vissza eredményt.")

            self.after(0, lambda: self.show_stats(self.result))
            self.safe_show_info("Kész", "Feldolgozás befejezve!")
            self.update_status("Sikeres feldolgozás")
        except Exception as e:
            self.logger.exception("Hiba történt a feldolgozás közben.")
            self.safe_show_error("Hiba", f"Feldolgozás hiba: {e}")
            self.update_status("Hiba történt")

    def update_status(self, text):
        self.after(0, lambda: self.statusbar.config(text=text))

    def safe_show_info(self, title, msg):
        self.after(0, lambda: messagebox.showinfo(title, msg))

    def safe_show_error(self, title, msg):
        self.after(0, lambda: messagebox.showerror(title, msg))

    def show_stats(self, result):
        ossz = result['ossz_ertek']
        szamlalo = result['szamlalok']
        ido_detect = result['ido_detect']
        ido_pre = result['ido_preprocess']
        ido_cls = result['ido_classify']
        ido_teljes = result['ido_teljes']
        osszes_db = sum(szamlalo.values())

        try:
            with open(self.config_path_var.get(), 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            ertekek = config.get("erme_ertekek", {})
        except:
            ertekek = {}

        szamlalo_rendezett = dict(sorted(szamlalo.items(), key=lambda item: ertekek.get(item[0], 0), reverse=True))

        self.stats_text.config(state="normal")
        self.stats_text.delete("1.0", tk.END)

        self.stats_text.insert(tk.END, f"Érmék összértéke: {ossz} Ft\n")
        self.stats_text.insert(tk.END, f"Talált érmék: {osszes_db} db\n")
        self.stats_text.insert(tk.END, "\nDarabszámok:\n")
        for nev, db in szamlalo_rendezett.items():
            self.stats_text.insert(tk.END, f"  - {nev}: {db} db\n")

        self.stats_text.insert(tk.END, "\nIdők:\n")
        self.stats_text.insert(tk.END, f"  - Detektálás: {ido_detect:.2f} mp\n")
        self.stats_text.insert(tk.END, f"  - Előfeldolgozás: {ido_pre:.2f} mp\n")
        self.stats_text.insert(tk.END, f"  - Osztályozás: {ido_cls:.2f} mp\n")
        self.stats_text.insert(tk.END, f"  - Teljes feldolgozás: {ido_teljes:.2f} mp\n")

        self.stats_text.config(state="disabled")

    def open_folder(self, path):
        path = os.path.abspath(path)
        if not os.path.exists(path):
            self.safe_show_info("Figyelem", f"Nem található: {path}")
            return

        system = platform.system()
        try:
            if system == "Windows":
                subprocess.Popen(f'explorer "{path}"')
            elif system == "Darwin":
                subprocess.Popen(["open", path])
            else:
                subprocess.Popen(["xdg-open", path])
        except Exception as e:
            self.logger.error(f"Hiba a mappa megnyitásakor: {e}")
            self.safe_show_error("Hiba", f"Nem sikerült megnyitni a mappát.\n{e}")

    def open_output_folder(self):
        if self.result and 'output_mappa' in self.result:
            self.open_folder(self.result['output_mappa'])
        else:
            self.safe_show_info("Figyelem", "Előbb futtasd a rendszert.")

    def open_pdf_report(self):
        if self.result and 'riport_ut' in self.result:
            self.open_folder(self.result['riport_ut'])
        else:
            self.safe_show_info("Figyelem", "Előbb futtasd a rendszert.")

    def open_input_folder(self):
        try:
            with open(self.config_path_var.get(), 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            folder = config.get('bemeneti_kep_konyvtar', '.')
            self.open_folder(folder)
        except:
            self.safe_show_error("Hiba", "Nem sikerült megnyitni a feltöltő mappát.")

if __name__ == "__main__":
    app = ErmeFelismeroApp()
    app.mainloop()

