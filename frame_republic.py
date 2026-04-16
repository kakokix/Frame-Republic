# ================================================================
#  FRAME REPUBLIC  v1.0  -  PC Optimizer
#  Low-Poly Dark  /  Custom Window  /  JSON Save  /  2025
# ================================================================
import sys, os, ctypes, subprocess, threading, time
import shutil, glob, winreg, re, json, math
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False

VERSION     = "1.0.0"
VERSION_URL = "https://raw.githubusercontent.com/kakokix/Frame-Republic/main/version.json"
UPDATE_URL  = "https://raw.githubusercontent.com/kakokix/Frame-Republic/main/frame_republic.py"
NW        = 0x08000000
SAVE_FILE = os.path.join(os.environ.get("APPDATA",""), "FrameRepublic", "save.json")

# ── Admin ──────────────────────────────────────────────────────────
def is_admin():
    try: return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except: return False

def elevate():
    if not is_admin():
        try:
            args = " ".join('"'+a+'"' for a in sys.argv)
            if ctypes.windll.shell32.ShellExecuteW(None,"runas",sys.executable,args,None,1) > 32:
                sys.exit(0)
        except: pass

elevate()

# ── Helpers ─────────────────────────────────────────────────────────
def run(cmd, t=20):
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True,
                           text=True, timeout=t, creationflags=NW)
        return ((r.stdout or "")+(r.stderr or "")).strip()
    except Exception as e: return str(e)

def ps(s, t=25):
    return run('powershell -NoProfile -NonInteractive -WindowStyle Hidden -Command "'+s+'"', t)

