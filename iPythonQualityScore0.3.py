#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
IP Quality Score - GUI version v0.3
-----------------------------------------------------
- VERSION v0.3
- Lecture automatique de l'API KEY depuis ./apikey.txt
- Création du fichier apikey.txt si inexistant
- Champ API masqué (****) avec bouton 👁️ pour afficher/masquer
- Bouton "Enregistrer API"
- Affichage logo et date supprimés (mais conservés ci-dessous)
-----------------------------------------------------

# (Logo conservé en commentaire)
LOGO = (
    " (\\_/) \n"
    " (OvO) \n"
    " //uuu\\\\ \n"
    " V\\UUU/V \n"
    "  ^^ ^^"
)

# (Date de création conservée en commentaire)
CREATION_DATE = "18:36 17/08/2025"
"""

import os
import threading
import time
import requests
import csv
from datetime import datetime
from tkinter import (
    Tk, Frame, Label, Button, Entry, StringVar, filedialog, ttk,
    Scrollbar, VERTICAL, HORIZONTAL, END, BOTH, RIGHT, LEFT, X, Y,
    BOTTOM, messagebox
)
import pandas as pd

# ------------- CONFIGURATION -------------
VERSION = "0.3"
NAME = "PS_IpQualityScore"
OUT_FOLDER = "OUT"
COLUMN_WIDTH = 140  # largeur initiale fixe pour les colonnes
API_FILE = "apikey.txt"
# -----------------------------------------


class IPQualityApp:
    def __init__(self, root):
        self.root = root
        self.root.title(f"{NAME} - v{VERSION}")
        self.api_key = StringVar(value="")
        self.filepath = StringVar(value="")
        self.status = StringVar(value="Prêt")
        self.progress = 0.0
        self.dataframe = None
        self.sep_var = StringVar(value=';')
        self.show_api = False

        # Charger la clé API si elle existe
        self._load_api_key()
        self._build_ui()

    # --- API KEY handling ---
    def _load_api_key(self):
        if os.path.exists(API_FILE):
            try:
                with open(API_FILE, "r", encoding="utf-8") as f:
                    key = f.read().strip()
                    self.api_key.set(key)
            except Exception as e:
                messagebox.showerror("Erreur", f"Impossible de lire {API_FILE} : {e}")
        else:
            if messagebox.askyesno("Fichier manquant", f"Aucun fichier {API_FILE} trouvé.\nSouhaitez-vous le créer ?"):
                try:
                    with open(API_FILE, "w", encoding="utf-8") as f:
                        f.write("")
                    messagebox.showinfo("Créé", f"Le fichier {API_FILE} a été créé.\nEntrez votre API puis cliquez sur 'Enregistrer API'.")
                except Exception as e:
                    messagebox.showerror("Erreur", f"Impossible de créer {API_FILE} : {e}")

    def _save_api_key(self):
        try:
            with open(API_FILE, "w", encoding="utf-8") as f:
                f.write(self.api_key.get().strip())
            self.status.set(f"Clé API enregistrée dans {API_FILE}")
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible d'enregistrer la clé API : {e}")

    def _toggle_show_api(self):
        self.show_api = not self.show_api
        self.api_entry.config(show="" if self.show_api else "*")
        self.toggle_btn.config(text="🙈" if self.show_api else "👁️")

    # --- UI building ---
    def _build_ui(self):
        top = Frame(self.root, padx=8, pady=8)
        top.pack(fill=BOTH, expand=False)

        # Banner
        banner_text = f"#### {NAME} ####\n#### v{VERSION} ####"
        Label(top, text=banner_text, font=("Consolas", 12, "bold")).pack(anchor="w", pady=(0,8))

        # === API Key Section ===
        api_frame = Frame(top)
        api_frame.pack(fill="x", pady=(0,6))
        Label(api_frame, text="API KEY :", font=("Consolas", 10, "bold")).pack(anchor="w")
        api_inner = Frame(api_frame)
        api_inner.pack(fill="x")
        self.api_entry = Entry(api_inner, textvariable=self.api_key, width=60, show="*")
        self.api_entry.pack(side=LEFT, padx=(0,6))
        self.toggle_btn = Button(api_inner, text="👁️", width=3, command=self._toggle_show_api)
        self.toggle_btn.pack(side=LEFT)
        Button(api_inner, text="Enregistrer API", command=self._save_api_key).pack(side=LEFT, padx=(6,0))

        # === File selection ===
        file_frame = Frame(top)
        file_frame.pack(fill="x", pady=(6,6))
        Label(file_frame, text="Fichier IP :", font=("Consolas", 10, "bold")).pack(anchor="w")
        file_inner = Frame(file_frame)
        file_inner.pack(fill="x")
        Button(file_inner, text="Choisir fichier d'IP", command=self.choose_file).pack(side=LEFT)
        Label(file_inner, textvariable=self.filepath, anchor="w").pack(side=LEFT, padx=(8,0))

        # === Controls ===
        ctrl_frame = Frame(top)
        ctrl_frame.pack(fill="x", pady=(8,6))
        self.start_btn = Button(ctrl_frame, text="Lancer", command=self.start_job, width=12)
        self.start_btn.pack(side=LEFT)
        Button(ctrl_frame, text="Quitter", command=self.root.quit, width=12).pack(side=LEFT, padx=(6,0))

        # === Progress ===
        prog_frame = Frame(top)
        prog_frame.pack(fill="x", pady=(6,6))
        Label(prog_frame, textvariable=self.status).pack(anchor="w")
        self.progressbar = ttk.Progressbar(prog_frame, orient="horizontal", length=400, mode="determinate")
        self.progressbar.pack(anchor="w", pady=(4,0))

        # === Table Preview ===
        table_outer = Frame(self.root, padx=8, pady=8)
        table_outer.pack(fill=BOTH, expand=True)
        Label(table_outer, text="Aperçu (Preview) :").pack(anchor="w")
        table_frame = Frame(table_outer)
        table_frame.pack(fill=BOTH, expand=True)

        columns = [
            "IP","fraudscore","success","message","country_code","region","city","ISP","ASN",
            "organization","latitude","longitude","is_crawler","timezone","mobile","host","proxy",
            "vpn","tor","active_vpn","active_tor","recent_abuse","bot_status"
        ]

        vsb = Scrollbar(table_frame, orient=VERTICAL)
        vsb.pack(side=RIGHT, fill=Y)
        hsb = Scrollbar(table_outer, orient=HORIZONTAL)
        hsb.pack(side=BOTTOM, fill=X)

        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=12,
                                 yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        for c in columns:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=COLUMN_WIDTH, stretch=True, anchor="w")
        self.tree.pack(side=LEFT, fill=BOTH, expand=True)
        vsb.config(command=self.tree.yview)
        hsb.config(command=self.tree.xview)

        # === Export Frame ===
        export_frame = Frame(self.root, pady=6)
        export_frame.pack(fill="x")
        Label(export_frame, text="Séparateur CSV :").pack(side=LEFT, padx=(8,0))
        sep_combo = ttk.Combobox(export_frame, textvariable=self.sep_var, width=5)
        sep_combo['values'] = [';', ',', '\t', '|', ':']
        sep_combo.pack(side=LEFT)
        Button(export_frame, text="Exporter CSV (OUT)", command=self.export_csv, width=18).pack(side=LEFT, padx=(6,0))
        Label(export_frame, text="Le CSV utilise le séparateur choisi").pack(side=LEFT, padx=(8,0))

    # --- Functional parts ---
    def choose_file(self):
        p = filedialog.askopenfilename(title="Choisissez le fichier contenant les IP (1 par ligne)")
        if p:
            self.filepath.set(p.replace('"', ''))

    def start_job(self):
        if not self.filepath.get():
            self.status.set("Erreur : aucun fichier sélectionné.")
            return
        if not self.api_key.get().strip():
            self.status.set("Erreur : API KEY manquante.")
            return
        self._save_api_key()
        self.start_btn.config(state="disabled")
        threading.Thread(target=self._run, daemon=True).start()

    def _run(self):
        try:
            self.status.set("Lecture du fichier...")
            ips = self._read_ip_file(self.filepath.get())
            total = len(ips)
            if total == 0:
                self.status.set("Aucune IP trouvée.")
                self.start_btn.config(state="normal")
                return

            self.status.set(f"{total} IP à traiter...")
            results = []
            for idx, ip in enumerate(ips, start=1):
                url = f"https://ipqualityscore.com/api/json/ip/{self.api_key.get().strip()}/{ip}"
                try:
                    r = requests.get(url, timeout=15)
                    r.raise_for_status()
                    result = r.json()
                except Exception as e:
                    result = {"fraud_score": "", "success": False, "message": f"request_error: {e}"}
                row = {
                    "IP": ip,
                    "fraudscore": result.get("fraud_score", ""),
                    "success": result.get("success", False),
                    "message": result.get("message", ""),
                    "country_code": result.get("country_code", ""),
                    "region": result.get("region", ""),
                    "city": result.get("city", ""),
                    "ISP": result.get("ISP", ""),
                    "ASN": result.get("ASN", ""),
                    "organization": result.get("organization", ""),
                    "latitude": result.get("latitude", ""),
                    "longitude": result.get("longitude", ""),
                    "is_crawler": result.get("is_crawler", ""),
                    "timezone": result.get("timezone", ""),
                    "mobile": result.get("mobile", ""),
                    "host": result.get("thehost", ""),
                    "proxy": result.get("proxy", ""),
                    "vpn": result.get("vpn", ""),
                    "tor": result.get("tor", ""),
                    "active_vpn": result.get("active_vpn", ""),
                    "active_tor": result.get("active_tor", ""),
                    "recent_abuse": result.get("recent_abuse", ""),
                    "bot_status": result.get("bot_status", "")
                }
                results.append(row)
                self.progress = idx / total * 100
                self._update_progress(self.progress, f"Traitement {idx}/{total} ({ip})")
                time.sleep(0.05)
            df = pd.DataFrame(results)
            self.dataframe = df
            self._fill_treeview(df)
            self.status.set("Terminé. Visualisez puis exportez.")
        except Exception as e:
            self.status.set(f"Erreur interne: {e}")
        finally:
            self.start_btn.config(state="normal")
            self.progressbar['value'] = 100

    def _read_ip_file(self, path):
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            raw = [line.strip().strip('"').strip("'") for line in f if line.strip()]
        return sorted(set(raw))

    def _update_progress(self, percent, text=None):
        self.root.after(0, lambda: (self.progressbar.config(value=percent), self.status.set(text or "")))

    def _fill_treeview(self, df: pd.DataFrame):
        def _ui_fill():
            self.tree.delete(*self.tree.get_children())
            max_show = 2000
            for _, row in df.head(max_show).iterrows():
                values = [str(row.get(col, "")) for col in self.tree["columns"]]
                self.tree.insert("", "end", values=values)
            if len(df) > max_show:
                self.status.set(f"Aperçu limité à {max_show} lignes (total {len(df)}).")
        self.root.after(0, _ui_fill)

    def export_csv(self):
        if self.dataframe is None:
            self.status.set("Aucun résultat à exporter.")
            return
        source_folder = os.path.dirname(self.filepath.get())
        out_dir = os.path.join(source_folder, OUT_FOLDER)
        os.makedirs(out_dir, exist_ok=True)
        base_name = os.path.basename(self.filepath.get())
        timestamp = datetime.now().strftime("%Y.%m.%d_%H.%M.%S")
        out_name = f"{base_name}_{timestamp}_result_fraudscore.csv"
        out_path = os.path.join(out_dir, out_name)
        try:
            sep = self.sep_var.get()
            self.dataframe.to_csv(out_path, sep=sep, index=False, quoting=csv.QUOTE_MINIMAL)
            self.status.set(f"Exporté : {out_path}")
            try:
                if os.name == "nt":
                    os.startfile(out_dir)
                elif os.name == "posix":
                    import subprocess
                    subprocess.call(["xdg-open", out_dir])
            except Exception:
                pass
        except Exception as e:
            self.status.set(f"Erreur export : {e}")


def main():
    root = Tk()
    app = IPQualityApp(root)
    root.geometry("1200x700")
    root.mainloop()


if __name__ == "__main__":
    main()