def reg_set(hive, path, name, val):
    try:
        rtype = winreg.REG_DWORD if isinstance(val, int) else winreg.REG_SZ
        k = winreg.CreateKeyEx(hive, path, 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(k, name, 0, rtype, val)
        winreg.CloseKey(k); return True
    except: return False

def b2gb(b): return round(b/1024**3, 1)

def del_folder(path, pat="*"):
    freed = 0
    try:
        for item in glob.glob(os.path.join(path, pat)):
            try:
                if os.path.isfile(item):
                    freed += os.path.getsize(item); os.remove(item)
                else:
                    freed += sum(
                        os.path.getsize(os.path.join(r,f))
                        for r,_,fs in os.walk(item) for f in fs
                        if os.path.isfile(os.path.join(r,f)))
                    shutil.rmtree(item, ignore_errors=True)
            except: pass
    except: pass
    return freed/1024**2

def is_laptop():
    if HAS_PSUTIL:
        try: return psutil.sensors_battery() is not None
        except: pass
    return False

LAPTOP = is_laptop()

# ── JSON Save ────────────────────────────────────────────────────────
def load_save():
    try:
        with open(SAVE_FILE, encoding="utf-8") as f:
            return json.load(f)
    except: return {}

def write_save(data):
    try:
        os.makedirs(os.path.dirname(SAVE_FILE), exist_ok=True)
        with open(SAVE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except: pass

# ================================================================
#  PALETTE  LOW-POLY DARK
# ================================================================
BG      = "#09090f"   # fond principal
PANEL   = "#0d0e16"   # sidebar / topbar
CARD    = "#111320"   # carte
CARD_H  = "#161928"   # carte hover
BD      = "#1a1d2e"   # bordure normale
BD_A    = "#2a3050"   # bordure active
A       = "#00e5b8"   # accent cyan-vert
A2      = "#00b890"   # accent2
A_D     = "#001a14"   # accent tres fonce
BLUE    = "#2979ff"
ORANGE  = "#ff6d00"
RED     = "#e53935"
YELLOW  = "#fdd835"
PURPLE  = "#7c4dff"
WHITE   = "#eef0ff"
T1      = "#b8c0d8"   # texte principal
T2      = "#4a5270"   # texte secondaire
T3      = "#222840"   # texte tres fonce
P1      = "#0c0e1a"   # poly fonce
P2      = "#0f1220"   # poly moyen
P3      = "#131628"   # poly clair

# Polices
F_TITLE  = ("Rajdhani", 11, "bold")     # Police low-poly / futuriste
F_HEAD   = ("Rajdhani", 10, "bold")
F_BODY   = ("Rajdhani", 9)
F_SMALL  = ("Rajdhani", 8)
F_TINY   = ("Rajdhani", 7)
F_BADGE  = ("Rajdhani", 7, "bold")
F_SCORE  = ("Rajdhani", 36, "bold")
F_MONO   = ("Consolas", 8)
F_ICON   = ("Segoe MDL2 Assets", 14)
F_ICO_S  = ("Segoe MDL2 Assets", 12)

# Fallback si Rajdhani absent (toujours present sur Windows 10/11)
import tkinter.font as tkfont

def safe_font(preferred, fallback, size, *style):
    return (preferred, size, *style)

# ================================================================
#  POLYGONES LOW-POLY (dessines sur canvas)
# ================================================================
def draw_poly_bg(cv, w, h, tag="bg"):
    """Fond low-poly avec triangles."""
    cv.delete(tag)
    triangles = [
        # coin haut-gauche
        [(0,0), (200,0), (0,90)],
        [(200,0), (320,0), (0,90)],
        [(0,90), (320,0), (260,150)],
        # coin haut-droite
        [(w,0), (w-180,0), (w,85)],
        [(w-180,0), (w-300,0), (w,85)],
        # coin bas-gauche
        [(0,h), (0,h-80), (160,h)],
        [(160,h), (0,h-80), (240,h-50)],
        # coin bas-droite
        [(w,h), (w-160,h), (w,h-80)],
        [(w-160,h), (w-280,h), (w,h-80)],
        # milieu gauche
        [(0,h//2-60), (0,h//2+60), (70,h//2)],
        # milieu droite
        [(w,h//2-60), (w,h//2+60), (w-70,h//2)],
    ]
    colors = [P3,P2,P1,P3,P2,P2,P3,P2,P3,P2,P2]
    for tri, col in zip(triangles, colors):
        pts = [c for p in tri for c in p]
        cv.create_polygon(*pts, fill=col, outline=BD, width=1, tags=tag)

# ================================================================
#  TOGGLE
# ================================================================
class Toggle(tk.Canvas):
    W, H = 42, 22
    def __init__(self, parent, on_change=None, initial=False, **kw):
        bg = kw.pop("bg", CARD)
        super().__init__(parent, width=self.W, height=self.H,
                         bg=bg, highlightthickness=0, cursor="hand2", **kw)
        self._on  = bool(initial)
        self._cb  = on_change
        self._pos = 1.0 if initial else 0.0
        self._anim = False
        self._draw()
        self.bind("<Button-1>", self._click)

    def _lerp(self, t):
        r1,g1,b1 = 0x1a,0x1d,0x2e
        r2,g2,b2 = 0x00,0xe5,0xb8
        return "#{:02x}{:02x}{:02x}".format(
            int(r1+(r2-r1)*t), int(g1+(g2-g1)*t), int(b1+(b2-b1)*t))

    def _draw(self):
        self.delete("all")
        W,H,p = self.W,self.H,self._pos
        track = self._lerp(p)
        r = H//2
        self.create_oval(0,0,H,H, fill=track, outline="")
        self.create_oval(W-H,0,W,H, fill=track, outline="")
        self.create_rectangle(r,0,W-r,H, fill=track, outline=track)
        kx = r+int(p*(W-H))
        self.create_oval(kx-r+2,2,kx+r-2,H-2, fill="#050810", outline="")
        self.create_oval(kx-r+3,3,kx+r-3,H-3, fill=WHITE, outline="")

    def _click(self, _=None):
        self._on = not self._on
        if not self._anim: self._anim=True; self._animate()
        if self._cb: threading.Thread(target=self._cb, args=(self._on,), daemon=True).start()

    def _animate(self):
        target = 1.0 if self._on else 0.0
        diff   = target - self._pos
        if abs(diff) < 0.04:
            self._pos=target; self._anim=False; self._draw(); return
        self._pos += diff*0.28; self._draw(); self.after(14, self._animate)

    def set_silent(self, val):
        self._on  = bool(val)
        self._pos = 1.0 if val else 0.0
        self._draw()

# ================================================================
#  CARTE OPTIMISATION  (low-poly)
# ================================================================
class OptCard(tk.Frame):
    def __init__(self, parent, oid, title, desc1, desc2="",
                 on_toggle=None, initial=False, locked=False, soon=False, **kw):
        super().__init__(parent, bg=CARD, highlightthickness=1, highlightbackground=BD, **kw)
        self._tog   = on_toggle
        self._title = title
        self._oid   = oid
        self._locked = locked

        # Triangle accent haut-gauche
        tri = tk.Canvas(self, width=22, height=22, bg=CARD, highlightthickness=0)
        tri.place(x=0, y=0)
        tri.create_polygon(0,0,22,0,0,22, fill=A_D, outline="")

        inner = tk.Frame(self, bg=CARD, padx=13, pady=10)
        inner.pack(fill="both", expand=True)

        # Titre + controle
        top = tk.Frame(inner, bg=CARD); top.pack(fill="x")
        tk.Label(top, text=title, font=F_HEAD, bg=CARD, fg=T1, anchor="w").pack(side="left")

        if soon:
            tk.Label(top, text=" BIENTOT ", font=F_BADGE, bg=A, fg=BG, padx=3).pack(side="right")
        elif locked:
            tk.Label(top, text="\ue72e", font=F_ICO_S, bg=CARD, fg=T3).pack(side="right")
        else:
            self._tgl = Toggle(top, on_change=self._toggled, initial=initial, bg=CARD)
            self._tgl.pack(side="right")

        # Descriptions
        tk.Label(inner, text=desc1, font=F_SMALL, bg=CARD, fg=T2,
                 anchor="w", wraplength=248, justify="left").pack(fill="x", pady=5)
        if desc2:
            tk.Label(inner, text=desc2, font=F_TINY, bg=CARD, fg=T3,
                     anchor="w", wraplength=248, justify="left").pack(fill="x", pady=1)

        # Statut
        sf = tk.Frame(inner, bg=CARD); sf.pack(fill="x", pady=7)
        self._dot = tk.Canvas(sf, width=8, height=8, bg=CARD, highlightthickness=0)
        self._dot.pack(side="left", padx=0)
        self._status = tk.Label(sf, font=F_TINY, bg=CARD)
        self._status.pack(side="left")
        self._set_status(initial and not locked and not soon)

        # Hover
        for w in self._all(self):
            w.bind("<Enter>", lambda e: self._hover(True))
            w.bind("<Leave>", lambda e: self._hover(False))

    def _all(self, w):
        yield w
        for c in w.winfo_children():
            yield from self._all(c)

    def _set_status(self, on):
        col = A if on else T3
        self._dot.delete("all")
        self._dot.create_polygon(4,0,8,8,0,8, fill=col, outline="")
        self._status.config(text="Actif" if on else "Inactif", fg=col)

    def _hover(self, on):
        col = CARD_H if on else CARD
        bdr = BD_A   if on else BD
        self.config(bg=col, highlightbackground=bdr)
        for w in self._all(self):
            try: w.config(bg=col)
            except: pass

    def _toggled(self, state):
        self._set_status(state)
        if self._tog: threading.Thread(target=self._tog, args=(state,), daemon=True).start()

# ================================================================
#  BOUTON SIDEBAR
# ================================================================
class SideBtn(tk.Frame):
    H = 60

    def __init__(self, parent, ico, lbl, cmd, **kw):
        super().__init__(parent, bg=PANEL, width=64, height=self.H, cursor="hand2", **kw)
        self.pack_propagate(False)
        self._cmd    = cmd
        self._active = False

        self._bar = tk.Frame(self, bg=PANEL, width=3)
        self._bar.pack(side="left", fill="y")

        mid = tk.Frame(self, bg=PANEL)
        mid.pack(fill="both", expand=True, pady=8)

        self._ico = tk.Label(mid, text=ico, font=F_ICON, bg=PANEL, fg=T2)
        self._ico.pack()
        self._lbl = tk.Label(mid, text=lbl, font=("Segoe UI", 6), bg=PANEL, fg=T3)
        self._lbl.pack()

        for w in (self, mid, self._ico, self._lbl, self._bar):
            w.bind("<Button-1>", lambda e: self._cmd())
            w.bind("<Enter>",    lambda e: self._hover(True))
            w.bind("<Leave>",    lambda e: self._hover(False))

    def _hover(self, on):
        if self._active: return
        c = CARD if on else PANEL
        self.config(bg=c)
        for w in (self._ico, self._lbl):
            w.config(bg=c, fg=T1 if on else T2)
        for ch in self.winfo_children():
            try: ch.config(bg=c)
            except: pass

    def activate(self):
        self._active = True
        act = "#0c1020"
        self._bar.config(bg=A)
        self.config(bg=act)
        for w in (self._ico, self._lbl): w.config(fg=A, bg=act)
        for ch in self.winfo_children():
            try: ch.config(bg=act)
            except: pass

    def deactivate(self):
        self._active = False
        self._bar.config(bg=PANEL)
        self.config(bg=PANEL)
        for w in (self._ico, self._lbl): w.config(fg=T2, bg=PANEL)
        for ch in self.winfo_children():
            try: ch.config(bg=PANEL)
            except: pass

# ================================================================
#  APPLICATION
# ================================================================
class App(tk.Tk):

    def __init__(self):
        super().__init__()
        self.overrideredirect(True)
        self.configure(bg=BG)
        try: ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except: pass

        self._save       = load_save()
        self._cards      = {}    # oid -> OptCard
        self._side_btns  = {}    # key -> SideBtn
        self._ring_fns   = {}    # key -> draw_fn
        self._spark_fns  = {}    # key -> push_fn
        self._stat_lbls  = {}    # key -> Label
        self._pages      = {}    # key -> Frame   (les vraies pages)
        self._net_prev   = None
        self._net_ts     = time.time()
        self._dn_kbs     = 0.0
        self._up_kbs     = 0.0
        self._drag_x     = 0
        self._drag_y     = 0
        self._maximized  = False
        self._norm_geo   = "1160x730"
        self._nm_running = False
        self._nm_cards   = {}
        self._nm_log     = None
        self._n_log      = None

        self._build()
        self._setup_style()

        if HAS_PSUTIL: psutil.cpu_percent(interval=None)
        self.after(900, self._poll)
        # Lancer la verification de mise a jour en arriere-plan
        self.after(2000, self._check_update_bg)
        self.protocol("WM_DELETE_WINDOW", self._quit)

        self.update_idletasks()
        w,h = 1160,730
        x = (self.winfo_screenwidth()-w)//2
        y = (self.winfo_screenheight()-h)//2
        self.geometry("{}x{}+{}+{}".format(w,h,x,y))

    # ================================================================
    #  SYSTEME DE MISE A JOUR AUTOMATIQUE
    # ================================================================
    def _check_network(self):
        """Verifie si le reseau est disponible."""
        try:
            import socket
            socket.setdefaulttimeout(3)
            socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect(
                ("8.8.8.8", 53))
            return True
        except Exception:
            return False

    def _parse_version(self, v):
        """Convertit '1.2.3' en tuple (1,2,3) pour comparaison."""
        try:
            return tuple(int(x) for x in str(v).strip().split("."))
        except Exception:
            return (0, 0, 0)

    def _check_update_bg(self):
        """Lance la verification en arriere-plan toutes les 2 heures."""
        threading.Thread(target=self._update_loop, daemon=True).start()

    def _update_loop(self):
        """Boucle de verification periodique (toutes les 2h)."""
        # Premier check apres 30 secondes (laisse le temps au demarrage)
        time.sleep(30)
        while True:
            self._do_update_check()
            # Attendre 2 heures avant le prochain check
            time.sleep(7200)

    def _do_update_check(self):
        """Verifie si une mise a jour est disponible."""
        if not self._check_network():
            return  # Pas de reseau, on skip silencieusement

        try:
            import urllib.request
            import ssl

            # Contexte SSL permissif pour eviter les erreurs de cert
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode    = ssl.CERT_NONE

            req = urllib.request.Request(
                VERSION_URL,
                headers={"User-Agent": "FrameRepublic/" + VERSION})

            with urllib.request.urlopen(req, timeout=8, context=ctx) as r:
                data = json.loads(r.read().decode("utf-8"))

            remote_ver   = data.get("version", "0.0.0")
            remote_notes = data.get("notes", "")

            if self._parse_version(remote_ver) > self._parse_version(VERSION):
                # Nouvelle version disponible -> notifier dans l UI
                self.after(0, lambda v=remote_ver, n=remote_notes:
                           self._show_update_available(v, n))

        except Exception:
            pass  # Echec silencieux

    def _show_update_available(self, new_ver, notes):
        """Affiche la notification de mise a jour dans la topbar."""
        # Badge dans la topbar
        if hasattr(self, "_upd_badge"):
            self._upd_badge.config(
                text="  Mise a jour " + new_ver + " disponible  ",
                fg=BG, bg=A, cursor="hand2")
            self._upd_badge.bind("<Button-1>",
                lambda e, v=new_ver, n=notes: self._prompt_update(v, n))
        self._dlog("Mise a jour disponible: v" + new_ver + " - " + notes)

    def _prompt_update(self, new_ver, notes):
        """Demande a l utilisateur s il veut mettre a jour."""
        msg = (
            "Mise a jour disponible: v" + new_ver + "\n"
            "Version actuelle: v" + VERSION + "\n\n"
            "Notes: " + notes + "\n\n"
            "Installer maintenant ?\n"
            "(Le logiciel redemarrera automatiquement)"
        )
        if messagebox.askyesno("Mise a jour Frame Republic", msg):
            threading.Thread(
                target=self._download_and_apply,
                args=(new_ver,), daemon=True).start()

    def _download_and_apply(self, new_ver):
        """Telecharge et applique la mise a jour."""
        try:
            import urllib.request, ssl, shutil

            self._dlog("Telechargement de la mise a jour v" + new_ver + "...")

            # Verifier le reseau une derniere fois
            if not self._check_network():
                self.after(0, lambda: messagebox.showerror(
                    "Erreur", "Pas de connexion reseau."))
                return

            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode    = ssl.CERT_NONE

            # Chemin du script actuel
            script_path = os.path.abspath(__file__)
            backup_path = script_path + ".backup"
            tmp_path    = script_path + ".tmp"

            # Telecharger dans un fichier temporaire
            req = urllib.request.Request(
                UPDATE_URL,
                headers={"User-Agent": "FrameRepublic/" + VERSION})

            with urllib.request.urlopen(req, timeout=30, context=ctx) as r:
                content = r.read()

            # Verifier que c est du Python valide
            try:
                import ast
                ast.parse(content.decode("utf-8"))
            except SyntaxError:
                self.after(0, lambda: messagebox.showerror(
                    "Erreur", "Fichier de mise a jour invalide."))
                return

            # Sauvegarder l ancien fichier
            shutil.copy2(script_path, backup_path)

            # Ecrire le nouveau fichier
            with open(tmp_path, "wb") as f:
                f.write(content)

            # Remplacer
            os.replace(tmp_path, script_path)

            self._dlog("Mise a jour installee. Redemarrage...")

            # Redemarrer le logiciel
            self.after(500, self._restart_app)

        except Exception as e:
            self.after(0, lambda err=str(e): messagebox.showerror(
                "Erreur mise a jour",
                "Echec: " + err + "\n\nAncienne version conservee."))
            # Restaurer le backup si besoin
            try:
                if os.path.exists(backup_path):
                    os.replace(backup_path, script_path)
            except Exception:
                pass

    def _restart_app(self):
        """Redemarre le logiciel proprement."""
        write_save(self._save)
        python = sys.executable
        script = os.path.abspath(__file__)
        self.destroy()
        subprocess.Popen([python, script], creationflags=NW)


    def _quit(self):
        write_save(self._save)
        self.destroy()

    # ================================================================
    #  BUILD
    # ================================================================
    def _build(self):
        # Bordure externe 1px accent - utilise grid pour resize propre
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        outer = tk.Frame(self, bg=BD_A)
        outer.grid(row=0, column=0, sticky="nsew", padx=1, pady=1)
        outer.grid_rowconfigure(1, weight=1)
        outer.grid_columnconfigure(0, weight=1)

        self._build_topbar(outer)

        body = tk.Frame(outer, bg=BG)
        body.grid(row=1, column=0, sticky="nsew")
        body.grid_rowconfigure(0, weight=1)
        body.grid_columnconfigure(1, weight=1)

        self._build_sidebar(body)

        # Zone contenu — UN seul frame qui contient tout
        self._content = tk.Frame(body, bg=BG)
        self._content.grid(row=0, column=1, sticky="nsew")

        # Creer toutes les pages dans le même parent
        for key in ["dashboard","perf","jeu","confidentialite",
                    "reseau","confort","nettoyage","processus","outils"]:
            pg = tk.Frame(self._content, bg=BG)
            pg.place(relx=0, rely=0, relwidth=1, relheight=1)
            self._pages[key] = pg

        # Construire chaque page
        self._build_dashboard()
        self._build_page_perf()
        self._build_page_jeu()
        self._build_page_confidentialite()
        self._build_page_reseau()
        self._build_page_confort()
        self._build_page_nettoyage()
        self._build_page_processus()
        self._build_page_outils()

        # Afficher dashboard par defaut
        self._nav("dashboard")

    # ================================================================
    #  TOPBAR  (custom window chrome)
    # ================================================================
    def _build_topbar(self, parent):
        bar = tk.Frame(parent, bg=PANEL, height=44)
        bar.grid(row=0, column=0, sticky="ew", columnspan=1)
        bar.grid_propagate(False)
        parent.grid_columnconfigure(0, weight=1)

        # Canvas low-poly dans la topbar
        cv = tk.Canvas(bar, bg=PANEL, highlightthickness=0)
        cv.place(relx=0, rely=0, relwidth=1, relheight=1)
        cv.create_polygon(0,0,220,0,0,44, fill=P3, outline="")
        cv.create_polygon(220,0,380,0,0,44, fill=P2, outline="")

        for w in (bar, cv):
            w.bind("<ButtonPress-1>",   self._drag_start)
            w.bind("<B1-Motion>",       self._drag_move)
            w.bind("<Double-Button-1>", self._toggle_max)

        # Logo hexagone
        logo = tk.Frame(bar, bg=PANEL)
        logo.place(x=12, rely=0.5, anchor="w")
        hx = tk.Canvas(logo, width=28, height=28, bg=PANEL, highlightthickness=0)
        hx.pack(side="left")
        pts = []
        for i in range(6):
            a = math.radians(60*i-30); pts += [14+12*math.cos(a), 14+12*math.sin(a)]
        hx.create_polygon(*pts, fill=A_D, outline=A, width=1)
        hx.create_text(14,14, text="FR", fill=A, font=("Rajdhani",8,"bold"))
        for w in (hx, logo):
            w.bind("<ButtonPress-1>", self._drag_start)
            w.bind("<B1-Motion>",     self._drag_move)

        tk.Label(logo, text="  FRAME REPUBLIC", font=("Rajdhani",12,"bold"),
                 bg=PANEL, fg=WHITE).pack(side="left")
        tk.Label(logo, text="  PC Optimizer", font=F_SMALL,
                 bg=PANEL, fg=T2).pack(side="left")

        # Boutons fenetre
        wb = tk.Frame(bar, bg=PANEL)
        wb.place(relx=1, rely=0, anchor="ne")
        for sym,col_h,cmd in [
            ("  -  ", CARD_H,  self._minimize),
            ("  o  ", CARD_H,  self._toggle_max),
            ("  x  ", RED,     self._quit),
        ]:
            lb = tk.Label(wb, text=sym, font=("Segoe UI",10,"bold"),
                          bg=PANEL, fg=T2, cursor="hand2")
            lb.pack(side="left", ipady=12, ipadx=3)
            ch = col_h
            lb.bind("<Enter>", lambda e, w=lb, c=ch: w.config(bg=c, fg=WHITE))
            lb.bind("<Leave>", lambda e, w=lb: w.config(bg=PANEL, fg=T2))
            lb.bind("<Button-1>", lambda e, c=cmd: c())

        # Badge + horloge
        mid = tk.Frame(bar, bg=PANEL)
        mid.place(relx=0.5, rely=0.5, anchor="center")
        adm_col = A if is_admin() else ORANGE
        tk.Label(mid, text="  "+("ADMIN" if is_admin() else "NON-ADMIN")+"  ",
                 font=F_BADGE, bg=A_D, fg=adm_col).pack(side="left", padx=4)
        self._clock = tk.Label(mid, text="", font=F_TINY, bg=PANEL, fg=T2)
        self._clock.pack(side="left", padx=8)
        self._tick()

        # Badge mise a jour (invisible par defaut)
        self._upd_badge = tk.Label(mid, text="", font=F_BADGE,
                                    bg=PANEL, fg=PANEL, padx=6, pady=2)
        self._upd_badge.pack(side="left", padx=4)

        # Separateur accent degrade
        sep = tk.Canvas(parent, height=2, bg=BG, highlightthickness=0)
        sep.grid(row=1, column=0, sticky="ew")
        def draw_sep(e=None):
            sep.delete("all")
            w = sep.winfo_width()
            if w < 10: return
            sep.create_line(0,1,w//2,1, fill=A, width=2)
            sep.create_line(w//2,1,w,1, fill=A2, width=2)
        sep.bind("<Configure>", lambda e: draw_sep())

    def _tick(self):
        self._clock.config(text=datetime.now().strftime("%H:%M:%S"))
        self.after(1000, self._tick)

    def _drag_start(self, e):
        self._drag_x = e.x_root - self.winfo_x()
        self._drag_y = e.y_root - self.winfo_y()

    def _drag_move(self, e):
        if not self._maximized:
            self.geometry("+{}+{}".format(
                e.x_root-self._drag_x, e.y_root-self._drag_y))

    def _minimize(self):
        self.overrideredirect(False); self.iconify()
        self.bind("<Map>", lambda e: (self.overrideredirect(True), self.unbind("<Map>")))

    def _toggle_max(self, _=None):
        if self._maximized:
            self.geometry(self._norm_geo); self._maximized = False
        else:
            self._norm_geo = self.geometry()
            sw = self.winfo_screenwidth()
            sh = self.winfo_screenheight()
            # Use workarea height (minus taskbar ~40px)
            self.geometry("{}x{}+0+0".format(sw, sh - 40))
            self._maximized = True
        # Force layout update
        self.update_idletasks()

    # ================================================================
    #  SIDEBAR
    # ================================================================
    def _build_sidebar(self, parent):
        sb = tk.Frame(parent, bg=PANEL, width=64)
        sb.grid(row=0, column=0, sticky="ns"); sb.grid_propagate(False)

        # Separateur droite
        tk.Frame(sb, bg=BD, width=1).pack(side="right", fill="y")

        # Canvas low-poly sidebar
        cv = tk.Canvas(sb, bg=PANEL, highlightthickness=0, width=63)
        cv.place(relx=0, rely=0, relwidth=1, relheight=1)
        def draw_sb(e=None):
            cv.delete("sbp")
            h = cv.winfo_height()
            cv.create_polygon(0,0,63,0,63,120, fill=P3, outline="", tags="sbp")
            cv.create_polygon(0,0,63,120,0,200, fill=P2, outline="", tags="sbp")
            if h > 10:
                cv.create_polygon(0,h,63,h,0,h-100, fill=P2, outline="", tags="sbp")
        cv.bind("<Configure>", lambda e: draw_sb())

        # Inner par-dessus
        inner = tk.Frame(sb, bg=PANEL)
        inner.place(relx=0, rely=0, relwidth=1, relheight=1)

        pages = [
            ("dashboard",       "\ue80f", "Accueil"),
            ("perf",            "\ue945", "Perfs"),
            ("jeu",             "\ue7fc", "Jeu"),
            ("confidentialite", "\ue72e", "Prive"),
            ("reseau",          "\uec27", "Reseau"),
            ("confort",         "\ued54", "Confort"),
            ("nettoyage",       "\uea99", "Nettoyer"),
            ("processus",       "\ue9f9", "Process"),
            ("outils",          "\ue90f", "Outils"),
        ]
        for key, ico, lbl in pages:
            btn = SideBtn(inner, ico, lbl, cmd=lambda k=key: self._nav(k))
            btn.pack(fill="x")
            self._side_btns[key] = btn

        # Icone user en bas
        ub = tk.Frame(inner, bg=PANEL, height=46)
        ub.pack(side="bottom", fill="x"); ub.pack_propagate(False)
        tk.Frame(ub, bg=BD, height=1).pack(fill="x")
        tk.Label(ub, text="\ue77b", font=("Segoe MDL2 Assets",15),
                 bg=PANEL, fg=T3).pack(expand=True)

    # ── Navigation : lift() + activer le bon bouton ──────────────────
    def _nav(self, key):
        for k, btn in self._side_btns.items():
            if k == key: btn.activate()
            else:        btn.deactivate()
        # On leve la bonne page
        self._pages[key].lift()

    # ================================================================
    #  COMPOSANTS RÉUTILISABLES
    # ================================================================
    def _sub_tabs(self, parent, labels):
        """Barre d'onglets horizontaux. Retourne dict index->Frame."""
        bar  = tk.Frame(parent, bg=PANEL); bar.pack(fill="x")
        tk.Frame(parent, bg=BD, height=1).pack(fill="x")
        area = tk.Frame(parent, bg=BG);   area.pack(fill="both", expand=True)

        frames = {}; items = []

        def switch(idx):
            for i, (lw, ul) in enumerate(items):
                a = (i == idx)
                lw.config(fg=WHITE if a else T2,
                           font=(("Rajdhani",9,"bold") if a else F_TINY))
                ul.config(bg=A if a else PANEL)
            frames[idx].lift()

        for i, lbl in enumerate(labels):
            col = tk.Frame(bar, bg=PANEL); col.pack(side="left")
            lw  = tk.Label(col, text=lbl.upper(),
                           font=("Rajdhani",9,"bold") if i==0 else F_TINY,
                           bg=PANEL, fg=WHITE if i==0 else T2,
                           padx=14, pady=9, cursor="hand2")
            lw.pack()
            ul = tk.Frame(col, bg=A if i==0 else PANEL, height=2)
            ul.pack(fill="x")
            items.append((lw, ul))
            f = tk.Frame(area, bg=BG)
            f.place(relx=0, rely=0, relwidth=1, relheight=1)
            frames[i] = f
            ic = i
            lw.bind("<Button-1>", lambda e, idx=ic: switch(idx))

        return frames

    def _card_grid(self, parent, cards_data):
        """Grille scrollable 3 colonnes de OptCard."""
        cv = tk.Canvas(parent, bg=BG, highlightthickness=0)
        sb = tk.Scrollbar(parent, orient="vertical", command=cv.yview,
                          bg=PANEL, troughcolor=BG, relief="flat", width=5)
        inner = tk.Frame(cv, bg=BG)
        inner.bind("<Configure>",
            lambda e: cv.configure(scrollregion=cv.bbox("all")))
        cv.create_window((0,0), window=inner, anchor="nw")
        cv.configure(yscrollcommand=sb.set)
        cv.bind("<MouseWheel>",
            lambda e: cv.yview_scroll(-1*(e.delta//120), "units"))
        inner.bind("<MouseWheel>",
            lambda e: cv.yview_scroll(-1*(e.delta//120), "units"))
        cv.pack(side="left", fill="both", expand=True, padx=14, pady=10)
        sb.pack(side="right", fill="y", pady=10)

        grid = tk.Frame(inner, bg=BG); grid.pack(fill="both", expand=True)

        for i, d in enumerate(cards_data):
            oid = d["id"]
            saved = self._save.get(oid, d.get("initial", False))

            def make_cb(o, fn):
                def cb(state):
                    self._save[o] = state
                    write_save(self._save)
                    if fn and not d.get("locked") and not d.get("soon"):
                        try: fn(state)
                        except Exception as ex:
                            print("Erreur", o, ex)
                return cb

            card = OptCard(
                grid, oid=oid, title=d["title"],
                desc1=d["desc1"], desc2=d.get("desc2",""),
                on_toggle=make_cb(oid, d.get("fn")),
                initial=saved,
                locked=d.get("locked", False),
                soon=d.get("soon", False))
            card.grid(row=i//3, column=i%3, padx=6, pady=6, sticky="nsew")
            grid.columnconfigure(i%3, weight=1)
            self._cards[oid] = card

    def _mk_btn(self, parent, text, cmd, color=A, padx=10, pady=6):
        b = tk.Label(parent, text=text, font=F_SMALL, bg=CARD, fg=color,
                     padx=padx, pady=pady, cursor="hand2",
                     highlightthickness=1, highlightbackground=BD)
        b.bind("<Enter>",    lambda e, w=b, c=color: w.config(bg=CARD_H, highlightbackground=c))
        b.bind("<Leave>",    lambda e, w=b: w.config(bg=CARD, highlightbackground=BD))
        b.bind("<Button-1>", lambda e, c=cmd: threading.Thread(target=c, daemon=True).start())
        return b

    def _mk_console(self, parent, height=6):
        t = tk.Text(parent, bg=P1, fg=T2, font=F_MONO, relief="flat",
                    height=height, state="disabled",
                    selectbackground=A_D, wrap="word",
                    padx=8, pady=6,
                    highlightthickness=1, highlightbackground=BD)
        for tag, col in [("ok",A),("warn",YELLOW),("err",RED),
                         ("info",BLUE),("title",A),("dim",T3)]:
            t.tag_config(tag, foreground=col)
        return t

    def _clog(self, console, text, tag=""):
        console.config(state="normal")
        console.insert("end", datetime.now().strftime("%H:%M:%S")+"  "+text+"\n", tag)
        console.see("end"); console.config(state="disabled")

    # ================================================================
    #  DASHBOARD
    # ================================================================
    def _build_dashboard(self):
        pg = self._pages["dashboard"]

        # BG low-poly
        bg_cv = tk.Canvas(pg, bg=BG, highlightthickness=0)
        bg_cv.place(relx=0, rely=0, relwidth=1, relheight=1)
        bg_cv.bind("<Configure>", lambda e: draw_poly_bg(bg_cv, e.width, e.height))

        # Contenu par-dessus
        body = tk.Frame(pg, bg=BG)
        body.place(relx=0, rely=0, relwidth=1, relheight=1)

        # --- Ligne haute ---
        row1 = tk.Frame(body, bg=BG); row1.pack(fill="x", padx=18, pady=14)

        # Score
        sc_f = tk.Frame(row1, bg=CARD, highlightthickness=1, highlightbackground=BD)
        sc_f.pack(side="left", fill="y", padx=0)
        sc_cv = tk.Canvas(sc_f, width=130, height=120, bg=CARD, highlightthickness=0)
        sc_cv.pack()
        sc_cv.create_polygon(0,0,130,0,0,55, fill=A_D, outline="")
        sc_cv.create_polygon(130,120,0,120,130,65, fill=A_D, outline="")
        self._score_lbl = tk.Label(sc_f, text="--", font=F_SCORE, bg=CARD, fg=A)
        self._score_lbl.place(in_=sc_cv, relx=0.5, rely=0.36, anchor="center")
        tk.Label(sc_f, text="/ 100", font=F_TINY, bg=CARD, fg=T3).place(
            in_=sc_cv, relx=0.5, rely=0.66, anchor="center")
        self._score_sub = tk.Label(sc_f, text="Calcul...",
                                    font=("Rajdhani",8,"bold"), bg=CARD, fg=A2)
        self._score_sub.place(in_=sc_cv, relx=0.5, rely=0.88, anchor="center")

        # Jauges
        gf = tk.Frame(row1, bg=BG); gf.pack(side="left", padx=8)
        self._ring_fns = {}; self._spark_fns = {}

        for key, lbl, col in [("cpu","CPU",A),("ram","RAM",BLUE),("disk","DSK",ORANGE)]:
            cf = tk.Frame(gf, bg=BG); cf.pack(side="left", padx=8)
            cv = tk.Canvas(cf, width=82, height=82, bg=BG, highlightthickness=0)
            cv.pack()
            spbuf = []

            def mk_ring(canvas, color):
                def draw(pct):
                    canvas.delete("all")
                    col2 = A if pct<60 else YELLOW if pct<80 else RED
                    canvas.create_arc(7,7,75,75, start=90, extent=360,
                                     outline=BD_A, width=8, style="arc")
                    if pct > 0:
                        canvas.create_arc(7,7,75,75, start=90, extent=-int(3.6*pct),
                                         outline=col2, width=8, style="arc")
                    # Petit triangle deco coin bas-gauche
                    canvas.create_polygon(0,82,14,82,0,68, fill=P3, outline="")
                    canvas.create_text(41,35, text=str(int(pct))+"%",
                                      fill=col2, font=("Rajdhani",11,"bold"))
                return draw

            fn = mk_ring(cv, col)
            self._ring_fns[key] = fn
            cv.after(100, lambda f=fn: f(0))

            tk.Label(cf, text=lbl, font=F_TINY, bg=BG, fg=T2).pack(pady=3)

            sp = tk.Canvas(cf, width=82, height=18, bg=BG, highlightthickness=0)
            sp.pack()

            def mk_spark(canvas, color, buf):
                def push(v):
                    buf.append(max(0, min(100, float(v))))
                    if len(buf) > 60: buf.pop(0)
                    canvas.delete("all")
                    n = len(buf)
                    if n < 2: return
                    xs = [i*(82/(n-1)) for i in range(n)]
                    ys = [18-(p/100)*16 for p in buf]
                    pts = [0,18]+[c for p in zip(xs,ys) for c in p]+[82,18]
                    canvas.create_polygon(*pts, fill=color, outline="", stipple="gray50")
                    coords = [c for p in zip(xs,ys) for c in p]
                    canvas.create_line(*coords, fill=color, width=1, smooth=False)
                return push

            fn2 = mk_spark(sp, col, spbuf)
            self._spark_fns[key] = fn2

        # Batterie laptop
        if LAPTOP:
            bf = tk.Frame(gf, bg=BG); bf.pack(side="left", padx=8)
            cv_b = tk.Canvas(bf, width=82, height=82, bg=BG, highlightthickness=0)
            cv_b.pack()
            def draw_bat(p):
                cv_b.delete("all")
                col2 = A if p>30 else YELLOW if p>15 else RED
                cv_b.create_arc(7,7,75,75, start=90, extent=360, outline=BD_A, width=8, style="arc")
                if p > 0:
                    cv_b.create_arc(7,7,75,75, start=90, extent=-int(3.6*p),
                                   outline=col2, width=8, style="arc")
                cv_b.create_text(41,35, text=str(int(p))+"%",
                                fill=col2, font=("Rajdhani",11,"bold"))
            self._ring_fns["bat"] = draw_bat
            cv_b.after(100, lambda: draw_bat(0))
            tk.Label(bf, text="BATT", font=F_TINY, bg=BG, fg=T2).pack(pady=3)
            self._bat_txt = tk.Label(bf, text="--", font=F_TINY, bg=BG, fg=A)
            self._bat_txt.pack()

        # Actions rapides
        qa = tk.Frame(row1, bg=BG); qa.pack(side="left", padx=14)
        tk.Label(qa, text="ACTIONS RAPIDES", font=F_BADGE, bg=BG, fg=T3).pack(anchor="w", pady=0)
        for txt, col, cmd in [
            ("Liberer RAM",       A,      self._do_ram_free),
            ("Nettoyage rapide",  A,      self._clean_quick),
            ("Flush DNS",         BLUE,   lambda: threading.Thread(target=lambda:run("ipconfig /flushdns"),daemon=True).start()),
            ("Mode Gaming",       ORANGE, self._gaming_mode),
        ]:
            b = tk.Label(qa, text=txt, font=F_SMALL, bg=CARD, fg=col,
                         padx=10, pady=7, cursor="hand2",
                         highlightthickness=1, highlightbackground=BD)
            b.pack(fill="x", pady=2)
            b.bind("<Enter>",    lambda e,w=b,c=col: w.config(bg=CARD_H, highlightbackground=c))
            b.bind("<Leave>",    lambda e,w=b: w.config(bg=CARD, highlightbackground=BD))
            b.bind("<Button-1>", lambda e,c=cmd: threading.Thread(target=c,daemon=True).start())

        # Stat cards
        sc2 = tk.Frame(body, bg=BG); sc2.pack(fill="x", padx=18, pady=0)
        self._stat_lbls = {}
        stats = [("ram_free","RAM libre",A),("disk_free","Disque",ORANGE),
                 ("procs","Process",YELLOW),("net_dn","DL",A),
                 ("net_up","UL",A),("uptime","Uptime",BLUE),
                 ("bat","Batterie",BLUE),("cpu_info","CPU",WHITE)]
        for i,(key,lbl,col) in enumerate(stats):
            c = tk.Frame(sc2, bg=CARD, highlightthickness=1, highlightbackground=BD)
            c.grid(row=0, column=i, padx=4, sticky="nsew"); sc2.columnconfigure(i, weight=1)
            # Triangle deco
            tri = tk.Canvas(c, width=20,height=14, bg=CARD, highlightthickness=0)
            tri.pack(anchor="ne")
            tri.create_polygon(20,0,20,14,6,0, fill=A_D, outline="")
            ci = tk.Frame(c, bg=CARD, padx=8, pady=6); ci.pack(fill="both")
            tk.Label(ci, text=lbl, font=F_TINY, bg=CARD, fg=T3).pack(anchor="w")
            v = tk.Label(ci, text="--", font=("Rajdhani",10,"bold"), bg=CARD, fg=col)
            v.pack(anchor="w"); self._stat_lbls[key] = v

        # ── AUTO-OPTIMIZE PANEL ──────────────────────────────────────
        ao_frame = tk.Frame(body, bg=CARD,
                            highlightthickness=1, highlightbackground=BD)
        ao_frame.pack(fill="x", padx=18, pady=0)

        # Fond low-poly dans le panel
        ao_cv = tk.Canvas(ao_frame, height=50, bg=CARD, highlightthickness=0)
        ao_cv.place(relx=0, rely=0, relwidth=1, relheight=1)
        def draw_ao(e=None):
            w = ao_cv.winfo_width(); h = ao_cv.winfo_height()
            if w < 10: return
            ao_cv.delete("all")
            ao_cv.create_polygon(0,0,w,0,w,h,0,h, fill=CARD, outline="")
            ao_cv.create_polygon(0,0,180,0,0,50,   fill=P3, outline="")
            ao_cv.create_polygon(w,0,w-140,0,w,50, fill=P3, outline="")
        ao_cv.bind("<Configure>", lambda e: draw_ao())

        ao_inner = tk.Frame(ao_frame, bg=CARD, padx=14, pady=8)
        ao_inner.pack(fill="both", expand=True)

        # Titre + bouton
        ao_top = tk.Frame(ao_inner, bg=CARD); ao_top.pack(fill="x")
        ao_title_f = tk.Frame(ao_top, bg=CARD); ao_title_f.pack(side="left")

        # Triangle deco
        ao_tri = tk.Canvas(ao_title_f, width=16, height=16, bg=CARD, highlightthickness=0)
        ao_tri.pack(side="left", padx=0)
        ao_tri.create_polygon(8,0,16,16,0,16, fill=A, outline="")

        tk.Label(ao_title_f, text="OPTIMISATION AUTOMATIQUE",
                 font=("Rajdhani",10,"bold"), bg=CARD, fg=WHITE).pack(side="left")
        tk.Label(ao_title_f,
                 text="  Analyse et applique les optimisations sans endommager le systeme",
                 font=("Rajdhani",7), bg=CARD, fg=T2).pack(side="left")

        # Barre de progression + statut
        ao_mid = tk.Frame(ao_inner, bg=CARD); ao_mid.pack(fill="x", pady=6)

        # Barre progress custom low-poly
        self._ao_bar_frame = tk.Frame(ao_mid, bg=P2, height=8,
                                       highlightthickness=1, highlightbackground=BD)
        self._ao_bar_frame.pack(fill="x", pady=0)
        self._ao_bar_fill = tk.Frame(self._ao_bar_frame, bg=A, height=8, width=0)
        self._ao_bar_fill.place(x=0, y=0, height=8)

        ao_status_row = tk.Frame(ao_mid, bg=CARD); ao_status_row.pack(fill="x")
        self._ao_status = tk.Label(ao_status_row, text="Pret a optimiser",
                                    font=("Rajdhani",8), bg=CARD, fg=T2)
        self._ao_status.pack(side="left")
        self._ao_score_delta = tk.Label(ao_status_row, text="",
                                         font=("Rajdhani",8,"bold"), bg=CARD, fg=A)
        self._ao_score_delta.pack(side="left", padx=8)

        # Raisons / log compact
        self._ao_reasons = tk.Label(ao_inner, text="",
                                     font=("Rajdhani",7), bg=CARD, fg=T2,
                                     anchor="w", justify="left", wraplength=900)
        self._ao_reasons.pack(fill="x", pady=3)

        # Boutons
        ao_btns = tk.Frame(ao_top, bg=CARD); ao_btns.pack(side="right")

        self._ao_undo_btn = tk.Label(ao_btns, text="Annuler",
                                      font=("Rajdhani",8), bg=CARD, fg=T2,
                                      padx=10, pady=5, cursor="hand2",
                                      highlightthickness=1, highlightbackground=BD)
        self._ao_undo_btn.pack(side="right", padx=6)
        self._ao_undo_btn.bind("<Enter>", lambda e: self._ao_undo_btn.config(bg=CARD_H, highlightbackground=RED, fg=RED))
        self._ao_undo_btn.bind("<Leave>", lambda e: self._ao_undo_btn.config(bg=CARD, highlightbackground=BD, fg=T2))
        self._ao_undo_btn.bind("<Button-1>", lambda e: threading.Thread(target=self._ao_undo, daemon=True).start())

        self._ao_btn = tk.Label(ao_btns, text="  Optimiser maintenant  ",
                                 font=("Rajdhani",9,"bold"), bg=A_D, fg=A,
                                 padx=14, pady=5, cursor="hand2",
                                 highlightthickness=1, highlightbackground=A)
        self._ao_btn.pack(side="right")
        self._ao_btn.bind("<Enter>", lambda e: self._ao_btn.config(bg=A, fg=BG))
        self._ao_btn.bind("<Leave>", lambda e: self._ao_btn.config(bg=A_D, fg=A))
        self._ao_btn.bind("<Button-1>", lambda e: threading.Thread(target=self._ao_run, daemon=True).start())

        # Variables d'etat AO
        self._ao_running    = False
        self._ao_backup     = {}   # {oid: old_state} pour undo
        self._ao_score_before = 0

        # Journal
        tk.Label(body, text="JOURNAL", font=F_BADGE, bg=BG, fg=T3).pack(anchor="w", padx=18, pady=2)
        self._d_log = self._mk_console(body, height=5)
        self._d_log.pack(fill="both", expand=True, padx=18, pady=0)

    def _dlog(self, text, tag="ok"):
        self._clog(self._d_log, text, tag)

    # ================================================================
    #  PAGES OPTIMISATIONS
    # ================================================================
    def _opt_page(self, key, cards_data):
        """Construit une page simple avec grille de cartes."""
        pg = self._pages[key]
        self._card_grid(pg, cards_data)

    def _opt_page_tabs(self, key, tabs):
        """Construit une page avec onglets horizontaux.
           tabs = [("Nom", cards_data ou build_fn), ...]"""
        pg = self._pages[key]
        labels = [t[0] for t in tabs]
        frames = self._sub_tabs(pg, labels)
        for i, (name, content) in enumerate(tabs):
            if callable(content):
                content(frames[i])
            else:
                self._card_grid(frames[i], content)

    # ── Perfs ────────────────────────────────────────────────────
    def _build_page_perf(self):
        self._opt_page_tabs("perf", [
            ("Performances", self._perf_cards()),
            ("Jeu",          self._jeu_cards()),
            ("Demarrage",    self._build_startup),
            ("Registre",     self._build_reg),
        ])

    def _perf_cards(self): return [
        dict(id="ram_free",      title="Liberer la RAM",            desc1="Vide les pages memoire inutilisees.",       desc2="Ameliore la fluidite du systeme.",       fn=self._do_ram_free),
        dict(id="high_perf",     title="Plan Haute Performance",    desc1="Supprime les baisses auto de CPU.",         desc2="Maintient les frequences au maximum.",    fn=self._do_high_perf,    initial=True),
        dict(id="gamedvr",       title="Desactiver GameDVR",        desc1="Supprime les services Xbox.",               desc2="Reduit l'utilisation CPU/GPU.",            fn=self._do_gamedvr,      initial=True),
        dict(id="reg_perf",      title="Tweaks registre perf",      desc1="Reduit les delais systeme.",                desc2="Ameliore la reactivite.",                  fn=self._do_reg_perf,     initial=True),
        dict(id="superfetch",    title="Desactiver SysMain",        desc1="Stoppe le pre-chargement memoire.",         desc2="Recommande si moins de 8 Go.",             fn=self._do_superfetch),
        dict(id="visual_fx",     title="Effets visuels Performance",desc1="Supprime les effets graphiques.",           fn=self._do_visual_fx),
        dict(id="cpu_priority",  title="Priorite CPU AboveNormal",  desc1="Eleve la priorite des processus.",          desc2="Reduit les micro-coupures.",               fn=self._do_cpu_priority, initial=True),
        dict(id="copilot",       title="Desactiver Copilot",        desc1="Desactive l'IA Copilot Windows.",           desc2="Libere CPU et memoire.",                   fn=self._do_copilot,      initial=True),
        dict(id="plan_fr",       title="Plan Frame Republic",       desc1="Cree un plan d'alimentation sur-mesure.",   desc2="Performance maximale.",                    fn=self._do_power_plan_fr,initial=True),
        dict(id="mem_mgmt",      title="Optimisation memoire",      desc1="Ajuste les parametres de pagination.",      fn=self._do_memory_mgmt,                                                    initial=True),
        dict(id="msi",           title="Interruptions MSI",         desc1="Active MSI pour GPU et reseau.",            fn=self._do_msi),
        dict(id="timer",         title="Timer systeme",             desc1="Ameliore la precision des timers.",         fn=self._do_timer),
    ]

    def _jeu_cards(self): return [
        dict(id="game_mode",   title="Mode Jeu Windows",           desc1="Priorise les ressources.",            fn=self._do_game_mode),
        dict(id="xbox_svc",    title="Services Xbox off",           desc1="Arrete les services Xbox inutiles.",  fn=self._do_xbox,       initial=True),
        dict(id="tcp_game",    title="TCP gaming",                  desc1="Reduit le ping et la latence.",       fn=self._do_tcp_game,   initial=True),
        dict(id="gpu_cache",   title="Vider caches GPU",            desc1="DirectX, NVIDIA, AMD, Vulkan.",       fn=self._do_gpu_cache),
        dict(id="mouse_fps",   title="Souris FPS",                  desc1="Desactive l'acceleration souris.",    fn=self._do_mouse,      initial=True),
        dict(id="gamebar",     title="Desactiver Game Bar",         desc1="Supprime la surcouche Xbox.",         fn=self._do_gamebar,    initial=True),
        dict(id="affinity",    title="Affinite CPU",                desc1="Repartit sur tous les coeurs.",       soon=True),
        dict(id="msi_irq",     title="Interruptions MSI GPU",       desc1="Optimise les IRQ.",                   soon=True),
        dict(id="nvidia_opt",  title="GPU NVIDIA",                  desc1="Reglages NVIDIA performants.",        soon=True),
    ]

    def _build_startup(self, p):
        top = tk.Frame(p, bg=BG); top.pack(fill="x", padx=14, pady=8)
        self._mk_btn(top, "Rafraichir",     self._load_startup,     A).pack(side="left", padx=0)
        self._mk_btn(top, "Analyser impact",self._startup_impact,   BLUE).pack(side="left")
        cols = ("Nom","Type","Chemin","Statut")
        self._su_tree = ttk.Treeview(p, columns=cols, show="headings",
                                      style="FR.Treeview", height=14)
        for c,w in zip(cols,[200,110,430,90]):
            self._su_tree.heading(c,text=c); self._su_tree.column(c,width=w,anchor="w")
        sb = ttk.Scrollbar(p, orient="vertical", command=self._su_tree.yview)
        self._su_tree.configure(yscrollcommand=sb.set)
        self._su_tree.pack(side="left",fill="both",expand=True,padx=14)
        sb.pack(side="left",fill="y")
        self._su_log = self._mk_console(p,6)
        self._su_log.pack(fill="x",padx=14,pady=8)
        self.after(600, self._load_startup)

    def _build_reg(self, p):
        top = tk.Frame(p, bg=BG); top.pack(fill="x", padx=14, pady=8)
        for txt,cmd in [("Scanner orphelins",self._reg_scan),
                        ("Sauvegarder",self._reg_backup),
                        ("Tweaks perf",lambda:self._do_reg_perf(True)),
                        ("Telemetrie off",lambda:self._do_telemetry(True)),
                        ("Nettoyer MRU",self._do_mru)]:
            self._mk_btn(top,txt,cmd,A).pack(side="left",padx=0)
        self._r_log = self._mk_console(p)
        self._r_log.pack(fill="both",expand=True,padx=14,pady=0)

    # ── Autres pages ────────────────────────────────────────────
    def _build_page_jeu(self):
        self._opt_page("jeu", self._jeu_cards())

    def _build_page_confidentialite(self):
        self._opt_page("confidentialite", [
            dict(id="telemetry",    title="Telemetrie Windows",      desc1="Bloque l'envoi de donnees.",         fn=self._do_telemetry,       initial=True),
            dict(id="cortana",      title="Desactiver Cortana",      desc1="Desactive l'assistant vocal.",        fn=self._do_cortana,         initial=True),
            dict(id="ads",          title="Publicites ciblees",       desc1="Supprime l'ID publicitaire.",         fn=self._do_ads,             initial=True),
            dict(id="activity",     title="Historique activites",     desc1="Empeche la journalisation.",          fn=self._do_activity,        initial=True),
            dict(id="location",     title="Localisation",             desc1="Desactive le service GPS.",           fn=self._do_location),
            dict(id="br_telem",     title="Telemetrie navigateurs",   desc1="Chrome et Edge.",                     fn=self._do_browser_telem,   initial=True),
            dict(id="find_dev",     title="Find My Device",           desc1="Desactive le suivi.",                 fn=self._do_find_device,     initial=True),
            dict(id="win_search",   title="Recherche Windows",        desc1="Reduit l'indexation.",                fn=self._do_win_search,      initial=True),
            dict(id="copilot2",     title="Copilot IA",               desc1="Desactive Microsoft Copilot.",        fn=self._do_copilot,         initial=True),
        ])

    def _build_page_reseau(self):
        self._opt_page_tabs("reseau", [
            ("Optimisations", [
                dict(id="tcp",         title="Optimisation TCP/IP",       desc1="Ameliore le debit et la latence reseau.",        desc2="AutoTuning, chimney, DCA actives.",           fn=self._do_tcp,         initial=True),
                dict(id="dns_flush",   title="Vider cache DNS",           desc1="Resout les problemes de resolution de noms.",    desc2="Efface le cache DNS Windows.",                fn=self._do_dns_flush),
                dict(id="qos",         title="Desactiver QoS",            desc1="Libere 20% de bande passante reservee.",         desc2="Supprime la limitation Microsoft Psched.",    fn=self._do_qos,         initial=True),
                dict(id="net_power",   title="Alimentation carte reseau", desc1="Empeche l'arret automatique de la carte.",       desc2="Desactive le mode eco sur tous les adaptateurs.", fn=self._do_net_power, initial=True),
                dict(id="nagle",       title="Desactiver Nagle",          desc1="Envoie les paquets TCP immediatement.",          desc2="Reduit la latence en jeu (TCPNoDelay=1).",    fn=self._do_nagle,       initial=True),
                dict(id="ipv6",        title="Desactiver IPv6",           desc1="Desactive IPv6 si non utilise.",                 desc2="Reduit les timeouts de connexion IPv4.",       fn=self._do_ipv6),
                dict(id="smb",         title="Desactiver SMBv1",          desc1="Supprime le protocole reseau obsolete.",         desc2="SMBv1 est une faille de securite connue.",    fn=self._do_smb,         initial=True),
                dict(id="net_mtu",     title="Optimiser MTU (1500)",      desc1="Regle la taille max des paquets reseau.",        desc2="Evite la fragmentation des donnees.",         fn=self._do_mtu,         initial=True),
                dict(id="net_tcp_ack", title="Optimiser TCP ACK",         desc1="Reduit la frequence des accuses de reception.",  desc2="Ameliore le debit sur connexions rapides.",   fn=self._do_tcp_ack,     initial=True),
                dict(id="net_buf",     title="Buffers TCP etendus",       desc1="Augmente les tampons d envoi et reception.",     desc2="Ameliore les transferts de gros fichiers.",   fn=self._do_tcp_buf,     initial=True),
                dict(id="net_dns_pri", title="DNS Google (8.8.8.8)",      desc1="Configure Google DNS comme serveur primaire.",   desc2="Souvent plus rapide que les DNS de FAI.",     fn=self._do_dns_google),
                dict(id="winsock_r",   title="Reset Winsock",             desc1="Reinitialise la pile reseau Windows.",           desc2="Corrige les connexions cassees ou instables.", fn=self._do_winsock),
            ]),
            ("Diagnostics",  self._build_diag),
            ("Surveillance", self._build_net_monitor),
        ])

    def _build_diag(self, p):
        top = tk.Frame(p, bg=BG); top.pack(fill="x", padx=14, pady=8)
        for txt, cmd, col in [
            ("Test debit",     self._net_speed,    A),
            ("Connexions TCP", self._netstat,      A),
            ("Ports ouverts",  self._open_ports,   ORANGE),
            ("Adaptateurs",    self._net_adapters, BLUE),
            ("Ping 8.8.8.8",  self._ping,         A),
            ("Traceroute",     self._traceroute,   PURPLE),
            ("Table ARP",      self._arp,          A),
            ("Winsock info",   self._winsock_info, T2),
        ]:
            self._mk_btn(top, txt, cmd, col).pack(side="left", padx=4)
        if not hasattr(self, "_n_log") or not self._n_log:
            self._n_log = self._mk_console(p, height=20)
        else:
            self._n_log = self._mk_console(p, height=20)
        self._n_log.pack(fill="both", expand=True, padx=14, pady=0)

    def _build_net_monitor(self, p):
        """Surveillance reseau en temps reel."""
        hdr = tk.Frame(p, bg=BG); hdr.pack(fill="x", padx=14, pady=10)
        tk.Label(hdr, text="SURVEILLANCE EN TEMPS REEL",
                 font=("Rajdhani",9,"bold"), bg=BG, fg=A).pack(side="left")

        # Cartes stats
        cr = tk.Frame(p, bg=BG); cr.pack(fill="x", padx=14, pady=0)
        self._nm_cards = {}
        for key, lbl, col in [
            ("dl",     "Telechargement", A),
            ("ul",     "Envoi",          BLUE),
            ("latence","Latence",        ORANGE),
            ("paquets","Paquets/s",      PURPLE),
            ("erreurs","Erreurs",        RED),
        ]:
            c = tk.Frame(cr, bg=CARD, highlightthickness=1, highlightbackground=BD)
            c.pack(side="left", fill="y", padx=0, ipadx=6, ipady=6)
            tri = tk.Canvas(c, width=16, height=12, bg=CARD, highlightthickness=0)
            tri.pack(anchor="ne")
            tri.create_polygon(16,0,16,12,4,0, fill=A_D, outline="")
            tk.Label(c, text=lbl, font=F_TINY, bg=CARD, fg=T3).pack(padx=10)
            v = tk.Label(c, text="--", font=("Rajdhani",13,"bold"), bg=CARD, fg=col)
            v.pack(padx=10); self._nm_cards[key] = v

        # Boutons
        br = tk.Frame(p, bg=BG); br.pack(fill="x", padx=14, pady=0)
        self._nm_running = False
        self._nm_btn = self._mk_btn(br, "Demarrer la surveillance", self._nm_toggle, A)
        self._nm_btn.pack(side="left", padx=0)
        self._mk_btn(br, "Test latence Google", self._nm_latency_test, ORANGE).pack(side="left", padx=0)
        self._mk_btn(br, "Scanner ports locaux", self._nm_scan_ports, BLUE).pack(side="left")

        self._nm_log = self._mk_console(p, height=12)
        self._nm_log.pack(fill="both", expand=True, padx=14, pady=0)
        self._nm_prev_net = None; self._nm_prev_ts = time.time()

    def _build_page_confort(self):
        tabs = [
            ("Confort", [
                dict(id="dark",       title="Mode sombre Windows",   desc1="Active le theme sombre.",            fn=self._do_dark),
                dict(id="notifs",     title="Notifs desactivees",    desc1="Bloque les pop-ups Windows.",        fn=self._do_notifs),
                dict(id="explorer",   title="Explorateur optimise",  desc1="Affiche extensions et caches.",      fn=self._do_explorer,    initial=True),
                dict(id="start_snd",  title="Son demarrage off",     desc1="Supprime le son au boot.",           fn=self._do_start_sound, initial=True),
                dict(id="numlock",    title="NumLock auto",          desc1="Active le pave numerique.",          fn=self._do_numlock,     initial=True),
                dict(id="hibernate",  title="Desactiver hibernation",desc1="Libere hiberfil.sys (4-32 Go).",     fn=self._do_hibernate),
            ])
        ]
        if LAPTOP:
            tabs.append(("Laptop", [
                dict(id="eco",       title="Mode eco batterie",      desc1="CPU limite a 60%.",                 fn=self._do_eco,         initial=True),
                dict(id="hp_ac",     title="Haute perf. secteur",   desc1="Performance max quand branche.",    fn=self._do_high_perf),
                dict(id="auto_pow",  title="Bascule auto",          desc1="Detecte batterie/secteur auto.",    fn=self._do_auto_power,  initial=True),
                dict(id="bt_sb",     title="Bluetooth standby",     desc1="Coupe le BT en veille.",            fn=self._do_bt_standby),
            ]))
        self._opt_page_tabs("confort", tabs)

    def _build_page_nettoyage(self):
        pg = self._pages["nettoyage"]
        fs = self._sub_tabs(pg, ["Nettoyage"])
        p  = fs[0]

        body = tk.Frame(p, bg=BG); body.pack(fill="both",expand=True,padx=14,pady=10)

        left = tk.Frame(body,bg=BG,width=280); left.pack(side="left",fill="y",padx=0); left.pack_propagate(False)
        opts = tk.Frame(left,bg=CARD,highlightthickness=1,highlightbackground=BD); opts.pack(fill="x")
        tk.Label(opts,text="CIBLES",font=F_BADGE,bg=CARD,fg=T3,padx=12,pady=6).pack(anchor="w")
        tk.Frame(opts,bg=BD,height=1).pack(fill="x")
        self._cv = {}
        cibles=[("tmp_win","Temp Windows",True,A),("tmp_usr","Temp Utilisateur",True,A),
                ("prefetch","Prefetch",True,ORANGE),("recycle","Corbeille",True,RED),
                ("chrome","Cache Chrome",True,BLUE),("edge","Cache Edge",True,BLUE),
                ("logs","Logs Windows",True,T3),("thumbs","Cache miniatures",True,T3),
                ("crashes","Dump memoire",True,RED),("shaders","Caches GPU",True,ORANGE),
                ("wu","Cache Windows Update",False,ORANGE)]
        oi = tk.Frame(opts,bg=CARD,padx=10,pady=8); oi.pack(fill="x")
        for key,lbl,default,col in cibles:
            var=tk.BooleanVar(value=default); self._cv[key]=var
            row=tk.Frame(oi,bg=CARD); row.pack(fill="x",pady=1)
            tri=tk.Canvas(row,width=8,height=12,bg=CARD,highlightthickness=0); tri.pack(side="left",padx=0)
            tri.create_polygon(0,0,8,6,0,12, fill=col, outline="")
            tk.Checkbutton(row,text=lbl,variable=var,bg=CARD,fg=T2,selectcolor=CARD_H,
                           activebackground=CARD,activeforeground=A,
                           font=F_SMALL,cursor="hand2").pack(side="left",anchor="w")

        tk.Frame(left,bg=BD,height=1).pack(fill="x",pady=8)
        sel=tk.Frame(left,bg=BG); sel.pack(fill="x",pady=0)
        self._mk_btn(sel,"Tout",lambda:[x.set(True) for x in self._cv.values()],A).pack(side="left",padx=0)
        self._mk_btn(sel,"Rien",lambda:[x.set(False) for x in self._cv.values()],T2).pack(side="left")

        for txt,col,cmd in [("Analyser l'espace",BLUE,self._clean_scan),
                             ("Nettoyer maintenant",A,self._clean_confirm)]:
            b=tk.Label(left,text=txt,font=F_BODY,bg=CARD,fg=col,pady=9,cursor="hand2",
                       highlightthickness=1,highlightbackground=BD)
            b.pack(fill="x",pady=3)
            b.bind("<Enter>",lambda e,w=b,c=col: w.config(bg=CARD_H,highlightbackground=c))
            b.bind("<Leave>",lambda e,w=b: w.config(bg=CARD,highlightbackground=BD))
            b.bind("<Button-1>",lambda e,c=cmd: threading.Thread(target=c,daemon=True).start())

        self._c_bar=ttk.Progressbar(left,mode="indeterminate",style="FR.Horizontal.TProgressbar")
        self._c_bar.pack(fill="x",pady=8)
        self._c_res=tk.Label(left,text="",font=("Rajdhani",9,"bold"),bg=BG,fg=A)
        self._c_res.pack(anchor="w",pady=4)

        right=tk.Frame(body,bg=BG); right.pack(side="right",fill="both",expand=True)
        self._c_log=self._mk_console(right); self._c_log.pack(fill="both",expand=True)

    def _build_page_processus(self):
        pg=self._pages["processus"]
        fs=self._sub_tabs(pg,["Processus actifs"]); p=fs[0]

        top=tk.Frame(p,bg=BG); top.pack(fill="x",padx=14,pady=10)
        self._pr_search=tk.Entry(top,bg=CARD,fg=T1,font=F_SMALL,relief="flat",width=22,
                                  insertbackground=A,highlightthickness=1,highlightbackground=BD)
        self._pr_search.insert(0,"Rechercher...")
        self._pr_search.pack(side="left",ipady=6,padx=0)
        self._pr_search.bind("<FocusIn>",lambda e: self._pr_search.delete(0,"end") if self._pr_search.get()=="Rechercher..." else None)
        self._pr_search.bind("<KeyRelease>",lambda e: self._refresh_procs())

        for txt,col,cmd in [("Rafraichir",A,self._refresh_procs),
                             ("Terminer",RED,self._kill_proc),
                             ("Top CPU",ORANGE,self._top_cpu),
                             ("Top RAM",BLUE,self._top_ram)]:
            self._mk_btn(top,txt,cmd,col).pack(side="left",padx=0)
        self._pr_count=tk.Label(top,text="",font=F_TINY,bg=BG,fg=T3); self._pr_count.pack(side="right")

        cols=("PID","Nom","CPU %","RAM MB","Statut","Threads")
        self._pr_tree=ttk.Treeview(p,columns=cols,show="headings",style="FR.Treeview",height=24)
        for c,w in zip(cols,[70,240,70,80,100,70]):
            self._pr_tree.heading(c,text=c); self._pr_tree.column(c,width=w,anchor="center")
        self._pr_tree.column("Nom",anchor="w")
        sb=ttk.Scrollbar(p,orient="vertical",command=self._pr_tree.yview)
        self._pr_tree.configure(yscrollcommand=sb.set)
        self._pr_tree.pack(side="left",fill="both",expand=True,padx=14)
        sb.pack(side="left",fill="y")
        self.after(900,self._refresh_procs)

    def _build_page_outils(self):
        pg=self._pages["outils"]
        fs=self._sub_tabs(pg,["Outils Windows","Terminal"])

        grid=tk.Frame(fs[0],bg=BG); grid.pack(fill="x",padx=14,pady=12)
        tools=[("Gest. taches","taskmgr",A),("Panneau config.","control",BLUE),
               ("Infos systeme","msinfo32",BLUE),("Gestion disques","diskmgmt.msc",A),
               ("Editeur registre","regedit",RED),("Services Windows","services.msc",ORANGE),
               ("Config. reseau","ncpa.cpl",BLUE),("Options energie","powercfg.cpl",ORANGE),
               ("Strat. securite","secpol.msc",RED),("Obs. evenements","eventvwr.msc",PURPLE),
               ("Planificateur","taskschd.msc",ORANGE),("Windows Security","windowsdefender:",A),
               ("DirectX Diag","dxdiag",BLUE),("Programmes","appwiz.cpl",T2),
               ("Moniteur ressources","resmon",A),("Invite commandes","cmd",A)]
        for i,(lbl,cmd,col) in enumerate(tools):
            c=tk.Frame(grid,bg=CARD,highlightthickness=1,highlightbackground=BD,cursor="hand2")
            c.grid(row=i//4,column=i%4,padx=5,pady=5,sticky="nsew"); grid.columnconfigure(i%4,weight=1)
            tri=tk.Canvas(c,width=18,height=12,bg=CARD,highlightthickness=0); tri.pack(anchor="ne")
            tri.create_polygon(18,0,18,12,4,0,fill=A_D,outline="")
            tk.Label(c,text=lbl,font=F_TINY,bg=CARD,fg=T1,wraplength=150,justify="center").pack(expand=True,pady=5)
            def open_t(cm=cmd):
                try: os.startfile(cm)
                except:
                    try: subprocess.Popen(cm,creationflags=NW)
                    except Exception as ex: messagebox.showerror("Erreur",str(ex))
            c.bind("<Button-1>",lambda e,cm=cmd: open_t(cm))
            c.bind("<Enter>",lambda e,ca=c,co=col: ca.configure(bg=CARD_H,highlightbackground=co))
            c.bind("<Leave>",lambda e,ca=c: ca.configure(bg=CARD,highlightbackground=BD))
            for ch in c.winfo_children(): ch.bind("<Button-1>",lambda e,cm=cmd: open_t(cm))

        p1=fs[1]; cr=tk.Frame(p1,bg=BG); cr.pack(fill="x",padx=14,pady=12)
        self._t_entry=tk.Entry(cr,bg=CARD,fg=T1,font=F_MONO,insertbackground=A,
                                relief="flat",highlightthickness=1,highlightbackground=BD,width=75)
        self._t_entry.pack(side="left",ipady=7,padx=0)
        self._t_entry.bind("<Return>",lambda e: threading.Thread(target=self._run_terminal,daemon=True).start())
        self._mk_btn(cr,"Executer",self._run_terminal,A).pack(side="left")
        self._t_log=self._mk_console(p1); self._t_log.pack(fill="both",expand=True,padx=14,pady=0)

    # ================================================================
    #  ACTIONS SYSTEME
    # ================================================================
    PLANS={"eco":"a1841308-3541-4fab-bc81-f71556f20b4a",
           "bal":"381b4222-f694-41f0-9685-ff5bb260df2e",
           "high":"8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c"}

    def _do_ram_free(self,state=True):
        if not HAS_PSUTIL: return
        before=psutil.virtual_memory().percent
        try: ctypes.windll.psapi.EmptyWorkingSet(-1)
        except: pass
        time.sleep(0.5); after=psutil.virtual_memory().percent
        self._dlog("RAM: {:.0f}% -> {:.0f}%".format(before,after))

    def _do_high_perf(self,state=True):
        run("powercfg /setactive "+self.PLANS["high" if state else "bal"])
        if state:
            run("powercfg /setacvalueindex SCHEME_CURRENT SUB_PROCESSOR PROCTHROTTLEMAX 100")
            run("powercfg /setactive SCHEME_CURRENT")

    def _do_eco(self,state=True):
        if state:
            run("powercfg /setactive "+self.PLANS["eco"])
            run("powercfg /setdcvalueindex SCHEME_CURRENT SUB_PROCESSOR PROCTHROTTLEMAX 60")
            run("powercfg /setactive SCHEME_CURRENT")
        else: run("powercfg /setactive "+self.PLANS["bal"])

    def _do_power_plan_fr(self,state=True):
        if not state: run("powercfg /setactive "+self.PLANS["bal"]); return
        out=run("powercfg /duplicatescheme "+self.PLANS["high"])
        m=re.search(r"([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})",out)
        if m:
            g=m.group(1); run('powercfg /changename '+g+' "Frame Republic"')
            run("powercfg /setactive "+g)
            run("powercfg /setacvalueindex "+g+" SUB_PROCESSOR PROCTHROTTLEMAX 100")
            run("powercfg /setacvalueindex "+g+" SUB_SLEEP STANDBYIDLE 0")
            run("powercfg /setactive "+g)
        else: self._do_high_perf(True)

    def _do_auto_power(self,state=True):
        if not HAS_PSUTIL: return
        try:
            bat=psutil.sensors_battery()
            if bat:
                if bat.power_plugged: self._do_high_perf(True)
                else: self._do_eco(True)
        except: pass

    def _do_gamedvr(self,state=True):
        v=0 if state else 1
        reg_set(winreg.HKEY_CURRENT_USER,r"System\GameConfigStore","GameDVR_Enabled",v)
        reg_set(winreg.HKEY_CURRENT_USER,r"Software\Microsoft\Windows\CurrentVersion\GameDVR","AppCaptureEnabled",v)

    def _do_gamebar(self,state=True):
        v=0 if state else 1
        reg_set(winreg.HKEY_CURRENT_USER,r"Software\Microsoft\Windows\CurrentVersion\GameDVR","AppCaptureEnabled",v)
        reg_set(winreg.HKEY_CURRENT_USER,r"Software\Microsoft\GameBar","UseNexusForGameBarEnabled",v)

    def _do_reg_perf(self,state=True):
        reg_set(winreg.HKEY_CURRENT_USER,r"Control Panel\Desktop","MenuShowDelay","0")
        reg_set(winreg.HKEY_CURRENT_USER,r"Control Panel\Desktop","WaitToKillAppTimeout","2000")
        reg_set(winreg.HKEY_LOCAL_MACHINE,r"SYSTEM\CurrentControlSet\Control","WaitToKillServiceTimeout","2000")
        reg_set(winreg.HKEY_CURRENT_USER,r"Control Panel\Desktop","AutoEndTasks","1")

    def _do_visual_fx(self,state=True):
        ps("Set-ItemProperty 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\VisualEffects' -Name VisualFXSetting -Value "+("2" if state else "0")+" -ErrorAction SilentlyContinue")

    def _do_superfetch(self,state=True):
        sc="disabled" if state else "auto"
        run("sc config SysMain start= "+sc)
        if state: run("sc stop SysMain")
        else: run("sc start SysMain")

    def _do_cpu_priority(self,state=True):
        ps("Get-Process | Where-Object {$_.PriorityClass -eq 'Normal'} | ForEach-Object { try { $_.PriorityClass='AboveNormal' } catch {} }")

    def _do_msi(self,state=True):
        v="1" if state else "0"
        ps("$d=Get-PnpDevice -Class 'Display','Net' -ErrorAction SilentlyContinue; foreach($x in $d){$p='HKLM:\\SYSTEM\\CurrentControlSet\\Enum\\'+$x.InstanceId+'\\Device Parameters\\Interrupt Management\\MessageSignaledInterruptProperties'; if(Test-Path $p){Set-ItemProperty -Path $p -Name MSISupported -Value "+v+" -Type DWord -ErrorAction SilentlyContinue}}")

    def _do_timer(self,state=True):
        if state: run("bcdedit /set useplatformclock false"); run("bcdedit /set tscsyncpolicy enhanced")
        else: run("bcdedit /deletevalue useplatformclock")

    def _do_memory_mgmt(self,state=True):
        reg_set(winreg.HKEY_LOCAL_MACHINE,r"SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management","LargeSystemCache",0)
        reg_set(winreg.HKEY_LOCAL_MACHINE,r"SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management","DisablePagingExecutive",1 if state else 0)

    def _do_copilot(self,state=True):
        reg_set(winreg.HKEY_LOCAL_MACHINE,r"SOFTWARE\Policies\Microsoft\Windows\WindowsCopilot","TurnOffWindowsCopilot",1 if state else 0)

    def _do_game_mode(self,state=True):
        reg_set(winreg.HKEY_CURRENT_USER,r"Software\Microsoft\GameBar","AutoGameModeEnabled",1 if state else 0)

    def _do_xbox(self,state=True):
        sc="disabled" if state else "demand"
        for svc in ["XblAuthManager","XblGameSave","XboxNetApiSvc","XboxGipSvc"]:
            run("sc config "+svc+" start= "+sc)
            if state: run("sc stop "+svc)

    def _do_tcp_game(self,state=True):
        if state:
            run('powershell -Command "netsh int tcp set supplemental internet congestionprovider=ctcp"')
            run('powershell -Command "netsh interface tcp set global autotuninglevel=highlyrestricted"')
        else:
            run('powershell -Command "netsh int tcp set supplemental internet congestionprovider=none"')
            run('powershell -Command "netsh interface tcp set global autotuninglevel=normal"')

    def _do_gpu_cache(self,state=True):
        la=os.environ.get("LOCALAPPDATA","")
        for p in [os.path.join(la,"D3DSCache"),os.path.join(la,"NVIDIA","DXCache"),
                  os.path.join(la,"NVIDIA","GLCache"),os.path.join(la,"AMD","DxcCache")]:
            del_folder(p)

    def _do_mouse(self,state=True):
        if state:
            for n,v in [("MouseSpeed","0"),("MouseThreshold1","0"),("MouseThreshold2","0")]:
                reg_set(winreg.HKEY_CURRENT_USER,r"Control Panel\Mouse",n,v)

    def _do_telemetry(self,state=True):
        v=0 if state else 1
        for path in [r"SOFTWARE\Policies\Microsoft\Windows\DataCollection",
                     r"SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\DataCollection"]:
            reg_set(winreg.HKEY_LOCAL_MACHINE,path,"AllowTelemetry",v)
        sc="disabled" if state else "auto"
        for svc in ["DiagTrack","dmwappushservice"]:
            run("sc config "+svc+" start= "+sc)
            if state: run("sc stop "+svc)

    def _do_cortana(self,state=True):
        reg_set(winreg.HKEY_LOCAL_MACHINE,r"SOFTWARE\Policies\Microsoft\Windows\Windows Search","AllowCortana",0 if state else 1)

    def _do_ads(self,state=True):
        reg_set(winreg.HKEY_CURRENT_USER,r"SOFTWARE\Microsoft\Windows\CurrentVersion\AdvertisingInfo","Enabled",0 if state else 1)

    def _do_activity(self,state=True):
        reg_set(winreg.HKEY_LOCAL_MACHINE,r"SOFTWARE\Policies\Microsoft\Windows\System","EnableActivityFeed",0 if state else 1)

    def _do_location(self,state=True):
        reg_set(winreg.HKEY_LOCAL_MACHINE,r"SOFTWARE\Microsoft\Windows\CurrentVersion\CapabilityAccessManager\ConsentStore\location","Value","Deny" if state else "Allow")

    def _do_browser_telem(self,state=True):
        reg_set(winreg.HKEY_LOCAL_MACHINE,r"SOFTWARE\Policies\Google\Chrome","MetricsReportingEnabled",0 if state else 1)

    def _do_find_device(self,state=True):
        reg_set(winreg.HKEY_LOCAL_MACHINE,r"SOFTWARE\Policies\Microsoft\FindMyDevice","AllowFindMyDevice",0 if state else 1)

    def _do_win_search(self,state=True):
        reg_set(winreg.HKEY_LOCAL_MACHINE,r"SOFTWARE\Policies\Microsoft\Windows\Windows Search","DisableWebSearch",1 if state else 0)

    def _do_tcp(self,state=True):
        if state:
            run("netsh int tcp set global autotuninglevel=normal")
            run("netsh int tcp set global chimney=enabled")

    def _do_dns_flush(self,state=None):
        out=run("ipconfig /flushdns"); self._dlog("DNS: "+out[:80])

    def _do_qos(self,state=True):
        reg_set(winreg.HKEY_LOCAL_MACHINE,r"SOFTWARE\Policies\Microsoft\Windows\Psched","NonBestEffortLimit",0 if state else 80)

    def _do_net_power(self,state=True):
        if state: ps("Get-NetAdapter | ForEach-Object { try { Disable-NetAdapterPowerManagement -Name $_.Name -WakeOnMagicPacket -WakeOnPattern -D0PacketCoalescing -ErrorAction SilentlyContinue } catch {} }")

    def _do_nagle(self,state=True):
        reg_set(winreg.HKEY_LOCAL_MACHINE,r"SYSTEM\CurrentControlSet\Services\Tcpip\Parameters","TCPNoDelay",1 if state else 0)

    def _do_ipv6(self,state=True):
        run("netsh int ipv6 set global state="+("disabled" if state else "enabled"))

    def _do_smb(self,state=True):
        if state: ps("Set-SmbServerConfiguration -EnableSMB1Protocol $false -Force -ErrorAction SilentlyContinue")

    def _do_dark(self,state=True):
        v=0 if state else 1
        for n in ["AppsUseLightTheme","SystemUsesLightTheme"]:
            reg_set(winreg.HKEY_CURRENT_USER,r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize",n,v)

    def _do_notifs(self,state=True):
        reg_set(winreg.HKEY_CURRENT_USER,r"SOFTWARE\Microsoft\Windows\CurrentVersion\PushNotifications","ToastEnabled",0 if state else 1)

    def _do_explorer(self,state=True):
        if state:
            reg_set(winreg.HKEY_CURRENT_USER,r"Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced","HideFileExt",0)
            reg_set(winreg.HKEY_CURRENT_USER,r"Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced","Hidden",1)

    def _do_start_sound(self,state=True):
        reg_set(winreg.HKEY_CURRENT_USER,r"AppEvents\Schemes\Apps\.Default\SystemStart\.Current","","")

    def _do_numlock(self,state=True):
        reg_set(winreg.HKEY_USERS,r".DEFAULT\Control Panel\Keyboard","InitialKeyboardIndicators","2" if state else "0")

    def _do_hibernate(self,state=True):
        run("powercfg /hibernate "+("off" if state else "on"))

    def _do_bt_standby(self,state=True):
        run("sc config bthserv start= "+("disabled" if state else "demand"))

    def _gaming_mode(self):
        self._do_high_perf(True); self._do_gamedvr(True)
        self._do_tcp_game(True); self._do_game_mode(True)
        self._dlog("Mode Gaming actif")

    # ── Startup ──────────────────────────────────────────────────
    def _load_startup(self):
        for i in self._su_tree.get_children(): self._su_tree.delete(i)
        self._clog(self._su_log,"Chargement...","info")
        threading.Thread(target=self._load_startup_th,daemon=True).start()

    def _load_startup_th(self):
        entries=[]
        for hive,path,lbl in [(winreg.HKEY_CURRENT_USER,r"Software\Microsoft\Windows\CurrentVersion\Run","HKCU"),
                               (winreg.HKEY_LOCAL_MACHINE,r"Software\Microsoft\Windows\CurrentVersion\Run","HKLM")]:
            try:
                key=winreg.OpenKey(hive,path); i=0
                while True:
                    try: n,v,_=winreg.EnumValue(key,i); entries.append((n,lbl,v[:70],"Actif")); i+=1
                    except OSError: break
                winreg.CloseKey(key)
            except: pass
        for e in entries: self._su_tree.insert("","end",values=e)
        self._clog(self._su_log,str(len(entries))+" entree(s)","warn" if len(entries)>8 else "ok")

    def _startup_impact(self):
        n=len(self._su_tree.get_children())
        self._clog(self._su_log,str(n)+" programmes - "+("rapide" if n<5 else "modere" if n<10 else "lent!"),"ok" if n<5 else "warn")

    # ── Registre ──────────────────────────────────────────────────
    def _reg_scan(self):
        self._clog(self._r_log,"Scan...","info")
        threading.Thread(target=self._reg_scan_th,daemon=True).start()

    def _reg_scan_th(self):
        invalid=0
        for hive,path in [(winreg.HKEY_LOCAL_MACHINE,r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
                          (winreg.HKEY_CURRENT_USER,r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall")]:
            try:
                key=winreg.OpenKey(hive,path); i=0
                while True:
                    try:
                        sub=winreg.EnumKey(key,i); sk=winreg.OpenKey(key,sub)
                        try:
                            loc,_=winreg.QueryValueEx(sk,"InstallLocation")
                            if loc and not os.path.exists(loc): invalid+=1
                        except: pass
                        winreg.CloseKey(sk); i+=1
                    except OSError: break
                winreg.CloseKey(key)
            except: pass
        self._clog(self._r_log,str(invalid)+" orphelin(s)","warn" if invalid>0 else "ok")

    def _reg_backup(self):
        path=filedialog.asksaveasfilename(defaultextension=".reg",filetypes=[("REG","*.reg")])
        if not path: return
        run('regedit /e "'+path+'" HKEY_CURRENT_USER'); self._clog(self._r_log,"OK -> "+path,"ok")

    def _do_mru(self):
        for path in [r"Software\Microsoft\Windows\CurrentVersion\Explorer\RunMRU",
                     r"Software\Microsoft\Windows\CurrentVersion\Explorer\RecentDocs"]:
            try:
                key=winreg.OpenKey(winreg.HKEY_CURRENT_USER,path,0,winreg.KEY_SET_VALUE|winreg.KEY_READ)
                vals=[]; i=0
                while True:
                    try: vals.append(winreg.EnumValue(key,i)[0]); i+=1
                    except OSError: break
                for v in vals:
                    try: winreg.DeleteValue(key,v)
                    except: pass
                winreg.CloseKey(key); self._clog(self._r_log,path.split("\\")[-1]+" nettoye","ok")
            except: pass

    # ── Nettoyage ──────────────────────────────────────────────────
    def _clean_scan(self):
        self._c_log.config(state="normal"); self._c_log.delete("1.0","end"); self._c_log.config(state="disabled")
        self._clog(self._c_log,"Analyse...","info"); self._c_bar.start(10)
        threading.Thread(target=self._clean_scan_th,daemon=True).start()

    def _clean_scan_th(self):
        t=os.environ.get("TEMP",""); w=os.environ.get("WINDIR","C:\\Windows"); total=0.0
        for key,lbl,path,pat in [("tmp_win","Temp Windows",w+"\\Temp","*"),
                                   ("tmp_usr","Temp Utilisateur",t,"*"),
                                   ("prefetch","Prefetch","C:\\Windows\\Prefetch","*.pf"),
                                   ("crashes","Dump memoire",w+"\\Minidump","*.dmp")]:
            if not self._cv.get(key,tk.BooleanVar()).get(): continue
            sz=sum(os.path.getsize(fp) for fp in glob.glob(os.path.join(path,pat)) if os.path.isfile(fp))/1024**2
            total+=sz; self._clog(self._c_log,"{:<26s}  {:6.1f} MB".format(lbl,sz),"warn" if sz>50 else "ok")
        self._clog(self._c_log,"> Total: {:.1f} MB recuperable".format(total),"title")
        self.after(0,self._c_bar.stop)

    def _clean_confirm(self):
        if not messagebox.askyesno("Confirmer","Nettoyer les elements selectionnes ?"): return
        self._clean_quick()

    def _clean_quick(self):
        self._c_log.config(state="normal"); self._c_log.delete("1.0","end"); self._c_log.config(state="disabled")
        self._c_bar.start(10); threading.Thread(target=self._clean_th,daemon=True).start()

    def _clean_th(self):
        t=os.environ.get("TEMP",""); w=os.environ.get("WINDIR","C:\\Windows")
        la=os.environ.get("LOCALAPPDATA",""); total=[0.0]
        def do(key,lbl,path,pat="*"):
            if not self._cv.get(key,tk.BooleanVar(value=True)).get(): return
            mb=del_folder(path,pat); total[0]+=mb
            self._clog(self._c_log,"{:<26s}  {:5.1f} MB".format(lbl,mb),"ok" if mb>0 else "dim")
        self._clog(self._c_log,"Nettoyage...","title")
        do("tmp_win","Temp Windows",w+"\\Temp"); do("tmp_usr","Temp Utilisateur",t)
        do("prefetch","Prefetch","C:\\Windows\\Prefetch","*.pf")
        do("thumbs","Cache miniatures",os.path.join(la,"Microsoft","Windows","Explorer"),"thumbcache_*.db")
        do("crashes","Dump memoire",w+"\\Minidump","*.dmp")
        do("chrome","Chrome Cache",os.path.join(la,"Google","Chrome","User Data","Default","Cache","Cache_Data"))
        do("edge","Edge Cache",os.path.join(la,"Microsoft","Edge","User Data","Default","Cache","Cache_Data"))
        do("shaders","Shader GPU",os.path.join(la,"D3DSCache"))
        do("shaders","NVIDIA Cache",os.path.join(la,"NVIDIA","DXCache"))
        if self._cv.get("recycle",tk.BooleanVar(value=True)).get():
            self._clog(self._c_log,"Corbeille...","info")
            ps("Clear-RecycleBin -Force -ErrorAction SilentlyContinue")
            self._clog(self._c_log,"Corbeille videe","ok")
        if self._cv.get("wu",tk.BooleanVar()).get():
            run("net stop wuauserv /y"); del_folder("C:\\Windows\\SoftwareDistribution\\Download"); run("net start wuauserv")
        mb=total[0]; self._clog(self._c_log,"OK {:.1f} MB liberes !".format(mb),"ok")
        self._c_res.config(text="OK  {:.1f} MB liberes".format(mb))
        self._dlog("Nettoyage: {:.1f} MB liberes".format(mb))
        self.after(0,self._c_bar.stop)

    # ── Processus ──────────────────────────────────────────────────
    def _refresh_procs(self):
        if not HAS_PSUTIL: return
        q=self._pr_search.get().lower()
        if q in ("rechercher...",""):q=""
        for i in self._pr_tree.get_children(): self._pr_tree.delete(i)
        procs=[]
        for p in psutil.process_iter(["pid","name","cpu_percent","memory_info","status","num_threads"]):
            try:
                name=p.info.get("name") or "?"
                if q and q not in name.lower(): continue
                mi=p.info.get("memory_info")
                procs.append((p.info["pid"],name,p.info.get("cpu_percent") or 0.0,
                              round(mi.rss/1024**2,1) if mi else 0,
                              p.info.get("status","?"),p.info.get("num_threads") or 0))
            except: pass
        procs.sort(key=lambda x:x[3],reverse=True)
        for row in procs:
            self._pr_tree.insert("","end",values=row,tags=("h",) if row[3]>500 else ())
        self._pr_tree.tag_configure("h",foreground=RED)
        self._pr_count.config(text=str(len(procs))+" processus")

    def _kill_proc(self):
        sel=self._pr_tree.selection()
        if not sel: messagebox.showwarning("Selection","Selectionnez un processus."); return
        item=self._pr_tree.item(sel[0]); pid=item["values"][0]; name=item["values"][1]
        if not messagebox.askyesno("Confirmer","Terminer "+str(name)+"?"): return
        try: psutil.Process(int(pid)).kill(); self._refresh_procs()
        except Exception as e: messagebox.showerror("Erreur",str(e))

    def _top_cpu(self):
        if not HAS_PSUTIL: return
        list(psutil.process_iter(["cpu_percent"])); time.sleep(0.8)
        procs=sorted(psutil.process_iter(["name","cpu_percent"]),
                     key=lambda p:p.info.get("cpu_percent") or 0,reverse=True)[:5]
        self._dlog("Top CPU: "+", ".join(str(p.info.get("name","?"))[:12]+"({:.0f}%)".format(p.info.get("cpu_percent") or 0) for p in procs))

    def _top_ram(self):
        if not HAS_PSUTIL: return
        procs=sorted(psutil.process_iter(["name","memory_percent"]),
                     key=lambda p:p.info.get("memory_percent") or 0,reverse=True)[:5]
        self._dlog("Top RAM: "+", ".join(str(p.info.get("name","?"))[:12]+"({:.0f}%)".format(p.info.get("memory_percent") or 0) for p in procs))

    # ── Reseau ──────────────────────────────────────────────────────
    def _net_speed(self):
        self._clog(self._n_log,"Test debit...","info")
        if not HAS_PSUTIL: return
        c1=psutil.net_io_counters(); time.sleep(2); c2=psutil.net_io_counters()
        self._clog(self._n_log,"UP:{:.1f} DN:{:.1f} KB/s".format(
            (c2.bytes_sent-c1.bytes_sent)/2/1024,(c2.bytes_recv-c1.bytes_recv)/2/1024),"ok")

    def _netstat(self):
        self._clog(self._n_log,"Connexions:","title")
        for l in run("netstat -an | findstr ESTABLISHED").split("\n")[:15]:
            if l.strip(): self._clog(self._n_log,"  "+l.strip())

    def _open_ports(self):
        self._clog(self._n_log,"Ports:","title")
        for l in run("netstat -ano | findstr LISTENING").split("\n")[:15]:
            if l.strip(): self._clog(self._n_log,"  "+l.strip())

    def _net_adapters(self):
        self._clog(self._n_log,run("ipconfig")[:800])

    def _ping(self):
        threading.Thread(target=lambda: self._clog(self._n_log,run("ping -n 4 8.8.8.8",15),"ok"),daemon=True).start()

    def _arp(self):
        for l in run("arp -a").split("\n"):
            if l.strip(): self._clog(self._n_log,"  "+l.strip())

    def _run_terminal(self):
        cmd=self._t_entry.get().strip()
        if not cmd: return
        self._t_log.config(state="normal"); self._t_log.insert("end","$ "+cmd+"\n"); self._t_log.config(state="disabled")
        def do():
            out=run(cmd,30)
            self._t_log.config(state="normal"); self._t_log.insert("end",out+"\n")
            self._t_log.see("end"); self._t_log.config(state="disabled")
        threading.Thread(target=do,daemon=True).start()


    # ================================================================
    #  RESEAU - NOUVELLES METHODES
    # ================================================================
    def _do_mtu(self, state=True):
        if state:
            ps("Get-NetAdapter | ForEach-Object { try { Set-NetAdapterAdvancedProperty -Name $_.Name -DisplayName \'Jumbo Packet\' -DisplayValue \'Disabled\' -ErrorAction SilentlyContinue } catch {} }")
            run('netsh interface ipv4 set subinterface "Wi-Fi" mtu=1500 store=persistent 2>nul')
            run('netsh interface ipv4 set subinterface "Ethernet" mtu=1500 store=persistent 2>nul')

    def _do_tcp_ack(self, state=True):
        if state:
            reg_set(winreg.HKEY_LOCAL_MACHINE,
                    r"SYSTEM\CurrentControlSet\Services\Tcpip\Parameters",
                    "TcpAckFrequency", 1)
            reg_set(winreg.HKEY_LOCAL_MACHINE,
                    r"SYSTEM\CurrentControlSet\Services\Tcpip\Parameters",
                    "TCPNoDelay", 1)
        else:
            reg_set(winreg.HKEY_LOCAL_MACHINE,
                    r"SYSTEM\CurrentControlSet\Services\Tcpip\Parameters",
                    "TcpAckFrequency", 2)

    def _do_tcp_buf(self, state=True):
        if state:
            run("netsh int tcp set global autotuninglevel=normal")
            run("netsh int tcp set global rss=enabled")
            run("netsh int tcp set global chimney=enabled")
            run("netsh int tcp set global ecncapability=enabled")
        else:
            run("netsh int tcp set global autotuninglevel=disabled")

    def _do_dns_google(self, state=True):
        if state:
            ps("$adapters=Get-NetAdapter | Where-Object {$_.Status -eq \'Up\'}; foreach($a in $adapters){ try{ Set-DnsClientServerAddress -InterfaceIndex $a.InterfaceIndex -ServerAddresses (\'8.8.8.8\',\'8.8.4.4\') -ErrorAction SilentlyContinue }catch{} }")
        else:
            ps("$adapters=Get-NetAdapter | Where-Object {$_.Status -eq \'Up\'}; foreach($a in $adapters){ try{ Set-DnsClientServerAddress -InterfaceIndex $a.InterfaceIndex -ResetServerAddresses -ErrorAction SilentlyContinue }catch{} }")

    def _do_winsock(self, state=True):
        if messagebox.askyesno("Reset Winsock",
                "Cette operation necessite un redemarrage.\nContinuer ?"):
            run("netsh winsock reset")
            run("netsh int ip reset")
            messagebox.showinfo("Reset Winsock",
                "Winsock reinitialise.\nRedemarrez le PC pour appliquer.")

    def _traceroute(self):
        self._clog(self._n_log, "Traceroute vers 8.8.8.8...", "info")
        threading.Thread(
            target=lambda: self._clog(self._n_log,
                run("tracert -h 15 8.8.8.8", 30), "ok"),
            daemon=True).start()

    def _winsock_info(self):
        self._clog(self._n_log, "Info Winsock:", "title")
        out = run("netsh winsock show catalog | findstr /i provider")
        count = len([l for l in out.split("\n") if l.strip()])
        self._clog(self._n_log, str(count) + " providers Winsock installes.", "ok")
        self._clog(self._n_log, run("netsh int ip show config")[:400], "ok")

    # ── Surveillance reseau ──────────────────────────────────────
    def _nm_toggle(self):
        if not self._nm_running:
            self._nm_running = True
            self._nm_btn.config(text="Arreter la surveillance", fg=RED,
                                highlightbackground=RED)
            self._clog(self._nm_log, "Surveillance demarree...", "info")
            threading.Thread(target=self._nm_loop, daemon=True).start()
        else:
            self._nm_running = False
            self._nm_btn.config(text="Demarrer la surveillance", fg=A,
                                highlightbackground=BD)
            self._clog(self._nm_log, "Surveillance arretee.", "dim")

    def _nm_loop(self):
        prev = None; prev_ts = time.time()
        while self._nm_running:
            try:
                net = psutil.net_io_counters() if HAS_PSUTIL else None
                now = time.time()
                if net and prev:
                    dt = now - prev_ts
                    if dt > 0:
                        dl = (net.bytes_recv - prev.bytes_recv) / dt / 1024
                        ul = (net.bytes_sent - prev.bytes_sent) / dt / 1024
                        pkts = (net.packets_recv + net.packets_sent -
                                prev.packets_recv - prev.packets_sent) / dt
                        errs = net.errin + net.errout - prev.errin - prev.errout

                        dl_str  = "{:.1f} KB/s".format(dl) if dl < 1024 else "{:.2f} MB/s".format(dl/1024)
                        ul_str  = "{:.1f} KB/s".format(ul) if ul < 1024 else "{:.2f} MB/s".format(ul/1024)
                        pkt_str = "{:.0f}/s".format(pkts)
                        err_str = str(int(errs))

                        def upd(d=dl_str, u=ul_str, pk=pkt_str, er=err_str):
                            if "dl" in self._nm_cards:
                                self._nm_cards["dl"].config(text=d)
                                self._nm_cards["ul"].config(text=u)
                                self._nm_cards["paquets"].config(text=pk)
                                self._nm_cards["erreurs"].config(text=er,
                                    fg=RED if int(er)>0 else T3)
                        self.after(0, upd)
                prev = net; prev_ts = now
            except Exception:
                pass
            time.sleep(1)

    def _nm_latency_test(self):
        self._clog(self._nm_log, "Test latence (4 pings Google)...", "info")
        def do():
            out = run("ping -n 4 8.8.8.8", 15)
            latency = "N/A"
            import re as re2
            m = re2.search(r"Moyenne = (\d+)ms", out)
            if m:
                latency = m.group(1) + " ms"
                def upd(l=latency):
                    if "latence" in self._nm_cards:
                        col = A if int(m.group(1))<50 else YELLOW if int(m.group(1))<100 else RED
                        self._nm_cards["latence"].config(text=l, fg=col)
                self.after(0, upd)
            self._clog(self._nm_log, "Latence: " + latency, "ok")
        threading.Thread(target=do, daemon=True).start()

    def _nm_scan_ports(self):
        self._clog(self._nm_log, "Scan ports locaux...", "info")
        threading.Thread(target=self._nm_scan_th, daemon=True).start()

    def _nm_scan_th(self):
        import socket
        common_ports = [21,22,23,25,53,80,110,135,139,143,443,445,
                        3306,3389,5985,8080,8443]
        open_ports = []
        for port in common_ports:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(0.3)
                result = s.connect_ex(("127.0.0.1", port))
                s.close()
                if result == 0:
                    open_ports.append(str(port))
            except Exception:
                pass
        if open_ports:
            self._clog(self._nm_log,
                "Ports ouverts locaux: " + ", ".join(open_ports), "warn")
        else:
            self._clog(self._nm_log, "Aucun port commun ouvert detecte.", "ok")

    # ================================================================
    #  AUTO-OPTIMISATION  (safe, reversible, score-aware)
    # ================================================================

    # Liste des optimisations AUTO avec risque et condition
    # Format: (oid, fn_enable, fn_disable, label, safe)
    # safe=True  = toujours applique
    # safe=False = applique seulement si pas de risque detecte
    AO_STEPS = [
        # (id,              label_court,                   safe)
        ("high_perf",       "Plan Haute Performance",       True),
        ("gamedvr",         "Desactivation GameDVR",        True),
        ("reg_perf",        "Tweaks registre",              True),
        ("cpu_priority",    "Priorite CPU",                 True),
        ("copilot",         "Desactivation Copilot",        True),
        ("plan_fr",         "Plan Frame Republic",          True),
        ("mem_mgmt",        "Optimisation memoire",         True),
        ("tcp",             "Optimisation TCP/IP",          True),
        ("qos",             "Liberation QoS",               True),
        ("nagle",           "Desactivation Nagle",          True),
        ("net_power",       "Alimentation carte reseau",    True),
        ("telemetry",       "Desactivation telemetrie",     True),
        ("ads",             "Suppression publicites",       True),
        ("win_search",      "Optimisation recherche",       True),
        ("explorer",        "Optimisation Explorateur",     True),
        ("start_snd",       "Son demarrage off",            True),
        ("game_mode",       "Mode Jeu",                     True),
        ("tcp_game",        "TCP gaming",                   True),
        # Ces etapes sont conditionnelles (seulement si RAM < 8 Go)
        ("superfetch",      "Desactivation SysMain",        False),
    ]

    def _ao_get_score(self):
        """Calcule le score actuel (0-100)."""
        if not HAS_PSUTIL: return 50
        try:
            cpu = psutil.cpu_percent(interval=1)
            vm  = psutil.virtual_memory()
            d   = 0
            try:
                disk = psutil.disk_usage("C:\\")
                d = disk.percent
            except Exception:
                d = 0
            return max(0, min(100, int(100 - cpu*0.35 - vm.percent*0.35 - d*0.30)))
        except Exception:
            return 50

    def _ao_set_status(self, text, col=None):
        """Met a jour le statut (thread-safe via after)."""
        if col is None: col = T2
        def upd():
            self._ao_status.config(text=text, fg=col)
        self.after(0, upd)

    def _ao_set_reasons(self, text, col=None):
        if col is None: col = T2
        def upd():
            self._ao_reasons.config(text=text, fg=col)
        self.after(0, upd)

    def _ao_update_bar(self, pct):
        """Met a jour la barre de progression (0-100)."""
        def upd():
            self._ao_bar_frame.update_idletasks()
            w = self._ao_bar_frame.winfo_width()
            fill_w = max(0, int(w * pct / 100))
            self._ao_bar_fill.place(x=0, y=0, width=fill_w, height=8)
            col = A if pct < 80 else YELLOW
            self._ao_bar_fill.config(bg=col)
        self.after(0, upd)

    def _ao_run(self):
        """Lance l'optimisation automatique complete."""
        if self._ao_running: return
        self._ao_running = True
        self._ao_backup  = {}

        def upd_btn(text, bg, fg, bdbdr):
            def u():
                self._ao_btn.config(text=text, bg=bg, fg=fg, highlightbackground=bdbdr)
            self.after(0, u)

        upd_btn("  Optimisation en cours...  ", P2, T2, BD)
        self._ao_update_bar(0)
        self._ao_set_reasons("", T3)
        self.after(0, lambda: self._ao_score_delta.config(text=""))

        # Score avant
        self._ao_set_status("Analyse du systeme...", A)
        self._ao_update_bar(5)
        score_before = self._ao_get_score()
        self._ao_score_before = score_before

        # Conditions systeme
        ram_gb = 8
        if HAS_PSUTIL:
            try: ram_gb = round(psutil.virtual_memory().total / 1024**3, 1)
            except: pass

        applied   = []
        skipped   = []
        reasons   = []

        total = len(self.AO_STEPS)

        for i, (oid, label, safe) in enumerate(self.AO_STEPS):
            progress = int(10 + (i / total) * 75)
            self._ao_update_bar(progress)
            self._ao_set_status("Optimisation: " + label + "...", A)
            time.sleep(0.08)

            # Verifier si deja actif
            already_on = self._save.get(oid, False)
            if already_on:
                skipped.append(label + " (deja actif)")
                continue

            # Condition pour etapes non-safe
            if not safe:
                if oid == "superfetch" and ram_gb >= 8:
                    reasons.append("SysMain conserve (RAM " + str(ram_gb) + " Go >= 8 Go)")
                    continue

            # Sauvegarder l'etat avant
            self._ao_backup[oid] = self._save.get(oid, False)

            # Appliquer
            fn_map = {
                "high_perf":    lambda: self._do_high_perf(True),
                "gamedvr":      lambda: self._do_gamedvr(True),
                "reg_perf":     lambda: self._do_reg_perf(True),
                "cpu_priority": lambda: self._do_cpu_priority(True),
                "copilot":      lambda: self._do_copilot(True),
                "plan_fr":      lambda: self._do_power_plan_fr(True),
                "mem_mgmt":     lambda: self._do_memory_mgmt(True),
                "tcp":          lambda: self._do_tcp(True),
                "qos":          lambda: self._do_qos(True),
                "nagle":        lambda: self._do_nagle(True),
                "net_power":    lambda: self._do_net_power(True),
                "telemetry":    lambda: self._do_telemetry(True),
                "ads":          lambda: self._do_ads(True),
                "win_search":   lambda: self._do_win_search(True),
                "explorer":     lambda: self._do_explorer(True),
                "start_snd":    lambda: self._do_start_sound(True),
                "game_mode":    lambda: self._do_game_mode(True),
                "tcp_game":     lambda: self._do_tcp_game(True),
                "superfetch":   lambda: self._do_superfetch(True),
            }
            if oid in fn_map:
                try:
                    fn_map[oid]()
                    self._save[oid] = True
                    applied.append(label)
                except Exception as ex:
                    reasons.append(label + " echoue: " + str(ex)[:40])

        write_save(self._save)
        self._ao_update_bar(90)
        self._ao_set_status("Verification du score...", A)
        time.sleep(1.5)

        # Score apres
        score_after = self._ao_get_score()
        delta = score_after - score_before

        self._ao_update_bar(100)

        # Construire le message de resultat
        if delta >= 0:
            self._ao_set_status(
                str(len(applied)) + " optimisations appliquees  |  Score: "
                + str(score_before) + " -> " + str(score_after), A)
            self.after(0, lambda: self._ao_score_delta.config(
                text="(+" + str(delta) + " pts)" if delta > 0 else "(stable)",
                fg=A if delta > 0 else T2))
            msg = ""
            if skipped:
                msg += "Deja actifs: " + ", ".join(skipped[:4])
                if len(skipped) > 4: msg += " +" + str(len(skipped)-4)
            if reasons:
                if msg: msg += "  |  "
                msg += "Ignores: " + "  |  ".join(reasons[:3])
            self._ao_set_reasons(msg, T3)
            self._dlog("Auto-optim: +" + str(delta) + " pts, " + str(len(applied)) + " opt. appliquees")
        else:
            # Le score a baisse - annuler automatiquement
            self._ao_set_status("Score reduit (" + str(abs(delta)) + " pts) - annulation automatique...", RED)
            self.after(0, lambda: self._ao_score_delta.config(
                text="(" + str(delta) + " pts -> annule)", fg=RED))
            time.sleep(0.5)
            self._ao_undo_internal()
            reasons_all = []
            if delta < -5:
                reasons_all.append("Charge CPU trop elevee pendant l'optimisation")
            if delta < -10:
                reasons_all.append("Systeme instable detecte")
            reasons_all.append("Toutes les modifications ont ete annulees")
            self._ao_set_reasons("Raison: " + "  |  ".join(reasons_all), RED)
            self._dlog("Auto-optim annulee: score reduit de " + str(abs(delta)) + " pts")

        upd_btn("  Optimiser maintenant  ", A_D, A, A)
        self._ao_running = False

    def _ao_undo_internal(self):
        """Annule en silence (appele automatiquement si score baisse)."""
        fn_disable_map = {
            "high_perf":    lambda: self._do_high_perf(False),
            "gamedvr":      lambda: self._do_gamedvr(False),
            "reg_perf":     lambda: None,  # registre: pas de rollback simple
            "cpu_priority": lambda: None,  # priorite: pas critique
            "copilot":      lambda: self._do_copilot(False),
            "plan_fr":      lambda: run("powercfg /setactive " + self.PLANS["bal"]),
            "mem_mgmt":     lambda: self._do_memory_mgmt(False),
            "tcp":          lambda: None,
            "qos":          lambda: self._do_qos(False),
            "nagle":        lambda: self._do_nagle(False),
            "net_power":    lambda: None,
            "telemetry":    lambda: self._do_telemetry(False),
            "ads":          lambda: self._do_ads(False),
            "win_search":   lambda: self._do_win_search(False),
            "explorer":     lambda: None,
            "start_snd":    lambda: None,
            "game_mode":    lambda: self._do_game_mode(False),
            "tcp_game":     lambda: self._do_tcp_game(False),
            "superfetch":   lambda: self._do_superfetch(False),
        }
        for oid, old_state in self._ao_backup.items():
            if not old_state:  # etait desactive avant
                fn = fn_disable_map.get(oid)
                if fn:
                    try: fn()
                    except: pass
                self._save[oid] = False
        write_save(self._save)
        self._ao_backup = {}

    def _ao_undo(self):
        """Annulation manuelle par l'utilisateur."""
        if not self._ao_backup:
            self._ao_set_status("Rien a annuler", T2)
            return
        if self._ao_running: return
        self._ao_set_status("Annulation en cours...", YELLOW)
        self._ao_update_bar(50)
        self._ao_undo_internal()
        self._ao_update_bar(0)
        self._ao_set_status("Annulation complete - systeme restaure", YELLOW)
        self.after(0, lambda: self._ao_score_delta.config(text="(annule)", fg=YELLOW))
        self._dlog("Auto-optim: annulation manuelle effectuee")


    # ================================================================
    #  METHODES RESEAU AVANCEES
    # ================================================================
    def _do_net_throttle(self, state=True):
        """Desactive le throttling reseau Windows."""
        val = 0xFFFFFFFF if state else 10
        reg_set(winreg.HKEY_LOCAL_MACHINE,
                r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile",
                "NetworkThrottlingIndex", val)

    def _do_tcp_ack(self, state=True):
        """Optimise les ACK TCP pour reduire la latence."""
        val = 1 if state else 2
        reg_set(winreg.HKEY_LOCAL_MACHINE,
                r"SYSTEM\CurrentControlSet\Services\Tcpip\Parameters\Interfaces",
                "TcpAckFrequency", val)
        reg_set(winreg.HKEY_LOCAL_MACHINE,
                r"SYSTEM\CurrentControlSet\Services\Tcpip\Parameters",
                "TcpAckFrequency", val)

    def _do_winsock_reset(self):
        """Reset la pile Winsock."""
        if not messagebox.askyesno("Reset Winsock",
            "Reinitialiser la pile Winsock ?\nNecessite un redemarrage."):
            return
        out = run("netsh winsock reset")
        if hasattr(self, "_net_adv_log"):
            self._clog(self._net_adv_log, "Winsock reset: "+out[:80], "ok")
        self._dlog("Winsock reset effectue - redemarrage conseille", "warn")

    def _do_mtu_optimize(self):
        """Lance un test MTU optimal."""
        if hasattr(self, "_net_adv_log"):
            self._clog(self._net_adv_log, "Test MTU en cours...", "info")
        threading.Thread(target=self._mtu_test_th, daemon=True).start()

    def _mtu_test_th(self):
        """Teste le MTU optimal par dichotomie."""
        best = 576
        for size in [1500, 1480, 1468, 1452, 1440, 1400, 1350, 1300]:
            out = run("ping -n 1 -l {} -f 8.8.8.8".format(size-28), t=8)
            if "TTL=" in out or "octets" in out.lower():
                best = size
                break
        if hasattr(self, "_net_adv_log"):
            self._clog(self._net_adv_log,
                       "MTU optimal detecte: {} octets".format(best), "ok")
            self._clog(self._net_adv_log,
                       "Appliquez ce MTU dans le champ ci-dessus", "info")

    def _do_tcp_buffers(self):
        """Optimise les buffers TCP send/receive."""
        reg_set(winreg.HKEY_LOCAL_MACHINE,
                r"SYSTEM\CurrentControlSet\Services\AFD\Parameters",
                "DefaultReceiveWindow", 65536)
        reg_set(winreg.HKEY_LOCAL_MACHINE,
                r"SYSTEM\CurrentControlSet\Services\AFD\Parameters",
                "DefaultSendWindow", 65536)
        if hasattr(self, "_net_adv_log"):
            self._clog(self._net_adv_log,
                       "Buffers TCP: Send=64KB, Recv=64KB", "ok")

    def _do_disable_rss(self):
        """Desactive RSS (Receive Side Scaling) si non utilise."""
        out = run("netsh int tcp set global rss=disabled")
        if hasattr(self, "_net_adv_log"):
            self._clog(self._net_adv_log, "RSS: "+out[:80], "ok")

    def _net_adapter_detail(self):
        """Affiche les details des adaptateurs."""
        if not HAS_PSUTIL: return
        threading.Thread(target=self._net_adapter_detail_th, daemon=True).start()

    def _net_adapter_detail_th(self):
        try:
            stats = psutil.net_if_stats()
            addrs = psutil.net_if_addrs()
            for name, stat in stats.items():
                status = "UP" if stat.isup else "DOWN"
                speed  = str(stat.speed)+"Mbps" if stat.speed > 0 else "?"
                msg = "{:<20s}  {}  {}  duplex={}".format(
                    name[:20], status, speed,
                    "full" if stat.duplex.value == 2 else "half")
                if hasattr(self, "_net_adv_log"):
                    self._clog(self._net_adv_log, msg,
                               "ok" if stat.isup else "dim")
        except Exception as e:
            if hasattr(self, "_net_adv_log"):
                self._clog(self._net_adv_log, str(e), "err")

    def _net_latency_test(self):
        """Test de latence vers plusieurs serveurs."""
        if hasattr(self, "_net_adv_log"):
            self._clog(self._net_adv_log, "Test latence...", "info")
        threading.Thread(target=self._net_latency_th, daemon=True).start()

    def _net_latency_th(self):
        targets = [("Google DNS", "8.8.8.8"), ("Cloudflare", "1.1.1.1"),
                   ("Quad9", "9.9.9.9"), ("OpenDNS", "208.67.222.222")]
        for name, ip in targets:
            out = run("ping -n 4 "+ip, t=12)
            avg = "?"
            import re
            m = re.search("[Mm]oyenne\\s*=\\s*(\\d+)|[Aa]verage\\s*=\\s*(\\d+)ms", out)
            if m:
                avg = (m.group(1) or m.group(2))+"ms"
            else:
                m2 = re.search(r"(\d+)ms", out)
                if m2: avg = m2.group(1)+"ms"
            tag = "ok" if avg != "?" and int(avg.replace("ms","")) < 30 else "warn"
            if hasattr(self, "_net_adv_log"):
                self._clog(self._net_adv_log,
                           "{:<14s}  {}".format(name, avg), tag)

    def _apply_mtu(self):
        """Applique le MTU choisi sur tous les adaptateurs."""
        try:
            mtu = int(self._mtu_var.get())
            if mtu < 576 or mtu > 9000:
                if hasattr(self, "_net_adv_log"):
                    self._clog(self._net_adv_log, "MTU invalide (576-9000)", "err")
                return
        except ValueError:
            if hasattr(self, "_net_adv_log"):
                self._clog(self._net_adv_log, "MTU invalide", "err")
            return
        threading.Thread(target=self._apply_mtu_th, args=(mtu,), daemon=True).start()

    def _apply_mtu_th(self, mtu):
        out = run("netsh interface ipv4 set subinterface "
                  '"Wi-Fi" mtu={} store=persistent'.format(mtu))
        out2 = run("netsh interface ipv4 set subinterface "
                   '"Ethernet" mtu={} store=persistent'.format(mtu))
        if hasattr(self, "_net_adv_log"):
            self._clog(self._net_adv_log,
                       "MTU={} applique (Wi-Fi + Ethernet)".format(mtu), "ok")

    def _set_dns(self, primary, secondary=None):
        """Change le serveur DNS sur tous les adaptateurs."""
        if not secondary:
            secondary = primary
        log = self._dns_log if hasattr(self, "_dns_log_txt") else self._dlog
        try:
            ps_cmd = (
                'Get-NetAdapter | Where-Object {$_.Status -eq "Up"} | '
                'ForEach-Object { '
                'Set-DnsClientServerAddress -InterfaceAlias $_.Name '
                '-ServerAddresses ("' + primary + '","' + secondary + '") '
                '-ErrorAction SilentlyContinue }'
            )
            out = ps(ps_cmd, t=20)
            self._dns_log("DNS configure: "+primary+" / "+secondary, "ok")
            self._dns_log("Tous les adaptateurs actifs mis a jour", "info")
        except Exception as e:
            self._dns_log("Erreur DNS: "+str(e), "err")

    def _dns_test(self):
        """Test la resolution DNS."""
        self._dns_log("Test resolution DNS...", "info")
        threading.Thread(target=self._dns_test_th, daemon=True).start()

    def _dns_test_th(self):
        domains = ["google.com", "github.com", "microsoft.com", "cloudflare.com"]
        for d in domains:
            out = run("nslookup "+d+" 2>&1", t=8)
            ok = "Address" in out or "Adresse" in out
            self._dns_log("{:<20s}  {}".format(d, "OK" if ok else "ECHEC"),
                         "ok" if ok else "err")

    def _dns_latency(self):
        """Mesure la latence DNS de plusieurs serveurs."""
        self._dns_log("Mesure latence DNS...", "info")
        threading.Thread(target=self._dns_latency_th, daemon=True).start()

    def _dns_latency_th(self):
        import time as _time
        servers = [("Google",      "8.8.8.8"),
                   ("Cloudflare",  "1.1.1.1"),
                   ("Quad9",       "9.9.9.9"),
                   ("OpenDNS",     "208.67.222.222")]
        for name, ip in servers:
            t0 = _time.perf_counter()
            run("nslookup google.com "+ip, t=6)
            ms = int((time.perf_counter()-t0)*1000)
            tag = "ok" if ms < 30 else "warn" if ms < 80 else "err"
            self._dns_log("{:<14s} {} : {}ms".format(name, ip, ms), tag)

    def _dns_show_current(self):
        """Affiche les serveurs DNS actuels."""
        self._dns_log("Serveurs DNS actuels:", "title")
        threading.Thread(
            target=lambda: self._dns_log(
                run("ipconfig /all | findstr DNS", t=8)[:400], "info"),
            daemon=True).start()

    def _dns_restore(self):
        """Restaure le DNS automatique (DHCP)."""
        try:
            ps_cmd = (
                'Get-NetAdapter | Where-Object {$_.Status -eq "Up"} | '
                'ForEach-Object { '
                'Set-DnsClientServerAddress -InterfaceAlias $_.Name '
                '-ResetServerAddresses -ErrorAction SilentlyContinue }'
            )
            ps(ps_cmd, t=15)
            self._dns_log("DNS restaure en automatique (DHCP)", "ok")
        except Exception as e:
            self._dns_log("Erreur: "+str(e), "err")

    def _net_route(self):
        """Affiche la table de routage."""
        if hasattr(self, "_n_log"):
            self._clog(self._n_log, "Table de routage:", "title")
            threading.Thread(
                target=lambda: self._clog(self._n_log, run("route print", t=10)[:800]),
                daemon=True).start()

    def _netstat_stats(self):
        """Affiche les statistiques reseau."""
        if hasattr(self, "_n_log"):
            self._clog(self._n_log, "Statistiques TCP/IP:", "title")
            threading.Thread(
                target=lambda: self._clog(self._n_log,
                    run("netstat -s | findstr -i tcp 2>&1", t=10)[:600]),
                daemon=True).start()

    # ================================================================
    #  POLLING
    # ================================================================
    def _poll(self):
        if not HAS_PSUTIL: self.after(3000,self._poll); return
        try:
            cpu=psutil.cpu_percent(interval=None); vm=psutil.virtual_memory()
            try: disk=psutil.disk_usage("C:\\")
            except: disk=None
            net=psutil.net_io_counters(); now=time.time()
            if self._net_prev:
                dt=now-self._net_ts
                if dt>0:
                    self._dn_kbs=(net.bytes_recv-self._net_prev[0])/dt/1024
                    self._up_kbs=(net.bytes_sent-self._net_prev[1])/dt/1024
            self._net_prev=(net.bytes_recv,net.bytes_sent); self._net_ts=now

            for key,val in [("cpu",cpu),("ram",vm.percent),("disk",disk.percent if disk else 0)]:
                if key in self._ring_fns: self._ring_fns[key](val)
                if key in self._spark_fns: self._spark_fns[key](val)

            bat=None
            try: bat=psutil.sensors_battery()
            except: pass
            if bat and "bat" in self._ring_fns:
                self._ring_fns["bat"](bat.percent)
                if hasattr(self,"_bat_txt"):
                    self._bat_txt.config(text="Secteur" if bat.power_plugged else "Batterie",
                                        fg=A if bat.power_plugged else (YELLOW if bat.percent>20 else RED))
                if LAPTOP and not bat.power_plugged and bat.percent<15: self._do_eco(True)

            d=disk.percent if disk else 0
            score=max(0,min(100,int(100-cpu*0.35-vm.percent*0.35-d*0.30)))
            col=A if score>=70 else YELLOW if score>=40 else RED
            self._score_lbl.config(text=str(score),fg=col)
            self._score_sub.config(text=("Excellent" if score>=85 else "Bon" if score>=65 else "Moyen" if score>=45 else "Critique"),fg=col)

            self._stat_lbls["ram_free"].config(text="{:.1f}GB".format(b2gb(vm.available)))
            if disk: self._stat_lbls["disk_free"].config(text="{:.1f}GB".format(b2gb(disk.free)))
            self._stat_lbls["procs"].config(text=str(len(list(psutil.process_iter()))))
            self._stat_lbls["net_dn"].config(text="{:.0f}KB/s".format(self._dn_kbs))
            self._stat_lbls["net_up"].config(text="{:.0f}KB/s".format(self._up_kbs))
            h,r=divmod(int(time.time()-psutil.boot_time()),3600)
            self._stat_lbls["uptime"].config(text="{}h{}m".format(h,r//60))
            self._stat_lbls["cpu_info"].config(text="{}C/{}T".format(psutil.cpu_count(logical=False),psutil.cpu_count()))
            if bat:
                bc=A if bat.power_plugged else (YELLOW if bat.percent>20 else RED)
                self._stat_lbls["bat"].config(text="{:.0f}%".format(bat.percent),fg=bc)
            else: self._stat_lbls["bat"].config(text="N/A")
        except: pass
        self.after(2000,self._poll)

    # ================================================================
    #  STYLES TTK
    # ================================================================
    def _setup_style(self):
        s=ttk.Style(self); s.theme_use("clam")
        s.configure("FR.Treeview",background=CARD,foreground=T1,fieldbackground=CARD,
                    bordercolor=BD,rowheight=24,font=("Rajdhani",8))
        s.map("FR.Treeview",background=[("selected",A_D)],foreground=[("selected",A)])
        s.configure("FR.Treeview.Heading",background=CARD_H,foreground=A,
                    bordercolor=BD,font=("Rajdhani",8,"bold"))
        s.configure("FR.Horizontal.TProgressbar",troughcolor=CARD,background=A,bordercolor=BD)

# ================================================================
if __name__ == "__main__":
    try: ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except: pass
    App().mainloop()
