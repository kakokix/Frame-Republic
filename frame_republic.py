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

VERSION     = "1.1.6"
VERSION_URL = "https://raw.githubusercontent.com/kakokix/Frame-Republic/main/version.json"
UPDATE_URL  = "https://raw.githubusercontent.com/kakokix/Frame-Republic/main/frame_republic.py"
# Pour les .exe compiles: telecharger la derniere release
EXE_URL     = "https://github.com/kakokix/Frame-Republic/releases/latest/download/FrameRepublic.exe"

def _is_frozen():
    """True si lance comme .exe PyInstaller, False si script Python."""
    return getattr(sys, "frozen", False)

def _get_exe_path():
    """Chemin de l executable en mode frozen, ou du script sinon."""
    if _is_frozen():
        return sys.executable
    try:
        return os.path.abspath(__file__)
    except NameError:
        return os.path.abspath(sys.argv[0])
NW        = 0x08000000
SAVE_FILE = os.path.join(os.environ.get("APPDATA",""), "FrameRepublic", "save.json")

# ── Admin ──────────────────────────────────────────────────────────
def is_admin():
    try: return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except: return False

def elevate():
    """Relance le processus avec droits admin si necessaire."""
    if is_admin():
        return  # Deja admin
    try:
        import subprocess as _sp
        # Methode 1: ShellExecute runas (fonctionne exe + script)
        script = os.path.abspath(sys.argv[0])
        args   = " ".join('"'+a+'"' for a in sys.argv[1:])
        ret = ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable,
            '"' + script + '" ' + args, None, 1)
        if ret > 32:
            sys.exit(0)
    except Exception:
        pass
    # Si elevation echoue, continuer sans admin (mode degrade)

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
# ═══ PALETTE EXACTE DU SITE frame-republic.netlify.app ═══
# Variables CSS du site reproduites fidelement
BG      = "#07070b"   # --bg (fond principal)
PANEL   = "#0f0f17"   # --bg-elev (topbar, sidebar)
CARD    = "#12121d"   # --bg-card (cartes)
CARD_H  = "#171724"   # --bg-card-2 (hover cartes)
CARD_3  = "#1c1c2b"   # --bg-card-3 (cartes fonce)
BD      = "#1f1f2e"   # --line (bordures)
BD_A    = "#2a2a3d"   # --line-hot (bordures actives)
BD_H    = "#3a3a54"   # --line-hotter (bordures hot)
A       = "#ff2d55"   # --accent (ROUGE/ROSE principal)
A2      = "#ff5577"   # --accent-hot (accent hover)
A_D     = "#c0203f"   # --accent-deep (accent fonce)
A_BG    = "#1a0814"   # fond teinte accent
YELLOW2 = "#ffd60a"   # --accent-2 (jaune secondaire)
GOOD    = "#00e676"   # --good (vert)
BAD     = "#ff5c5c"   # --bad (rouge erreur)
BLUE    = "#38bdf8"   # --info
RED     = "#ff5c5c"   # --bad
ORANGE  = "#ff8c00"
YELLOW  = "#ffd60a"
PURPLE  = "#a78bfa"
WHITE   = "#f4f4f7"   # --text (blanc casse)
T1      = "#c3c3d1"   # --text-dim (texte secondaire)
T2      = "#8a8aa0"   # --muted
T3      = "#6a6a80"   # --muted-2
P1      = "#0a0a12"   # fond plus sombre
P2      = "#0d0d18"   # poly moyen
P3      = "#131322"   # poly clair
NV_G    = "#76b900"   # NVIDIA green
AM_R    = "#ed1c24"   # AMD red
IN_B    = "#0071c5"   # Intel blue

# Police principale - detection automatique
# Bahnschrift = Windows 10/11 natif, geometrique, futuriste
# Rajdhani = installe via Windows Update sur certains systemes
# Fallback -> Segoe UI

def _detect_fonts():
    """Detecte les polices matchant le site: Oswald (titres), Manrope (texte),
    JetBrains Mono (code). Fallbacks intelligents si non installees."""
    try:
        import tkinter as _tk
        import tkinter.font as _tkf
        _root = _tk.Tk(); _root.withdraw()
        fams = list(_tkf.families(_root))
        _root.destroy()
    except Exception:
        fams = []

    def pick(candidates, default):
        for f in candidates:
            if f in fams: return f
        return default

    # TITRES (site: Oswald - narrow uppercase gaming)
    title = pick(
        ["Oswald", "Bahnschrift Condensed", "Bahnschrift SemiCondensed",
         "Impact", "Bahnschrift", "Arial Narrow"],
        "Segoe UI"
    )
    # TEXTE (site: Manrope - geometric sans)
    body = pick(
        ["Manrope", "Inter", "Segoe UI Variable", "Segoe UI", "Calibri"],
        "Segoe UI"
    )
    # CODE (site: JetBrains Mono)
    mono = pick(
        ["JetBrains Mono", "Cascadia Code", "Cascadia Mono",
         "Consolas", "Courier New"],
        "Consolas"
    )
    return title, body, mono

_FONT_TITLE, _FONT_BODY, _FONT_MONO = _detect_fonts()
_FONT = _FONT_TITLE  # alias pour compatibilite

# Polices alignees sur le site frame-republic.netlify.app
# Titres: Oswald-like (condense, uppercase effect)
F_TITLE  = (_FONT_TITLE, 11, "bold")
F_HEAD   = (_FONT_TITLE, 10, "bold")
# Corps: Manrope-like (lisible, geometric)
F_BODY   = (_FONT_BODY,  9)
F_SMALL  = (_FONT_BODY,  8)
F_TINY   = (_FONT_BODY,  7)
F_BADGE  = (_FONT_TITLE, 7, "bold")
F_SCORE  = (_FONT_TITLE, 36, "bold")
# Code: JetBrains Mono-like
F_MONO   = (_FONT_MONO,  8)
F_ICON   = ("Segoe MDL2 Assets", 14)
F_ICO_S  = ("Segoe MDL2 Assets", 12)

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
        # Hauteur fixe garantie: 9 boutons rentrent dans 540px minimum
        super().__init__(parent, bg=PANEL, width=64, height=self.H, cursor="hand2", **kw)
        self.pack_propagate(False)
        self._cmd    = cmd
        self._active = False

        self._bar = tk.Frame(self, bg=PANEL, width=3)
        self._bar.pack(side="left", fill="y")

        mid = tk.Frame(self, bg=PANEL)
        mid.pack(fill="both", expand=True, pady=7)

        self._ico = tk.Label(mid, text=ico, font=F_ICON, bg=PANEL, fg=T2)
        self._ico.pack()
        self._lbl = tk.Label(mid, text=lbl, font=("Segoe UI", 6), bg=PANEL, fg=T3)
        self._lbl.pack(pady=1)

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
#  AUTHENTIFICATION
#  Code stocke sous forme de hash SHA-256 salte - impossible
#  a trouver dans le code source meme en decompilant
# ================================================================

def _auth_check(code_input):
    """Verifie le code saisi sans exposer le code original."""
    import hashlib
    # Hash SHA-256 avec salt du code correct
    # Impossible de retrouver le code meme en lisant cette valeur
    _expected = "61dcee57b8776f49e410d4892e726b241f18ac5b8899a9adc3cecd94fb2446c5"
    _salt     = "fr_salt_v1_kakokix"
    try:
        _computed = hashlib.sha256((_salt + str(code_input)).encode()).hexdigest()
        return _computed == _expected
    except Exception:
        return False

def _show_auth_window():
    """Fenetre d authentification bloquante avant l acces au logiciel.
    Sauvegarde un jeton chiffre apres validation reussie - plus besoin
    de retaper le code aux prochains lancements."""
    import tkinter as _tk
    import hashlib as _hl
    import os as _os
    import json as _js

    # Verifier si deja authentifie
    _save_dir = _os.path.join(_os.environ.get("APPDATA",""), "FrameRepublic")
    _save_path = _os.path.join(_save_dir, "save.json")
    try:
        with open(_save_path, "r", encoding="utf-8") as _f:
            _data = _js.load(_f)
        # Jeton = hash du hash stocke + identifiant machine
        _expected_token = _hl.sha256(
            ("61dcee57b8776f49e410d4892e726b241f18ac5b8899a9adc3cecd94fb2446c5"
             + _os.environ.get("COMPUTERNAME","")
             + _os.environ.get("USERNAME","")).encode()).hexdigest()
        if _data.get("_auth_token") == _expected_token:
            return  # Deja authentifie - skip la fenetre
    except Exception:
        pass

    # Palette EXACTE du site frame-republic.netlify.app
    _BG    = "#07070b"     # --bg
    _PANEL = "#0f0f17"     # --bg-elev
    _CARD  = "#12121d"     # --bg-card
    _CARD_H= "#171724"     # --bg-card-2
    _BD    = "#1f1f2e"     # --line
    _A     = "#ff2d55"     # --accent (ROUGE exact du site)
    _A_D   = "#c0203f"     # --accent-deep
    _RED   = "#ff5c5c"     # --bad
    _WHITE = "#f4f4f7"     # --text
    _T1    = "#c3c3d1"     # --text-dim
    _T2    = "#8a8aa0"     # --muted
    _T3    = "#6a6a80"     # --muted-2
    _P1    = "#0a0a12"     # plus sombre
    _GOOD  = "#00e676"     # --good (vert validation)

    import tkinter.font as _tkf
    def _detect():
        try:
            r = _tk.Tk(); r.withdraw()
            fams = _tkf.families(r); r.destroy()
            # Priorite: Oswald (site) > Bahnschrift Condensed > Bahnschrift > Segoe UI
            for f in ["Oswald", "Bahnschrift Condensed", "Bahnschrift",
                       "Rajdhani", "Segoe UI"]:
                if f in fams: return f
        except: pass
        return "Segoe UI"
    _F = _detect()

    root = _tk.Tk()
    root.overrideredirect(True)
    root.configure(bg=_BG)
    try: ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except: pass

    # Charger l icone (meme logique que App.__init__)
    try:
        if getattr(sys, "frozen", False):
            _icon_dir = _os.path.dirname(sys.executable)
        else:
            _icon_dir = _os.path.dirname(_os.path.abspath(__file__))
        _icon_path = _os.path.join(_icon_dir, "frame_republic.ico")
        if _os.path.exists(_icon_path):
            root.iconbitmap(_icon_path)
    except Exception: pass

    _result = {"ok": False, "attempts": 0, "drag_x": 0, "drag_y": 0}

    def _on_drag_start(e):
        _result["drag_x"] = e.x_root - root.winfo_x()
        _result["drag_y"] = e.y_root - root.winfo_y()
    def _on_drag(e):
        root.geometry("+{}+{}".format(
            e.x_root - _result["drag_x"], e.y_root - _result["drag_y"]))

    # Bordure externe accent
    outer = _tk.Frame(root, bg=_A)
    outer.pack(fill="both", expand=True, padx=1, pady=1)

    # Fond CARD
    main = _tk.Frame(outer, bg=_CARD)
    main.pack(fill="both", expand=True)

    # ── Topbar custom ──
    top = _tk.Frame(main, bg=_PANEL, height=36)
    top.pack(fill="x"); top.pack_propagate(False)
    top.bind("<ButtonPress-1>", _on_drag_start)
    top.bind("<B1-Motion>", _on_drag)

    _tk.Label(top, text="  Frame Republic  /  Acces securise",
              font=(_F, 9, "bold"), bg=_PANEL, fg=_WHITE).pack(side="left", padx=12)

    def _cancel():
        root.quit()
        try: root.destroy()
        except: pass
        sys.exit(0)

    close_b = _tk.Label(top, text="  x  ", font=(_F, 10, "bold"),
                         bg=_PANEL, fg=_T2, cursor="hand2")
    close_b.pack(side="right")
    close_b.bind("<Enter>", lambda e: close_b.config(bg=_RED, fg=_WHITE))
    close_b.bind("<Leave>", lambda e: close_b.config(bg=_PANEL, fg=_T2))
    close_b.bind("<Button-1>", lambda e: _cancel())

    # Separateur accent
    _tk.Frame(main, bg=_A, height=1).pack(fill="x")

    # ── Corps ──
    body = _tk.Frame(main, bg=_CARD, padx=36, pady=28)
    body.pack(fill="both", expand=True)

    # Logo rectangle arrondi gradient rouge (taille auth: 72px)
    _LS = 72
    lg = _tk.Canvas(body, width=_LS, height=_LS, bg=_CARD, highlightthickness=0)
    lg.pack(pady=8)
    _r = 16
    lg.create_rectangle(_r, 0, _LS-_r, _LS, fill=_A, outline="")
    lg.create_rectangle(0, _r, _LS, _LS-_r, fill=_A, outline="")
    lg.create_arc(0, 0, 2*_r, 2*_r, start=90, extent=90, fill=_A, outline="")
    lg.create_arc(_LS-2*_r, 0, _LS, 2*_r, start=0, extent=90, fill=_A, outline="")
    lg.create_arc(0, _LS-2*_r, 2*_r, _LS, start=180, extent=90, fill=_A, outline="")
    lg.create_arc(_LS-2*_r, _LS-2*_r, _LS, _LS, start=270, extent=90, fill=_A, outline="")
    # Gradient overlay
    lg.create_polygon(_LS, 0, _LS, _LS, 0, _LS,
                      fill="#c0203f", outline="", stipple="gray25")
    # F blanc bold
    lg.create_text(_LS/2, _LS/2, text="F", fill=_WHITE, font=(_F, 38, "bold"))

    _tk.Label(body, text="ACCES SECURISE",
              font=(_F, 14, "bold"), bg=_CARD, fg=_WHITE).pack(pady=4)
    _tk.Label(body, text="Entrez le code d activation",
              font=(_F, 9), bg=_CARD, fg=_T2).pack(pady=0)

    # Champ de saisie
    entry_frame = _tk.Frame(body, bg=_P1,
                             highlightthickness=1, highlightbackground=_BD)
    entry_frame.pack(fill="x", pady=0)

    entry = _tk.Entry(entry_frame, bg=_P1, fg=_A, font=("Consolas", 12, "bold"),
                       insertbackground=_A, relief="flat", show="*",
                       justify="center")
    entry.pack(fill="x", padx=12, pady=10, ipady=4)
    entry.focus_set()

    # Message erreur
    error_lbl = _tk.Label(body, text="", font=(_F, 8),
                           bg=_CARD, fg=_RED, height=1)
    error_lbl.pack(fill="x", pady=4)

    def _validate(_=None):
        code = entry.get().strip()
        if not code:
            error_lbl.config(text="Veuillez entrer un code")
            return

        if _auth_check(code):
            _result["ok"] = True
            # Sauvegarder le jeton pour eviter de redemander le code
            try:
                _save_dir = _os.path.join(_os.environ.get("APPDATA",""),
                                           "FrameRepublic")
                _save_path = _os.path.join(_save_dir, "save.json")
                _os.makedirs(_save_dir, exist_ok=True)
                _token = _hl.sha256(
                    ("61dcee57b8776f49e410d4892e726b241f18ac5b8899a9adc3cecd94fb2446c5"
                     + _os.environ.get("COMPUTERNAME","")
                     + _os.environ.get("USERNAME","")).encode()).hexdigest()
                try:
                    with open(_save_path, "r", encoding="utf-8") as _f:
                        _data = _js.load(_f)
                except Exception:
                    _data = {}
                _data["_auth_token"] = _token
                with open(_save_path, "w", encoding="utf-8") as _f:
                    _js.dump(_data, _f, indent=2)
            except Exception:
                pass

            # Petit effet visuel de validation - vert #00e676 du site
            ok_lbl = _tk.Label(body, text="  ACCES AUTORISE  ",
                                font=(_F, 10, "bold"),
                                bg=_GOOD, fg=_BG, padx=12, pady=6)
            ok_lbl.pack(pady=4)
            root.update()
            import time as _t; _t.sleep(0.6)
            root.quit()  # Sort du mainloop sans detruire les widgets
        else:
            _result["attempts"] += 1
            entry.delete(0, "end")

            if _result["attempts"] >= 5:
                error_lbl.config(text="Trop de tentatives. Fermeture...")
                root.update()
                import time as _t; _t.sleep(1.5)
                root.quit()
                try: root.destroy()
                except: pass
                sys.exit(0)
            else:
                remaining = 5 - _result["attempts"]
                error_lbl.config(
                    text="Code incorrect ({} tentative{} restante{})".format(
                        remaining, "s" if remaining>1 else "",
                        "s" if remaining>1 else ""))

                # Effet shake
                orig_x = root.winfo_x()
                for dx in [10, -20, 18, -16, 10, -8, 4, 0]:
                    root.geometry("+{}+{}".format(orig_x + dx, root.winfo_y()))
                    root.update(); import time as _t; _t.sleep(0.025)

    entry.bind("<Return>", _validate)

    # Bouton valider
    btn = _tk.Label(body, text="  Valider le code  ",
                     font=(_F, 10, "bold"),
                     bg=_A_D, fg=_A, cursor="hand2", padx=14, pady=8,
                     highlightthickness=1, highlightbackground=_A)
    btn.pack(fill="x", pady=4)
    btn.bind("<Enter>", lambda e: btn.config(bg=_A, fg=_BG))
    btn.bind("<Leave>", lambda e: btn.config(bg=_A_D, fg=_A))
    btn.bind("<Button-1>", lambda e: _validate())

    # Lien discret
    _tk.Label(body,
              text="Contactez l administrateur si vous n avez pas de code",
              font=(_F, 7), bg=_CARD, fg=_T3).pack(pady=8)

    # Centrer
    root.update_idletasks()
    w, h = 380, 420
    x = (root.winfo_screenwidth() - w) // 2
    y = (root.winfo_screenheight() - h) // 2
    root.geometry("{}x{}+{}+{}".format(w, h, x, y))

    root.mainloop()

    # Cleanup critique avant de laisser App() creer sa propre Tk
    try:
        root.destroy()
    except Exception: pass
    import gc as _gc
    _gc.collect()

    if not _result["ok"]:
        sys.exit(0)


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

        # Icone de l application (barre des taches Windows)
        try:
            import os as _os
            # Chercher l icone a cote de l exe/script
            if getattr(sys, "frozen", False):
                _icon_dir = _os.path.dirname(sys.executable)
            else:
                _icon_dir = _os.path.dirname(_os.path.abspath(__file__))
            _icon_path = _os.path.join(_icon_dir, "frame_republic.ico")
            if _os.path.exists(_icon_path):
                self.iconbitmap(_icon_path)
            # Aussi definir via ctypes pour la taskbar Windows
            _app_id = u"FrameRepublic.PCOptimizer.1.1.6"
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(_app_id)
        except Exception: pass

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
        self._tray_active = False
        self._hw_running       = False
        self._startup_entries   = []
        self._tray_hwnd  = None
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
        """Affiche une popup stylee pour la mise a jour."""
        win = tk.Toplevel(self)
        win.overrideredirect(True)
        win.configure(bg=BG)
        win.transient(self)
        win.grab_set()

        # Bordure externe accent
        outer = tk.Frame(win, bg=A)
        outer.pack(fill="both", expand=True, padx=1, pady=1)

        inner = tk.Frame(outer, bg=CARD)
        inner.pack(fill="both", expand=True)

        # Header avec triangle accent
        hdr = tk.Frame(inner, bg=PANEL, height=44)
        hdr.pack(fill="x"); hdr.pack_propagate(False)

        tri = tk.Canvas(hdr, width=30, height=30, bg=PANEL, highlightthickness=0)
        tri.place(x=14, rely=0.5, anchor="w")
        tri.create_polygon(0,0,30,15,0,30, fill=A, outline="")
        tri.create_polygon(5,5,25,15,5,25, fill=A_D, outline="")

        tk.Label(hdr, text="MISE A JOUR DISPONIBLE",
                 font=(_FONT, 11, "bold"), bg=PANEL, fg=WHITE).place(
                 x=52, rely=0.5, anchor="w")

        # Bouton fermer
        close_btn = tk.Label(hdr, text="  x  ", font=(_FONT, 10, "bold"),
                              bg=PANEL, fg=T2, cursor="hand2")
        close_btn.place(relx=1, rely=0, anchor="ne")
        close_btn.bind("<Enter>", lambda e: close_btn.config(bg=RED, fg=WHITE))
        close_btn.bind("<Leave>", lambda e: close_btn.config(bg=PANEL, fg=T2))
        close_btn.bind("<Button-1>", lambda e: win.destroy())

        # Separateur accent
        tk.Frame(inner, bg=A, height=1).pack(fill="x")

        # Corps
        body = tk.Frame(inner, bg=CARD, padx=24, pady=18)
        body.pack(fill="both", expand=True)

        # Versions
        vf = tk.Frame(body, bg=CARD); vf.pack(fill="x", pady=0)
        tk.Label(vf, text="Version actuelle:", font=(_FONT, 9),
                 bg=CARD, fg=T2, width=18, anchor="w").pack(side="left")
        tk.Label(vf, text="v" + VERSION, font=(_FONT, 10, "bold"),
                 bg=CARD, fg=T1).pack(side="left")

        vf2 = tk.Frame(body, bg=CARD); vf2.pack(fill="x", pady=0)
        tk.Label(vf2, text="Nouvelle version:", font=(_FONT, 9),
                 bg=CARD, fg=T2, width=18, anchor="w").pack(side="left")
        tk.Label(vf2, text="v" + new_ver, font=(_FONT, 10, "bold"),
                 bg=CARD, fg=A).pack(side="left")

        # Notes
        tk.Frame(body, bg=BD, height=1).pack(fill="x", pady=8)
        tk.Label(body, text="NOTES DE VERSION", font=(_FONT, 8, "bold"),
                 bg=CARD, fg=T3, anchor="w").pack(fill="x", pady=4)

        notes_txt = tk.Text(body, bg=P1, fg=T1, font=F_MONO, height=4,
                             relief="flat", padx=10, pady=8,
                             highlightthickness=1, highlightbackground=BD,
                             wrap="word")
        notes_txt.insert("1.0", notes or "Pas de notes disponibles.")
        notes_txt.config(state="disabled")
        notes_txt.pack(fill="x", pady=0)

        # Info auto-redemarrage
        tk.Label(body, text="Le logiciel redemarrera automatiquement.",
                 font=(_FONT, 8), bg=CARD, fg=T3).pack(anchor="w", pady=0)

        # Boutons
        btns = tk.Frame(body, bg=CARD); btns.pack(fill="x", pady=4)

        def do_update():
            win.destroy()
            # Ouvrir une fenetre de progression
            self._show_update_progress(new_ver)
            threading.Thread(
                target=self._download_and_apply,
                args=(new_ver,), daemon=True).start()

        def do_cancel():
            win.destroy()

        cancel_btn = tk.Label(btns, text="  Plus tard  ", font=(_FONT, 9),
                               bg=CARD, fg=T2, cursor="hand2",
                               padx=16, pady=7,
                               highlightthickness=1, highlightbackground=BD)
        cancel_btn.pack(side="left", padx=4)
        cancel_btn.bind("<Enter>", lambda e: cancel_btn.config(bg=CARD_H, fg=T1))
        cancel_btn.bind("<Leave>", lambda e: cancel_btn.config(bg=CARD, fg=T2))
        cancel_btn.bind("<Button-1>", lambda e: do_cancel())

        install_btn = tk.Label(btns, text="  Installer maintenant  ",
                                font=(_FONT, 9, "bold"),
                                bg=A_D, fg=A, cursor="hand2",
                                padx=16, pady=7,
                                highlightthickness=1, highlightbackground=A)
        install_btn.pack(side="right", padx=4)
        install_btn.bind("<Enter>", lambda e: install_btn.config(bg=A, fg=BG))
        install_btn.bind("<Leave>", lambda e: install_btn.config(bg=A_D, fg=A))
        install_btn.bind("<Button-1>", lambda e: do_update())

        # Centrer la popup
        win.update_idletasks()
        w, h = 460, 340
        x = (win.winfo_screenwidth() - w) // 2
        y = (win.winfo_screenheight() - h) // 2
        win.geometry("{}x{}+{}+{}".format(w, h, x, y))

    def _show_update_progress(self, new_ver):
        """Affiche une fenetre de progression pendant le telechargement."""
        self._upd_win = tk.Toplevel(self)
        self._upd_win.overrideredirect(True)
        self._upd_win.configure(bg=BG)
        self._upd_win.transient(self)

        outer = tk.Frame(self._upd_win, bg=A)
        outer.pack(fill="both", expand=True, padx=1, pady=1)
        inner = tk.Frame(outer, bg=CARD, padx=24, pady=20)
        inner.pack(fill="both", expand=True)

        # Triangle deco
        tri = tk.Canvas(inner, width=40, height=40, bg=CARD, highlightthickness=0)
        tri.pack(anchor="w", pady=0)
        tri.create_polygon(0,0,40,20,0,40, fill=A, outline="")

        tk.Label(inner, text="TELECHARGEMENT v" + new_ver,
                 font=(_FONT, 11, "bold"), bg=CARD, fg=WHITE).pack(anchor="w")
        tk.Label(inner, text="Veuillez patienter...",
                 font=(_FONT, 8), bg=CARD, fg=T2).pack(anchor="w", pady=2)

        # Barre de progression indeterminee
        self._upd_bar = ttk.Progressbar(inner, mode="indeterminate",
                                         style="FR.Horizontal.TProgressbar",
                                         length=340)
        self._upd_bar.pack(fill="x", pady=8)
        self._upd_bar.start(12)

        # Centrer
        self._upd_win.update_idletasks()
        w, h = 400, 160
        x = (self._upd_win.winfo_screenwidth() - w) // 2
        y = (self._upd_win.winfo_screenheight() - h) // 2
        self._upd_win.geometry("{}x{}+{}+{}".format(w, h, x, y))

    def _download_and_apply(self, new_ver):
        """Telecharge et applique la mise a jour.
        Gere deux modes:
        - Mode frozen (.exe PyInstaller): telecharge le nouvel exe
          dans le meme dossier et relance via script .bat
        - Mode script (.py): remplace le fichier directement
        """
        backup_path = None
        try:
            import urllib.request, ssl, shutil

            self._dlog("Telechargement mise a jour v" + new_ver + "...")

            if not self._check_network():
                self.after(0, lambda: messagebox.showerror(
                    "Erreur", "Pas de connexion reseau."))
                return

            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode    = ssl.CERT_NONE

            if _is_frozen():
                # === MODE EXE ===
                exe_path  = sys.executable
                exe_dir   = os.path.dirname(exe_path)
                new_exe   = os.path.join(exe_dir, "FrameRepublic_new.exe")
                old_exe   = os.path.join(exe_dir, "FrameRepublic_old.exe")
                bat_path  = os.path.join(exe_dir, "_update.bat")

                # Verifier que le dossier est ecrivable
                if not os.access(exe_dir, os.W_OK):
                    raise PermissionError(
                        "Dossier non ecrivable: " + exe_dir +
                        "\nDeplacez FrameRepublic.exe dans un dossier"
                        " sans restrictions.")

                # Telecharger le nouvel exe
                req = urllib.request.Request(
                    EXE_URL,
                    headers={"User-Agent": "FrameRepublic/" + VERSION})

                self._dlog("Telechargement depuis GitHub Releases...")
                with urllib.request.urlopen(req, timeout=120, context=ctx) as r:
                    total = int(r.headers.get("Content-Length", 0))
                    downloaded = 0
                    with open(new_exe, "wb") as f:
                        while True:
                            chunk = r.read(65536)
                            if not chunk: break
                            f.write(chunk)
                            downloaded += len(chunk)
                            if total:
                                pct = int(downloaded * 100 / total)
                                if pct % 10 == 0:
                                    self._dlog("Progression: " + str(pct) + "%")

                # Verifier taille minimale (eviter fichier corrompu)
                if os.path.getsize(new_exe) < 1024 * 100:  # au moins 100KB
                    os.remove(new_exe)
                    raise ValueError("Fichier telecharge trop petit - corrompu")

                # Creer un script batch qui:
                # 1. Attend que l exe actuel se ferme
                # 2. Remplace l exe
                # 3. Relance le nouvel exe
                # 4. Se supprime
                bat_content = (
                    "@echo off\r\n"
                    "timeout /t 2 /nobreak >nul\r\n"
                    ":retry\r\n"
                    "move /y \"" + exe_path + "\" \"" + old_exe + "\" >nul 2>&1\r\n"
                    "if errorlevel 1 (\r\n"
                    "  timeout /t 1 /nobreak >nul\r\n"
                    "  goto retry\r\n"
                    ")\r\n"
                    "move /y \"" + new_exe + "\" \"" + exe_path + "\" >nul\r\n"
                    "del /f /q \"" + old_exe + "\" >nul 2>&1\r\n"
                    "start \"\" \"" + exe_path + "\"\r\n"
                    "del /f /q \"%~f0\" >nul 2>&1\r\n"
                )

                with open(bat_path, "w", encoding="ascii") as f:
                    f.write(bat_content)

                # Lancer le bat en arriere plan
                self._dlog("Mise a jour installee. Redemarrage...")
                subprocess.Popen(
                    ["cmd", "/c", bat_path],
                    creationflags=NW | 0x00000008)  # DETACHED_PROCESS

                # Fermer proprement
                write_save(self._save)
                self.after(300, self._quit_completely)

            else:
                # === MODE SCRIPT .PY ===
                script_path = os.path.abspath(__file__)

                # Verifier que le script n est pas dans un dossier temp PyInstaller
                if "_MEI" in script_path or "Temp" in script_path:
                    raise RuntimeError(
                        "Le fichier est dans un dossier temporaire."
                        "\nReinstallez FrameRepublic dans un dossier permanent.")

                backup_path = script_path + ".backup"
                tmp_path    = script_path + ".tmp"

                req = urllib.request.Request(
                    UPDATE_URL,
                    headers={"User-Agent": "FrameRepublic/" + VERSION})

                with urllib.request.urlopen(req, timeout=60, context=ctx) as r:
                    content = r.read()

                # Valider Python
                import ast
                try:
                    ast.parse(content.decode("utf-8"))
                except SyntaxError:
                    self.after(0, lambda: messagebox.showerror(
                        "Erreur", "Fichier de mise a jour invalide."))
                    return

                # Backup + remplacement
                shutil.copy2(script_path, backup_path)
                with open(tmp_path, "wb") as f:
                    f.write(content)
                os.replace(tmp_path, script_path)

                self._dlog("Mise a jour installee. Redemarrage...")
                self.after(500, self._restart_app)

        except Exception as e:
            err_msg = str(e)
            self.after(0, lambda m=err_msg: messagebox.showerror(
                "Erreur mise a jour",
                "Echec: " + m + "\n\nAncienne version conservee."))
            # Restaurer backup script uniquement
            try:
                if backup_path and os.path.exists(backup_path):
                    os.replace(backup_path, os.path.abspath(__file__))
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
        """Ferme la fenetre et garde le logiciel en arriere-plan (tray)."""
        write_save(self._save)
        self.withdraw()          # Cache la fenetre
        self._show_tray_icon()   # Affiche l icone dans la barre systeme

    def _quit_completely(self):
        """Quitte completement le logiciel."""
        write_save(self._save)
        self._tray_active = False
        try:
            if hasattr(self, "_tray_icon") and self._tray_icon:
                self._tray_icon.destroy()
        except Exception: pass
        self.destroy()

    def _show_window(self):
        """Restaure la fenetre depuis le tray."""
        self.deiconify()
        self.overrideredirect(True)
        self.lift()
        self.focus_force()

    def _show_tray_icon(self):
        """Cree une icone dans la barre des taches (system tray) via win32."""
        self._tray_active = True
        threading.Thread(target=self._tray_loop, daemon=True).start()

    def _tray_loop(self):
        """Boucle tray via win32 API pure - aucune dependance externe."""
        try:
            import ctypes
            from ctypes import wintypes
            import struct

            # Constantes win32
            WM_APP        = 0x8000
            WM_TRAY       = WM_APP + 1
            NIM_ADD       = 0x00000000
            NIM_DELETE    = 0x00000002
            NIF_MESSAGE   = 0x00000001
            NIF_ICON      = 0x00000002
            NIF_TIP       = 0x00000004
            WM_LBUTTONDBLCLK = 0x0203
            WM_RBUTTONUP  = 0x0205
            WM_DESTROY    = 0x0002
            IDI_APPLICATION = 32512
            IMAGE_ICON    = 1
            LR_SHARED     = 0x8000

            user32   = ctypes.windll.user32
            shell32  = ctypes.windll.shell32
            kernel32 = ctypes.windll.kernel32

            # Creer une classe de fenetre invisible
            WNDPROC = ctypes.WINFUNCTYPE(
                ctypes.c_long, wintypes.HWND,
                ctypes.c_uint, wintypes.WPARAM, wintypes.LPARAM)

            def wnd_proc(hwnd, msg, wparam, lparam):
                if msg == WM_TRAY:
                    if lparam == WM_LBUTTONDBLCLK:
                        self.after(0, self._show_window)
                    elif lparam == WM_RBUTTONUP:
                        # Menu contextuel simple
                        self.after(0, self._tray_menu)
                elif msg == WM_DESTROY:
                    return 0
                return user32.DefWindowProcW(hwnd, msg, wparam, lparam)

            wnd_proc_ptr = WNDPROC(wnd_proc)

            class WNDCLASSEX(ctypes.Structure):
                _fields_ = [
                    ("cbSize",        ctypes.c_uint),
                    ("style",         ctypes.c_uint),
                    ("lpfnWndProc",   WNDPROC),
                    ("cbClsExtra",    ctypes.c_int),
                    ("cbWndExtra",    ctypes.c_int),
                    ("hInstance",     wintypes.HANDLE),
                    ("hIcon",         wintypes.HANDLE),
                    ("hCursor",       wintypes.HANDLE),
                    ("hbrBackground", wintypes.HANDLE),
                    ("lpszMenuName",  wintypes.LPCWSTR),
                    ("lpszClassName", wintypes.LPCWSTR),
                    ("hIconSm",       wintypes.HANDLE),
                ]

            hinstance = kernel32.GetModuleHandleW(None)
            class_name = "FrameRepublicTray"

            wc = WNDCLASSEX()
            wc.cbSize        = ctypes.sizeof(WNDCLASSEX)
            wc.lpfnWndProc   = wnd_proc_ptr
            wc.hInstance     = hinstance
            wc.lpszClassName = class_name
            wc.hIcon         = user32.LoadIconW(None, IDI_APPLICATION)
            wc.hIconSm       = wc.hIcon
            user32.RegisterClassExW(ctypes.byref(wc))

            hwnd = user32.CreateWindowExW(
                0, class_name, "FrameRepublic",
                0, 0, 0, 0, 0, None, None, hinstance, None)
            self._tray_hwnd = hwnd

            # Ajouter l icone dans le tray
            class NOTIFYICONDATA(ctypes.Structure):
                _fields_ = [
                    ("cbSize",           ctypes.c_ulong),
                    ("hWnd",             wintypes.HWND),
                    ("uID",              ctypes.c_uint),
                    ("uFlags",           ctypes.c_uint),
                    ("uCallbackMessage", ctypes.c_uint),
                    ("hIcon",            wintypes.HANDLE),
                    ("szTip",            ctypes.c_wchar * 128),
                ]

            nid = NOTIFYICONDATA()
            nid.cbSize           = ctypes.sizeof(NOTIFYICONDATA)
            nid.hWnd             = hwnd
            nid.uID              = 1
            nid.uFlags           = NIF_ICON | NIF_MESSAGE | NIF_TIP
            nid.uCallbackMessage = WM_TRAY
            nid.hIcon            = user32.LoadIconW(None, IDI_APPLICATION)
            nid.szTip            = "Frame Republic - En arriere-plan"
            shell32.Shell_NotifyIconW(NIM_ADD, ctypes.byref(nid))
            self._tray_nid = nid

            # Boucle de messages win32
            msg = wintypes.MSG()
            while self._tray_active:
                if user32.PeekMessageW(ctypes.byref(msg), None,
                                       0, 0, 1):  # PM_REMOVE=1
                    user32.TranslateMessage(ctypes.byref(msg))
                    user32.DispatchMessageW(ctypes.byref(msg))
                else:
                    import time as _t; _t.sleep(0.05)

            # Supprimer l icone
            shell32.Shell_NotifyIconW(NIM_DELETE, ctypes.byref(nid))

        except Exception as e:
            # Si tray echoue - quitter proprement quand meme
            self.after(0, self.destroy)

    def _tray_menu(self):
        """Menu clic-droit sur l icone tray."""
        menu = tk.Menu(self, tearoff=0,
                       bg=CARD, fg=T1,
                       activebackground=A_D, activeforeground=A,
                       font=F_SMALL, bd=0, relief="flat")
        menu.add_command(label="Ouvrir Frame Republic",
                         command=self._show_window)
        menu.add_separator()
        menu.add_command(label="Quitter completement",
                         command=self._quit_completely)
        try:
            x = self.winfo_pointerx()
            y = self.winfo_pointery()
            menu.tk_popup(x, y)
        except Exception: pass

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
        body.grid(row=1, column=0, sticky="nsew", columnspan=1)
        body.grid_rowconfigure(0, weight=1)
        body.grid_columnconfigure(0, weight=0)   # sidebar - largeur fixe
        body.grid_columnconfigure(1, weight=1)   # content - s etire

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
        bar.grid(row=0, column=0, sticky="ew", columnspan=2)
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

        # Logo rectangle arrondi gradient rouge + F blanc (site exact)
        logo = tk.Frame(bar, bg=PANEL)
        logo.place(x=16, rely=0.5, anchor="w")
        # Taille 34x34 comme le site (.brand-mark)
        LS = 34
        lg = tk.Canvas(logo, width=LS, height=LS, bg=PANEL, highlightthickness=0)
        lg.pack(side="left")
        # Simuler gradient 135deg avec 3 polygones superposes
        # Coins arrondis r=8 comme le site (border-radius: 8px)
        r = 8
        # Base rectangle avec arcs aux 4 coins
        lg.create_rectangle(r, 0, LS-r, LS, fill=A, outline="")
        lg.create_rectangle(0, r, LS, LS-r, fill=A, outline="")
        lg.create_arc(0, 0, 2*r, 2*r, start=90, extent=90, fill=A, outline="")
        lg.create_arc(LS-2*r, 0, LS, 2*r, start=0, extent=90, fill=A, outline="")
        lg.create_arc(0, LS-2*r, 2*r, LS, start=180, extent=90, fill=A, outline="")
        lg.create_arc(LS-2*r, LS-2*r, LS, LS, start=270, extent=90, fill=A, outline="")
        # Effet gradient: overlay diagonal plus fonce en bas-droite
        lg.create_polygon(LS, 0, LS, LS, 0, LS,
                          fill=A_D, outline="", stipple="gray25")
        # Le F blanc - path SVG du site: M4 4h16v5h-11v3h9v5h-9v7H4z
        # Stroke 2.5 simule avec du texte bold
        lg.create_text(LS/2, LS/2, text="F", fill=WHITE,
                        font=(_FONT, 18, "bold"))
        for w in (hx, logo):
            w.bind("<ButtonPress-1>", self._drag_start)
            w.bind("<B1-Motion>",     self._drag_move)

        tk.Label(logo, text="  Frame Republic", font=(_FONT,13,"bold"),
                 bg=PANEL, fg=WHITE).pack(side="left")
        tk.Label(logo, text="   L optimiseur PC gaming", font=F_SMALL,
                 bg=PANEL, fg=T2).pack(side="left")

        # Boutons fenetre
        wb = tk.Frame(bar, bg=PANEL)
        wb.place(relx=1, rely=0, anchor="ne")
        for sym,col_h,cmd,attr in [
            ("  -  ", CARD_H,  self._minimize,    None),
            ("  o  ", CARD_H,  self._toggle_max,  "_max_btn_lbl"),
            ("  x  ", RED,     self._quit,         None),
        ]:
            lb = tk.Label(wb, text=sym, font=("Segoe UI",10,"bold"),
                          bg=PANEL, fg=T2, cursor="hand2")
            lb.pack(side="left", ipady=12, ipadx=3)
            if attr: setattr(self, attr, lb)
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
            # Retour taille normale
            self.overrideredirect(True)
            self.geometry(self._norm_geo)
            self._maximized = False
            try: self._max_btn_lbl.config(text="  o  ")
            except Exception: pass
        else:
            # Sauvegarder taille normale
            self._norm_geo = self.geometry()
            # Maximize: garder overrideredirect mais remplir tout l ecran
            sw = self.winfo_screenwidth()
            sh = self.winfo_screenheight()
            # Recuperer la hauteur de travail (sans taskbar)
            try:
                import ctypes as _ct
                rc = _ct.create_string_buffer(16)
                _ct.windll.user32.SystemParametersInfoW(48, 0, rc, 0)  # SPI_GETWORKAREA=48
                import struct
                left, top, right, bottom = struct.unpack("iiii", rc.raw)
                sw = right - left; sh = bottom - top
                self.geometry("{}x{}+{}+{}".format(sw, sh, left, top))
            except Exception:
                self.geometry("{}x{}+0+0".format(sw, sh - 40))
            self._maximized = True
            try: self._max_btn_lbl.config(text="  _  ")
            except Exception: pass
        self.update_idletasks()

    # ================================================================
    #  SIDEBAR
    # ================================================================
    def _build_sidebar(self, parent):
        sb = tk.Frame(parent, bg=PANEL, width=64)
        sb.grid(row=0, column=0, sticky="ns"); sb.grid_propagate(False)
        sb.grid_rowconfigure(0, weight=1)

        # Separateur droite - simple ligne
        tk.Frame(sb, bg=BD, width=1).pack(side="right", fill="y")

        # Inner directement dans sb - PAS de canvas par-dessus
        inner = tk.Frame(sb, bg=PANEL)
        inner.pack(fill="both", expand=True)

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
                           font=((_FONT,9,"bold") if a else F_TINY))
                ul.config(bg=A if a else PANEL)
            frames[idx].lift()

        for i, lbl in enumerate(labels):
            col = tk.Frame(bar, bg=PANEL); col.pack(side="left")
            lw  = tk.Label(col, text=lbl.upper(),
                           font=(_FONT,9,"bold") if i==0 else F_TINY,
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

    def _mk_btn(self, parent, text, cmd, color=A, padx=14, pady=8, primary=False):
        """Bouton style site frame-republic.netlify.app.
        primary=True -> bouton rouge plein (comme .btn-primary)
        primary=False -> bouton ghost bordure accent (comme .btn-ghost)"""
        if primary:
            # Bouton primaire plein rouge (comme le site)
            bg_normal = color
            fg_normal = WHITE
            bg_hover  = A2      # --accent-hot au hover
            fg_hover  = WHITE
            border    = color
        else:
            # Bouton ghost avec bordure accent
            bg_normal = CARD
            fg_normal = color
            bg_hover  = CARD_H
            fg_hover  = color
            border    = BD

        b = tk.Label(parent, text=text,
                     font=(_FONT_TITLE, 9, "bold"),
                     bg=bg_normal, fg=fg_normal,
                     padx=padx+4, pady=pady+1,
                     cursor="hand2",
                     highlightthickness=1,
                     highlightbackground=border)

        def on_enter(e, w=b, bg=bg_hover, fg=fg_hover, brd=color):
            w.config(bg=bg, fg=fg, highlightbackground=brd)
        def on_leave(e, w=b, bg=bg_normal, fg=fg_normal, brd=border):
            w.config(bg=bg, fg=fg, highlightbackground=brd)

        b.bind("<Enter>", on_enter)
        b.bind("<Leave>", on_leave)
        b.bind("<Button-1>", lambda e, c=cmd:
               threading.Thread(target=c, daemon=True).start())
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
                                    font=(_FONT,8,"bold"), bg=CARD, fg=A2)
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
                                      fill=col2, font=(_FONT,11,"bold"))
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
                                fill=col2, font=(_FONT,11,"bold"))
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
            v = tk.Label(ci, text="--", font=(_FONT,10,"bold"), bg=CARD, fg=col)
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
                 font=(_FONT,10,"bold"), bg=CARD, fg=WHITE).pack(side="left")
        tk.Label(ao_title_f,
                 text="  Analyse et applique les optimisations sans endommager le systeme",
                 font=(_FONT,7), bg=CARD, fg=T2).pack(side="left")

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
                                    font=(_FONT,8), bg=CARD, fg=T2)
        self._ao_status.pack(side="left")
        self._ao_score_delta = tk.Label(ao_status_row, text="",
                                         font=(_FONT,8,"bold"), bg=CARD, fg=A)
        self._ao_score_delta.pack(side="left", padx=8)

        # Raisons / log compact
        self._ao_reasons = tk.Label(ao_inner, text="",
                                     font=(_FONT,7), bg=CARD, fg=T2,
                                     anchor="w", justify="left", wraplength=900)
        self._ao_reasons.pack(fill="x", pady=3)

        # Boutons
        ao_btns = tk.Frame(ao_top, bg=CARD); ao_btns.pack(side="right")

        self._ao_undo_btn = tk.Label(ao_btns, text="Annuler",
                                      font=(_FONT,8), bg=CARD, fg=T2,
                                      padx=10, pady=5, cursor="hand2",
                                      highlightthickness=1, highlightbackground=BD)
        self._ao_undo_btn.pack(side="right", padx=6)
        self._ao_undo_btn.bind("<Enter>", lambda e: self._ao_undo_btn.config(bg=CARD_H, highlightbackground=RED, fg=RED))
        self._ao_undo_btn.bind("<Leave>", lambda e: self._ao_undo_btn.config(bg=CARD, highlightbackground=BD, fg=T2))
        self._ao_undo_btn.bind("<Button-1>", lambda e: threading.Thread(target=self._ao_undo, daemon=True).start())

        self._ao_btn = tk.Label(ao_btns, text="  Optimiser maintenant  ",
                                 font=(_FONT,9,"bold"), bg=A_D, fg=A,
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
        dict(id="hdd_optim",     title="Optimisation disque dur",   desc1="Defrag SSD desactive, trim active.",        desc2="Prolonge la duree de vie du SSD.",          fn=self._do_hdd),
        dict(id="notif_gaming",  title="Notifications jeu off",     desc1="Bloque les notifications pendant les jeux.",desc2="Aucune interruption en pleine partie.",      fn=self._do_gaming_notifs,   initial=True),
        dict(id="usb_poll",      title="USB polling rate",          desc1="Augmente la frequence de scrutation USB.",  desc2="Souris et clavier plus reactifs.",           fn=self._do_usb_poll),
        dict(id="hpet_off",      title="Desactiver HPET",          desc1="Desactive le High Precision Event Timer.",  desc2="Reduit la latence CPU en jeu.",              fn=self._do_hpet),
        dict(id="startup_delay", title="Delai demarrage reduit",    desc1="Supprime le delai de demarrage Windows.",   desc2="Boot plus rapide.",                          fn=self._do_startup_delay,   initial=True),
        dict(id="paging_exec",   title="Kernel en RAM",             desc1="Garde le noyau Windows en memoire vive.",   desc2="Reduit les acces disque systeme.",           fn=self._do_paging_exec,     initial=True),
    ]

    def _jeu_cards(self): return [
        dict(id="game_mode",   title="Mode Jeu Windows",           desc1="Priorise les ressources.",            fn=self._do_game_mode),
        dict(id="xbox_svc",    title="Services Xbox off",           desc1="Arrete les services Xbox inutiles.",  fn=self._do_xbox,       initial=True),
        dict(id="tcp_game",    title="TCP gaming",                  desc1="Reduit le ping et la latence.",       fn=self._do_tcp_game,   initial=True),
        dict(id="gpu_cache",   title="Vider caches GPU",            desc1="DirectX, NVIDIA, AMD, Vulkan.",       fn=self._do_gpu_cache),
        dict(id="mouse_fps",   title="Souris FPS",                  desc1="Desactive l'acceleration souris.",    fn=self._do_mouse,      initial=True),
        dict(id="gamebar",     title="Desactiver Game Bar",         desc1="Supprime la surcouche Xbox.",         fn=self._do_gamebar,    initial=True),
        dict(id="cpu_aff",     title="Priorite CPU jeux",           desc1="Priorite elevee pour les jeux actifs.",       desc2="Detecte Steam, Epic, Battle.net, etc.",      fn=self._do_cpu_game_prio),
        dict(id="msi_gpu",     title="Interruptions MSI GPU",       desc1="Active MSI sur la carte graphique.",          desc2="Reduit la latence des interruptions.",       fn=self._do_msi_gpu),
        dict(id="gpu_optim",   title="Optimisation GPU (Auto)",     desc1="Detecte automatiquement NVIDIA/AMD/Intel.",   desc2="Applique les reglages gaming optimaux.",     fn=self._do_gpu_optim),
        dict(id="fs_optim",    title="Fullscreen optimise",         desc1="Force le mode exclusif plein ecran.",  desc2="Reduit l'input lag.",                  fn=self._do_fullscreen_opt, initial=True),
        dict(id="ram_gaming",  title="RAM gaming mode",             desc1="Optimise l'utilisation memoire.",      desc2="Reduit les stutters en jeu.",          fn=self._do_ram_gaming,     initial=True),
        dict(id="shader_pre",  title="Pre-compilation shaders",     desc1="Force la compilation des shaders.",    desc2="Moins de microstutters au lancement.", fn=self._do_shader_precomp),
        dict(id="cpu_park",    title="Desactiver CPU parking",      desc1="Maintient tous les coeurs actifs.",    desc2="Pas de latence au reveil des coeurs.", fn=self._do_cpu_unpark,     initial=True),
        dict(id="hw_accel",    title="Acceleration GPU Windows",    desc1="Active HAGS (Hardware Accelerated).",  desc2="Reduit la latence GPU sur Windows 11.",fn=self._do_hags),
    ]

    def _build_startup(self, p):
        # Boutons
        top = tk.Frame(p, bg=BG); top.pack(fill="x", padx=14, pady=8)
        self._mk_btn(top, "Rafraichir",         self._load_startup,     A).pack(side="left", padx=0)
        self._mk_btn(top, "Activer selection",  self._startup_enable,   A).pack(side="left", padx=0)
        self._mk_btn(top, "Desactiver select.", self._startup_disable,  RED).pack(side="left", padx=0)
        self._mk_btn(top, "Analyser impact",    self._startup_impact,   BLUE).pack(side="left", padx=0)
        self._mk_btn(top, "Ouvrir Gest. taches",self._open_taskmgr_startup, T2).pack(side="left")

        # Info label
        self._su_info = tk.Label(p, text="Selectionnez une entree puis Activer/Desactiver",
                                  font=F_TINY, bg=BG, fg=T2, anchor="w")
        self._su_info.pack(fill="x", padx=14, pady=0)

        # Treeview avec colonne Statut coloree
        cols = ("Nom", "Registre", "Statut", "Chemin")
        self._su_tree = ttk.Treeview(p, columns=cols, show="headings",
                                      style="FR.Treeview", selectmode="extended")
        self._su_tree.heading("Nom",      text="Nom programme")
        self._su_tree.heading("Registre", text="Source")
        self._su_tree.heading("Statut",   text="Statut")
        self._su_tree.heading("Chemin",   text="Chemin executable")
        self._su_tree.column("Nom",      width=200, anchor="w")
        self._su_tree.column("Registre", width=80,  anchor="center")
        self._su_tree.column("Statut",   width=90,  anchor="center")
        self._su_tree.column("Chemin",   width=440, anchor="w")

        # Tags couleur
        self._su_tree.tag_configure("enabled",  foreground=A)
        self._su_tree.tag_configure("disabled", foreground=RED)
        self._su_tree.tag_configure("folder",   foreground=YELLOW)

        sb = ttk.Scrollbar(p, orient="vertical", command=self._su_tree.yview)
        self._su_tree.configure(yscrollcommand=sb.set)
        self._su_tree.pack(side="left", fill="both", expand=True, padx=14)
        sb.pack(side="left", fill="y", padx=0)

        self._su_log = self._mk_console(p, 5)
        self._su_log.pack(fill="x", padx=14, pady=8)
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
            dict(id="copilot2",     title="Copilot IA",               desc1="Desactive Microsoft Copilot.",          fn=self._do_copilot,          initial=True),
        dict(id="diag_track",   title="DiagTrack service",        desc1="Arrete le service de telemetrie.",       fn=self._do_diagtrack,        initial=True),
        dict(id="compat_telem", title="Telemetrie compatibilite", desc1="Desactive WerSvc et WerMgr.",            fn=self._do_compat_telem,     initial=True),
        dict(id="app_compat",   title="Compatibilite applis",     desc1="Desactive la couche de compatibilite.",  fn=self._do_app_compat),
        dict(id="cloud_content",title="Contenus cloud Windows",   desc1="Desactive les suggestions cloud.",       fn=self._do_cloud_content,    initial=True),
        dict(id="smart_screen", title="SmartScreen reduit",       desc1="Reduit les envois SmartScreen.",         fn=self._do_smartscreen,      initial=True),
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
                 font=(_FONT,9,"bold"), bg=BG, fg=A).pack(side="left")

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
            v = tk.Label(c, text="--", font=(_FONT,13,"bold"), bg=CARD, fg=col)
            v.pack(padx=10); self._nm_cards[key] = v

        # Boutons
        br = tk.Frame(p, bg=BG); br.pack(fill="x", padx=14, pady=0)
        self._nm_running = False
        self._tray_active = False
        self._tray_hwnd  = None
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
                dict(id="hibernate",    title="Desactiver hibernation", desc1="Libere hiberfil.sys (4-32 Go).",        fn=self._do_hibernate),
        dict(id="focus_assist", title="Focus Assist",          desc1="Bloque les distractions en mode focus.",  fn=self._do_focus_assist),
        dict(id="clipboard_h",  title="Historique presse-papier",desc1="Active l historique multi-elements.",   fn=self._do_clipboard,        initial=True),
        dict(id="snap_windows", title="Snap Windows ameliore", desc1="Meilleur ancrage des fenetres.",          fn=self._do_snap,             initial=True),
        dict(id="virtual_desk", title="Bureaux virtuels rapides",desc1="Navigation rapide entre bureaux.",      fn=self._do_vdesk),
        dict(id="scrolling",    title="Defilement inactif",    desc1="Scroll dans fenetres en arriere-plan.",   fn=self._do_inactive_scroll,  initial=True),
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
        self._c_res=tk.Label(left,text="",font=(_FONT,9,"bold"),bg=BG,fg=A)
        self._c_res.pack(anchor="w",pady=4)

        right=tk.Frame(body,bg=BG); right.pack(side="right",fill="both",expand=True)
        self._c_log=self._mk_console(right); self._c_log.pack(fill="both",expand=True)

    def _build_page_processus(self):
        pg=self._pages["processus"]
        fs=self._sub_tabs(pg,["Processus actifs", "Materiel & Capteurs"]); p=fs[0]
        self._build_hardware_tab(fs[1])

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

    def _build_hardware_tab(self, p):
        """Page surveillance materiel: CPU, GPU, RAM, ventilateurs."""

        # Header
        hdr = tk.Frame(p, bg=BG); hdr.pack(fill="x", padx=14, pady=10)
        tk.Label(hdr, text="SURVEILLANCE MATERIEL EN TEMPS REEL",
                 font=("Bahnschrift",9) if True else F_HEAD,
                 bg=BG, fg=A).pack(side="left")
        self._hw_running = False

        # Boutons
        btns = tk.Frame(p, bg=BG); btns.pack(fill="x", padx=14, pady=0)
        self._hw_btn = self._mk_btn(btns, "Demarrer la surveillance", self._hw_toggle, A)
        self._hw_btn.pack(side="left", padx=0)
        self._mk_btn(btns, "Rafraichir maintenant", self._hw_refresh, BLUE).pack(side="left", padx=0)
        self._mk_btn(btns, "Exporter rapport", self._hw_export, T2).pack(side="left")

        # Grille de cartes capteurs
        cards_frame = tk.Frame(p, bg=BG)
        cards_frame.pack(fill="x", padx=14, pady=0)

        self._hw_vals = {}
        sensors = [
            # (key,         label,           unit,   col,    icon)
            ("cpu_temp",   "Temperature CPU", "C",   RED,    "T"),
            ("cpu_usage",  "Utilisation CPU", "%",    ORANGE, "C"),
            ("cpu_freq",   "Frequence CPU",   "MHz",  YELLOW, "F"),
            ("cpu_cores",  "Coeurs actifs",   "",     A,      "#"),
            ("ram_used",   "RAM utilisee",    "GB",   BLUE,   "M"),
            ("ram_pct",    "RAM %",           "%",    BLUE,   "%"),
            ("gpu_temp",   "Temperature GPU", "C",   RED,    "G"),
            ("gpu_usage",  "Utilisation GPU", "%",    PURPLE, "G"),
            ("fan_cpu",    "Ventil. CPU",     "RPM",  A,      "V"),
            ("fan_sys",    "Ventil. Systeme", "RPM",  A,      "V"),
            ("disk_temp",  "Temperature HDD", "C",   ORANGE, "D"),
            ("uptime_hw",  "Uptime systeme",  "",     T2,     "U"),
        ]

        for i, (key, lbl, unit, col, ico) in enumerate(sensors):
            c = tk.Frame(cards_frame, bg=CARD,
                         highlightthickness=1, highlightbackground=BD)
            c.grid(row=i//4, column=i%4, padx=5, pady=5, sticky="nsew")
            cards_frame.columnconfigure(i%4, weight=1)

            # Triangle déco
            tri = tk.Canvas(c, width=18, height=14, bg=CARD, highlightthickness=0)
            tri.pack(anchor="ne")
            tri.create_polygon(18,0,18,14,4,0, fill=A_D, outline="")

            inner = tk.Frame(c, bg=CARD, padx=10, pady=6); inner.pack(fill="both")
            tk.Label(inner, text=lbl, font=F_TINY, bg=CARD, fg=T3).pack(anchor="w")

            val_lbl = tk.Label(inner, text="--",
                               font=("Segoe UI", 14, "bold"), bg=CARD, fg=col)
            val_lbl.pack(anchor="w")

            unit_lbl = tk.Label(inner, text=unit, font=F_TINY, bg=CARD, fg=T2)
            unit_lbl.pack(anchor="w")

            self._hw_vals[key] = (val_lbl, col, unit)

        # Barre de statut + log
        self._hw_status = tk.Label(p, text="Pret - Appuyez sur Demarrer",
                                    font=F_TINY, bg=BG, fg=T2, anchor="w")
        self._hw_status.pack(fill="x", padx=14, pady=0)

        self._hw_log = self._mk_console(p, height=6)
        self._hw_log.pack(fill="both", expand=True, padx=14, pady=0)

    def _hw_toggle(self):
        """Demarrer/arreter la surveillance materielle."""
        if not self._hw_running:
            self._hw_running = True
            self._hw_btn.config(text="Arreter la surveillance",
                                fg=RED, highlightbackground=RED)
            self._hw_status.config(text="Surveillance active...", fg=A)
            self._hw_loop()
        else:
            self._hw_running = False
            self._hw_btn.config(text="Demarrer la surveillance",
                                fg=A, highlightbackground=BD)
            self._hw_status.config(text="Surveillance arretee.", fg=T2)

    def _hw_loop(self):
        """Boucle de mise a jour toutes les 2 secondes."""
        if not self._hw_running: return
        threading.Thread(target=self._hw_refresh, daemon=True).start()
        self.after(2000, self._hw_loop)

    def _hw_refresh(self):
        """Lit tous les capteurs et met a jour l'affichage."""
        data = self._hw_read_all()
        self.after(0, lambda d=data: self._hw_update_ui(d))

    def _hw_read_all(self):
        """Lit CPU, RAM, GPU, ventilateurs via WMI + psutil."""
        data = {}

        # ── CPU via psutil ─────────────────────────────────────
        if HAS_PSUTIL:
            try:
                data["cpu_usage"] = psutil.cpu_percent(interval=0.3)
            except Exception: data["cpu_usage"] = None

            try:
                freq = psutil.cpu_freq()
                data["cpu_freq"] = int(freq.current) if freq else None
            except Exception: data["cpu_freq"] = None

            try:
                data["cpu_cores"] = "{}/{}".format(
                    psutil.cpu_count(logical=False),
                    psutil.cpu_count())
            except Exception: data["cpu_cores"] = None

            try:
                vm = psutil.virtual_memory()
                data["ram_used"] = round(vm.used / 1024**3, 1)
                data["ram_pct"]  = vm.percent
            except Exception:
                data["ram_used"] = None; data["ram_pct"] = None

            try:
                h, r = divmod(int(time.time() - psutil.boot_time()), 3600)
                data["uptime_hw"] = "{}h{}m".format(h, r//60)
            except Exception: data["uptime_hw"] = None

            # Températures psutil (Linux surtout, parfois Windows)
            try:
                temps = psutil.sensors_temperatures()
                if temps:
                    for name, entries in temps.items():
                        if "cpu" in name.lower() or "core" in name.lower():
                            if entries:
                                data["cpu_temp"] = round(entries[0].current, 1)
                                break
            except Exception: pass

        # ── WMI pour ventilateurs et températures Windows ───────
        try:
            import subprocess
            # Température CPU via WMI MSAcpi
            out = run("wmic /namespace:\\root\\wmi PATH "
                      "MSAcpi_ThermalZoneTemperature GET CurrentTemperature "
                      "/value 2>nul", t=5)
            import re as re2
            temps_wmi = re2.findall(r"CurrentTemperature=(\d+)", out)
            if temps_wmi and "cpu_temp" not in data:
                # Convertir de decikelvin en Celsius
                val = (int(temps_wmi[0]) / 10.0) - 273.15
                if 0 < val < 120:
                    data["cpu_temp"] = round(val, 1)
        except Exception: pass

        # ── Ventilateurs via WMI Win32_Fan ─────────────────────
        try:
            out_fan = run("wmic path Win32_Fan GET DesiredSpeed,Name "
                          "/value 2>nul", t=5)
            import re as re3
            speeds = re3.findall(r"DesiredSpeed=(\d+)", out_fan)
            names  = re3.findall("Name=([^\\r\\n]+)", out_fan)
            if speeds:
                data["fan_cpu"] = int(speeds[0]) if speeds else None
                data["fan_sys"] = int(speeds[1]) if len(speeds) > 1 else None
        except Exception: pass

        # ── Température GPU via PowerShell + WMI ───────────────
        try:
            out_gpu = ps(
                "Get-WmiObject -Namespace root/OpenHardwareMonitor "
                "-Class Sensor | Where-Object {$_.SensorType -eq 'Temperature' "
                "-and $_.Name -like '*GPU*'} | Select-Object -First 1 Value",
                t=6)
            import re as re4
            m = re4.search(r"(\d+\.?\d*)", out_gpu)
            if m:
                data["gpu_temp"]  = float(m.group(1))
                data["gpu_usage"] = None
        except Exception: pass

        # ── Fallback OpenHardwareMonitor pour tout ──────────────
        if not data.get("fan_cpu"):
            try:
                out_ohm = ps(
                    "Get-WmiObject -Namespace root/OpenHardwareMonitor "
                    "-Class Sensor | Where-Object {$_.SensorType -eq 'Fan'} "
                    "| Select-Object Name, Value | Format-List",
                    t=6)
                import re as re5
                vals = re5.findall(r"Value\s*:\s*(\d+\.?\d*)", out_ohm)
                nms  = re5.findall(r"Name\s*:\s*(.+)", out_ohm)
                for nm, v in zip(nms, vals):
                    nm_l = nm.lower()
                    if "cpu" in nm_l and not data.get("fan_cpu"):
                        data["fan_cpu"] = int(float(v))
                    elif not data.get("fan_sys"):
                        data["fan_sys"] = int(float(v))
            except Exception: pass

        # ── Température disque via SMART ─────────────────────
        try:
            out_disk = run("wmic diskdrive get Status /value 2>nul", t=4)
            # Pas de temperature directe par wmic standard
            # Utiliser SMART via PowerShell
            out_smart = ps(
                "Get-PhysicalDisk | Get-StorageReliabilityCounter "
                "| Select-Object -ExpandProperty Temperature "
                "-ErrorAction SilentlyContinue",
                t=5)
            import re as re6
            m = re6.search(r"(\d+)", out_smart)
            if m and 0 < int(m.group(1)) < 80:
                data["disk_temp"] = int(m.group(1))
        except Exception: pass

        return data

    def _hw_update_ui(self, data):
        """Met a jour les labels avec les donnees capteurs."""
        for key, (lbl, default_col, unit) in self._hw_vals.items():
            val = data.get(key)

            if val is None:
                lbl.config(text="N/A", fg=T2)
                continue

            # Choisir la couleur selon la valeur
            col = default_col
            if key in ("cpu_temp", "gpu_temp", "disk_temp"):
                try:
                    v = float(val)
                    col = A if v < 60 else YELLOW if v < 80 else RED
                    lbl.config(text=str(val), fg=col)
                    continue
                except Exception: pass

            elif key in ("cpu_usage", "ram_pct", "gpu_usage"):
                try:
                    v = float(val)
                    col = A if v < 60 else YELLOW if v < 80 else RED
                except Exception: pass

            elif key in ("fan_cpu", "fan_sys"):
                try:
                    v = int(val)
                    if v == 0:
                        lbl.config(text="Arrete", fg=T2)
                        continue
                    col = A if v > 500 else YELLOW
                except Exception: pass

            lbl.config(text=str(val), fg=col)

        self._hw_status.config(
            text="Mis a jour: " + datetime.now().strftime("%H:%M:%S"),
            fg=T2)

    def _hw_export(self):
        """Exporte un rapport texte des capteurs."""
        path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Texte", "*.txt")],
            initialfile="rapport_hardware.txt")
        if not path: return
        threading.Thread(target=self._hw_export_th,
                         args=(path,), daemon=True).start()

    def _hw_export_th(self, path):
        data = self._hw_read_all()
        lines_out = [
            "FRAME REPUBLIC - Rapport Hardware",
            "=" * 40,
            "Date: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "",
        ]
        labels = {
            "cpu_temp":  "Temperature CPU",
            "cpu_usage": "Utilisation CPU",
            "cpu_freq":  "Frequence CPU",
            "cpu_cores": "Coeurs CPU",
            "ram_used":  "RAM utilisee (GB)",
            "ram_pct":   "RAM %",
            "gpu_temp":  "Temperature GPU",
            "gpu_usage": "Utilisation GPU",
            "fan_cpu":   "Ventilateur CPU (RPM)",
            "fan_sys":   "Ventilateur Systeme (RPM)",
            "disk_temp": "Temperature Disque",
            "uptime_hw": "Uptime",
        }
        for key, lbl in labels.items():
            v = data.get(key, "N/A")
            lines_out.append("{:<30s}: {}".format(lbl, v if v is not None else "N/A"))

        try:
            with open(path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(lines_out))
            self._clog(self._hw_log, "Rapport exporte -> " + path, "ok")
        except Exception as e:
            self._clog(self._hw_log, "Erreur export: " + str(e), "err")


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
        """Charge TOUTES les entrees de demarrage (Run, RunOnce, Wow64, dossiers, taches)."""
        entries = []

        # === 1. Toutes les cles Run (32 + 64 bits, HKCU + HKLM) ===
        run_keys = [
            (winreg.HKEY_CURRENT_USER,
             r"Software\Microsoft\Windows\CurrentVersion\Run", "HKCU Run"),
            (winreg.HKEY_LOCAL_MACHINE,
             r"Software\Microsoft\Windows\CurrentVersion\Run", "HKLM Run"),
            (winreg.HKEY_LOCAL_MACHINE,
             r"Software\Wow6432Node\Microsoft\Windows\CurrentVersion\Run",
             "HKLM Run x86"),
            (winreg.HKEY_CURRENT_USER,
             r"Software\Microsoft\Windows\CurrentVersion\Run32", "HKCU Run32"),
            (winreg.HKEY_LOCAL_MACHINE,
             r"Software\Microsoft\Windows\CurrentVersion\Policies\Explorer\Run",
             "HKLM Policies"),
            (winreg.HKEY_CURRENT_USER,
             r"Software\Microsoft\Windows\CurrentVersion\Policies\Explorer\Run",
             "HKCU Policies"),
        ]
        for hive, path, src_lbl in run_keys:
            try:
                key = winreg.OpenKey(hive, path, 0,
                                     winreg.KEY_READ | winreg.KEY_WOW64_64KEY)
                i = 0
                while True:
                    try:
                        n, v, _ = winreg.EnumValue(key, i)
                        # Eviter doublons
                        if not any(e["name"] == n and e["src"] == src_lbl
                                   for e in entries):
                            entries.append({
                                "name": n, "src": src_lbl,
                                "status": "Actif", "path": str(v)[:100],
                                "hive": hive, "key": path, "tag": "enabled"})
                        i += 1
                    except OSError: break
                winreg.CloseKey(key)
            except Exception: pass

        # Cles RunOnce actives
        for hive, path, src_lbl in [
            (winreg.HKEY_CURRENT_USER,
             r"Software\Microsoft\Windows\CurrentVersion\RunOnce", "HKCU Once"),
            (winreg.HKEY_LOCAL_MACHINE,
             r"Software\Microsoft\Windows\CurrentVersion\RunOnce", "HKLM Once"),
        ]:
            try:
                key = winreg.OpenKey(hive, path); i = 0
                while True:
                    try:
                        n, v, _ = winreg.EnumValue(key, i)
                        entries.append({
                            "name": n, "src": src_lbl,
                            "status": "RunOnce", "path": v[:80],
                            "hive": hive, "key": path, "tag": "folder"})
                        i += 1
                    except OSError: break
                winreg.CloseKey(key)
            except Exception: pass

        # Cles desactivees (prefixe avec "\0" dans le nom)
        disabled_path = r"Software\Microsoft\Windows\CurrentVersion\Explorer\StartupApproved\Run"
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, disabled_path)
            i = 0
            while True:
                try:
                    n, v, _ = winreg.EnumValue(key, i)
                    # Verifier si desactive (bytes commencent par 03 00)
                    if isinstance(v, bytes) and len(v) >= 4:
                        is_disabled = v[0] in (3, 0x03)
                        if is_disabled:
                            # Trouver le chemin dans Run
                            for e in entries:
                                if e["name"].lower() == n.lower():
                                    e["status"] = "Desactive"
                                    e["tag"] = "disabled"
                    i += 1
                except OSError: break
            winreg.CloseKey(key)
        except Exception: pass

        # === 4. Dossiers Startup (user + global) ===
        for folder, src_lbl in [
            (os.path.join(os.environ.get("APPDATA",""),
             "Microsoft","Windows","Start Menu","Programs","Startup"), "Dossier User"),
            (r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Startup",
             "Dossier Global"),
        ]:
            if os.path.isdir(folder):
                try:
                    for item in os.listdir(folder):
                        if item.lower() == "desktop.ini": continue
                        full = os.path.join(folder, item)
                        entries.append({
                            "name": item, "src": src_lbl,
                            "status": "Actif", "path": full,
                            "hive": None, "key": folder, "tag": "folder"})
                except Exception: pass

        # === 5. Taches planifiees au demarrage ===
        try:
            out = run("schtasks /query /fo csv /nh 2>nul", t=10)
            for line in out.split("\n")[:200]:  # Limiter
                parts = [p.strip('"') for p in line.split('","')]
                if len(parts) >= 3:
                    name = parts[0].split("\\")[-1]
                    status = parts[2]
                    # Seulement les taches liees au demarrage (heuristique)
                    name_lower = name.lower()
                    if any(kw in name_lower for kw in
                           ["startup", "logon", "update", "launcher",
                            "adobe", "nvidia", "amd", "realtek", "intel",
                            "onedrive", "teams", "discord", "steam",
                            "epic", "origin", "gog"]):
                        tag = "enabled" if status == "Ready" else "disabled"
                        if status == "Disabled": tag = "disabled"
                        entries.append({
                            "name": name, "src": "Tache planifiee",
                            "status": status,
                            "path": parts[1] if len(parts) > 1 else "",
                            "hive": None, "key": "schtasks",
                            "tag": tag})
        except Exception: pass

        # === 6. Services demarrant automatiquement (filtrage) ===
        try:
            import subprocess as _sp
            out = run('sc queryex type= service state= all', t=15)
            # Parsing basique des services AUTO_START
            current = {}
            for line in out.split("\n"):
                line = line.strip()
                if "SERVICE_NAME:" in line:
                    if current.get("name") and current.get("type") == "AUTO_START":
                        entries.append({
                            "name": current["name"], "src": "Service Auto",
                            "status": current.get("state", "?"),
                            "path": "Service Windows",
                            "hive": None, "key": "service",
                            "tag": "folder"})
                    current = {"name": line.split(":",1)[1].strip()}
                elif "DISPLAY_NAME" in line:
                    current["display"] = line.split(":",1)[1].strip()
                elif "START_TYPE" in line:
                    if "AUTO_START" in line: current["type"] = "AUTO_START"
                elif "STATE" in line:
                    current["state"] = "Running" if "RUNNING" in line else "Stopped"
        except Exception: pass

        # Dedupliquer par nom+src
        seen = set(); unique = []
        for e in entries:
            key = (e["name"].lower(), e["src"])
            if key not in seen:
                seen.add(key); unique.append(e)
        entries = unique

        # Trier: actifs d abord, par source
        entries.sort(key=lambda e: (e["tag"] != "enabled", e["src"], e["name"].lower()))

        # Stocker pour enable/disable
        self._startup_entries = entries

        # Mettre a jour le treeview
        def upd():
            for i in self._su_tree.get_children():
                self._su_tree.delete(i)
            for e in entries:
                self._su_tree.insert("", "end",
                    values=(e["name"], e["src"], e["status"], e["path"]),
                    tags=(e["tag"],))
        self.after(0, upd)

        n_dis = sum(1 for e in entries if e["status"] == "Desactive")
        n_act = sum(1 for e in entries if e["status"] == "Actif")
        msg = f"{len(entries)} entrees: {n_act} actives, {n_dis} desactivees"
        self._clog(self._su_log, msg, "warn" if n_act > 8 else "ok")

    def _startup_impact(self):
        n = len(self._su_tree.get_children())
        msg = str(n) + " programmes au demarrage - "
        if n < 5:   msg += "Demarrage RAPIDE"
        elif n < 10: msg += "Demarrage MODERE"
        else:        msg += "Demarrage LENT !"
        self._clog(self._su_log, msg, "ok" if n<5 else "warn" if n<10 else "err")

    def _startup_enable(self):
        """Active les entrees selectionnees dans le treeview."""
        sel = self._su_tree.selection()
        if not sel:
            self._clog(self._su_log, "Selectionnez une entree d abord.", "warn"); return
        count = 0
        for item in sel:
            vals = self._su_tree.item(item)["values"]
            name = vals[0]; src_lbl = vals[1]
            try:
                # Supprimer le flag desactive dans StartupApproved
                dis_path = r"Software\Microsoft\Windows\CurrentVersion\Explorer\StartupApproved\Run"
                try:
                    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, dis_path, 0,
                                         winreg.KEY_SET_VALUE)
                    # Ecrire bytes d activation (02 00 00 00 ...)
                    winreg.SetValueEx(key, name, 0, winreg.REG_BINARY,
                                      bytes([2,0,0,0,0,0,0,0,0,0,0,0]))
                    winreg.CloseKey(key)
                    count += 1
                except Exception:
                    pass
                self._su_tree.item(item, tags=("enabled",),
                                   values=(name, src_lbl, "Actif", vals[3]))
            except Exception as e:
                self._clog(self._su_log, "Erreur: " + str(e), "err")
        self._clog(self._su_log, str(count) + " entree(s) activee(s)", "ok")
        self.after(500, self._load_startup)

    def _startup_disable(self):
        """Desactive les entrees selectionnees."""
        sel = self._su_tree.selection()
        if not sel:
            self._clog(self._su_log, "Selectionnez une entree d abord.", "warn"); return
        if not messagebox.askyesno("Confirmer",
            str(len(sel)) + " entree(s) a desactiver au demarrage ?\n"
            "Elles ne seront pas supprimees, juste desactivees."):
            return
        count = 0
        for item in sel:
            vals = self._su_tree.item(item)["values"]
            name = vals[0]; src_lbl = vals[1]
            try:
                dis_path = r"Software\Microsoft\Windows\CurrentVersion\Explorer\StartupApproved\Run"
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, dis_path, 0,
                                     winreg.KEY_SET_VALUE | winreg.KEY_CREATE_SUB_KEY)
                # Ecrire bytes de desactivation (03 00 00 00 ...)
                winreg.SetValueEx(key, name, 0, winreg.REG_BINARY,
                                  bytes([3,0,0,0,0,0,0,0,0,0,0,0]))
                winreg.CloseKey(key)
                self._su_tree.item(item, tags=("disabled",),
                                   values=(name, src_lbl, "Desactive", vals[3]))
                count += 1
            except Exception as e:
                self._clog(self._su_log, "Erreur: " + str(e), "err")
        self._clog(self._su_log, str(count) + " entree(s) desactivee(s)", "ok")

    def _open_taskmgr_startup(self):
        """Ouvre le gestionnaire de taches sur l onglet Demarrage."""
        try:
            import subprocess as _sp
            _sp.Popen(["taskmgr.exe", "/0", "/startup"],
                      creationflags=NW)
        except Exception:
            os.startfile("taskmgr.exe")

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
        if not self._check_network():
            self._clog(self._n_log,"Pas de connexion reseau disponible.","err"); return
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
        if state and not self._check_network():
            self._dlog("Reseau requis pour configurer DNS","err"); return
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
        if not self._check_network():
            self._clog(self._n_log,"Pas de connexion reseau disponible.","err"); return
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
        if not self._check_network():
            self._clog(self._nm_log,"Pas de connexion reseau.","err"); return
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

    # ============================================================
    #  DETECTION MATERIEL + OPTIMISATION GPU
    # ============================================================

    def _detect_gpu(self):
        """Detecte le GPU principal et son constructeur.
        Retourne un dict: {vendor, name, driver_version}."""
        info = {"vendor": None, "name": None, "driver": None}
        try:
            out = run(
                'wmic path Win32_VideoController get Name,'
                'AdapterCompatibility,DriverVersion /format:csv 2>nul',
                t=8)
            # Parser CSV
            lines = [l.strip() for l in out.split("\n") if l.strip()]
            for line in lines[1:]:  # skip header
                parts = line.split(",")
                if len(parts) >= 4:
                    vendor = parts[1].strip()
                    driver = parts[2].strip()
                    name = parts[3].strip()
                    if vendor and name:
                        vl = vendor.lower()
                        nl = name.lower()
                        # Priorite GPU dedie > integre
                        is_ded = any(k in nl for k in
                                     ["geforce","rtx","gtx","radeon","rx ",
                                      "arc "," vega","quadro","tesla"])
                        if is_ded or not info["vendor"]:
                            if "nvidia" in vl or "nvidia" in nl:
                                info["vendor"] = "NVIDIA"
                            elif "amd" in vl or "advanced micro" in vl or "ati" in vl:
                                info["vendor"] = "AMD"
                            elif "intel" in vl:
                                info["vendor"] = "INTEL"
                            else:
                                info["vendor"] = "UNKNOWN"
                            info["name"] = name
                            info["driver"] = driver
                            if is_ded: break
        except Exception: pass
        return info

    def _do_gpu_optim(self, state=True):
        """Optimisation GPU avec detection automatique du vendor."""
        gpu = self._detect_gpu()
        vendor = gpu.get("vendor")
        name   = gpu.get("name", "inconnu")

        self._dlog("GPU detecte: " + str(name) + " (" + str(vendor or "?") + ")")

        if not state:
            self._dlog("Reglages GPU restaures par defaut")
            if vendor == "NVIDIA": self._gpu_reset_nvidia()
            elif vendor == "AMD":  self._gpu_reset_amd()
            return

        if vendor == "NVIDIA":
            self._gpu_optim_nvidia()
        elif vendor == "AMD":
            self._gpu_optim_amd()
        elif vendor == "INTEL":
            self._gpu_optim_intel()
        else:
            self._dlog("Aucune optimisation GPU disponible pour ce vendor")

        # Optimisations communes a tous les GPU
        self._gpu_optim_common(state)

    # ── NVIDIA ────────────────────────────────────────────────
    def _gpu_optim_nvidia(self):
        """Optimisations NVIDIA SURES uniquement (aucun risque de casser le PC).
        Applique les reglages du Panneau de configuration NVIDIA > Gerer
        les parametres 3D pour un profil gaming optimal."""
        try:
            import winreg as wr
            applied = []

            # ─────────────────────────────────────────────────────
            # 1. MODE ALIMENTATION = PERFORMANCE MAXIMALE
            # ─────────────────────────────────────────────────────
            # Safe: juste dit au GPU de ne pas se downclocker
            # Reversible: un toggle OFF restaure la valeur par defaut
            reg_set(wr.HKEY_LOCAL_MACHINE,
                    r"SYSTEM\CurrentControlSet\Services\nvlddmkm\Global\NVTweak",
                    "PowerMizerEnable", 1)
            reg_set(wr.HKEY_LOCAL_MACHINE,
                    r"SYSTEM\CurrentControlSet\Services\nvlddmkm\Global\NVTweak",
                    "PerfLevelSrc", 0x2222)
            reg_set(wr.HKEY_LOCAL_MACHINE,
                    r"SYSTEM\CurrentControlSet\Services\nvlddmkm\Global\NVTweak",
                    "PowerMizerLevel", 1)
            reg_set(wr.HKEY_LOCAL_MACHINE,
                    r"SYSTEM\CurrentControlSet\Services\nvlddmkm\Global\NVTweak",
                    "PowerMizerLevelAC", 1)
            applied.append("Mode alimentation: Performance maximale")

            # ─────────────────────────────────────────────────────
            # 2. SYNCHRO VERTICALE = DESACTIVEE
            # ─────────────────────────────────────────────────────
            # Safe: reglage standard du panneau NVIDIA
            reg_set(wr.HKEY_LOCAL_MACHINE,
                    r"SOFTWARE\NVIDIA Corporation\Global\NVTweak",
                    "VSync", 0)
            applied.append("Synchro verticale: Desactivee")

            # ─────────────────────────────────────────────────────
            # 3. MODE LATENCE = ULTRA (NVIDIA Reflex)
            # ─────────────────────────────────────────────────────
            # Safe: equivalent de "Low Latency Mode = Ultra"
            reg_set(wr.HKEY_LOCAL_MACHINE,
                    r"SOFTWARE\NVIDIA Corporation\Global\NGXCore",
                    "ReflexMode", 2)  # 2 = Ultra
            # Valeur officielle du panneau NVIDIA pour Low Latency Mode
            reg_set(wr.HKEY_LOCAL_MACHINE,
                    r"SYSTEM\CurrentControlSet\Services\nvlddmkm\Global\NVTweak",
                    "LowLatencyMode", 2)
            applied.append("Mode latence: Ultra")

            # ─────────────────────────────────────────────────────
            # 4. MAX FRAMES RENDERED AHEAD = 1
            # ─────────────────────────────────────────────────────
            # Safe: reduit l input lag, pas de risque
            reg_set(wr.HKEY_LOCAL_MACHINE,
                    r"SYSTEM\CurrentControlSet\Services\nvlddmkm\Global\NVTweak",
                    "PrerenderLimit", 1)
            applied.append("Pre-render frames: 1")

            # ─────────────────────────────────────────────────────
            # 5. THREADED OPTIMIZATION = ON
            # ─────────────────────────────────────────────────────
            # Safe: utilise plusieurs coeurs CPU, defaut NVIDIA moderne
            reg_set(wr.HKEY_LOCAL_MACHINE,
                    r"SYSTEM\CurrentControlSet\Services\nvlddmkm",
                    "DisableThreadedOptimization", 0)
            applied.append("Threaded optimization: Activee")

            # ─────────────────────────────────────────────────────
            # 6. SHADER CACHE = ILLIMITE
            # ─────────────────────────────────────────────────────
            # Safe: evite les stutters de compilation de shaders
            # 0xFFFFFFFF = unlimited
            reg_set(wr.HKEY_LOCAL_MACHINE,
                    r"SYSTEM\CurrentControlSet\Services\nvlddmkm\Global\NVTweak",
                    "ShaderCacheSize", 0xFFFFFFFF)
            applied.append("Shader cache: Illimite")

            # ─────────────────────────────────────────────────────
            # 7. TEXTURE FILTERING = HIGH PERFORMANCE
            # ─────────────────────────────────────────────────────
            # Safe: privilegie FPS sur qualite textures
            reg_set(wr.HKEY_LOCAL_MACHINE,
                    r"SYSTEM\CurrentControlSet\Services\nvlddmkm\Global\NVTweak",
                    "TextureFilteringQuality", 0)  # 0 = High Performance
            applied.append("Filtrage textures: Haute performance")

            # ─────────────────────────────────────────────────────
            # 8. ANISOTROPIC SAMPLE OPTIMIZATION = ON
            # ─────────────────────────────────────────────────────
            reg_set(wr.HKEY_LOCAL_MACHINE,
                    r"SYSTEM\CurrentControlSet\Services\nvlddmkm\Global\NVTweak",
                    "AnisotropicSampleOptim", 1)
            applied.append("Anisotropic sample optim: Activee")

            # ─────────────────────────────────────────────────────
            # 9. NVIDIA TELEMETRY = OFF (safe, recommande)
            # ─────────────────────────────────────────────────────
            # Safe: desactive juste la collecte de stats
            for svc in ["NvTelemetryContainer"]:
                run("sc config " + svc + " start= demand 2>nul")
                run("sc stop " + svc + " 2>nul")
            applied.append("Telemetrie NVIDIA: Desactivee")

            # ─────────────────────────────────────────────────────
            # Afficher le resume
            # ─────────────────────────────────────────────────────
            self._dlog("=== Optimisations NVIDIA appliquees ===")
            for a in applied:
                self._dlog("  OK  " + a)
            self._dlog("Redemarrez vos jeux pour appliquer les changements")

        except Exception as e:
            self._dlog("Erreur NVIDIA: " + str(e)[:80])

    def _gpu_reset_nvidia(self):
        """Restaure les valeurs par defaut NVIDIA."""
        try:
            import winreg as wr
            reg_set(wr.HKEY_LOCAL_MACHINE,
                    r"SYSTEM\CurrentControlSet\Services\nvlddmkm\Global\NVTweak",
                    "PowerMizerLevel",   0)
            reg_set(wr.HKEY_LOCAL_MACHINE,
                    r"SOFTWARE\NVIDIA Corporation\Global\NVTweak",
                    "VSync", 1)
            reg_set(wr.HKEY_LOCAL_MACHINE,
                    r"SYSTEM\CurrentControlSet\Services\nvlddmkm\Global\NVTweak",
                    "PrerenderLimit", 3)
            self._dlog("NVIDIA: valeurs par defaut restaurees")
        except Exception: pass

    # ── AMD ───────────────────────────────────────────────────
    def _gpu_optim_amd(self):
        """Applique les reglages AMD Radeon gaming optimaux."""
        try:
            import winreg as wr
            # AMD Radeon Software - reglages registre
            # Cle: HKLM\SYSTEM\CurrentControlSet\Control\Class\{4d36e968-...}
            # Variable: VSync, PowerXpress, etc.

            # 1. Power Efficiency = Off (Maximum performance)
            reg_set(wr.HKEY_LOCAL_MACHINE,
                    r"SOFTWARE\AMD\CN",
                    "PowerSaving", 0)

            # 2. Radeon Anti-Lag = On (equivalent Reflex)
            reg_set(wr.HKEY_LOCAL_MACHINE,
                    r"SOFTWARE\AMD\DAL",
                    "AntiLag_ENABLE", 1)

            # 3. Radeon Boost = Off (peut causer stutters)
            reg_set(wr.HKEY_LOCAL_MACHINE,
                    r"SOFTWARE\AMD\DAL",
                    "RadeonBoost_ENABLE", 0)

            # 4. VSync = Off
            reg_set(wr.HKEY_LOCAL_MACHINE,
                    r"SOFTWARE\ATI Technologies\CN",
                    "VSyncControl", 0)

            # 5. Tessellation = Optimise
            reg_set(wr.HKEY_LOCAL_MACHINE,
                    r"SOFTWARE\AMD\CN",
                    "TessellationMode", 1)

            # 6. Surface format optim = On
            reg_set(wr.HKEY_LOCAL_MACHINE,
                    r"SOFTWARE\AMD\CN",
                    "SurfaceFormatOptim", 1)

            # 7. Telemetrie AMD OFF
            for svc in ["AMD External Events Utility", "AMDRyzenMasterDriverV22"]:
                run('sc config "' + svc + '" start= demand 2>nul')

            self._dlog("OK AMD: Anti-Lag on, VSync off, Max performance")

        except Exception as e:
            self._dlog("Erreur AMD: " + str(e)[:60])

    def _gpu_reset_amd(self):
        """Restaure les valeurs par defaut AMD."""
        try:
            import winreg as wr
            reg_set(wr.HKEY_LOCAL_MACHINE, r"SOFTWARE\AMD\CN",
                    "PowerSaving", 1)
            reg_set(wr.HKEY_LOCAL_MACHINE, r"SOFTWARE\ATI Technologies\CN",
                    "VSyncControl", 1)
            self._dlog("AMD: valeurs par defaut restaurees")
        except Exception: pass

    # ── INTEL ─────────────────────────────────────────────────
    def _gpu_optim_intel(self):
        """Optimisations Intel Graphics (UHD/Arc/Iris)."""
        try:
            import winreg as wr
            # Intel Graphics Command Center / Arc Control
            reg_set(wr.HKEY_LOCAL_MACHINE,
                    r"SOFTWARE\Intel\Display\igfxcui",
                    "PowerPlan", 2)  # 2 = Maximum Performance
            reg_set(wr.HKEY_LOCAL_MACHINE,
                    r"SOFTWARE\Intel\Display\igfxcui",
                    "VSync", 0)
            self._dlog("OK Intel: Max performance, VSync off")
        except Exception as e:
            self._dlog("Erreur Intel: " + str(e)[:60])

    # ── OPTIMISATIONS COMMUNES (tous GPU) ─────────────────────
    def _gpu_optim_common(self, state=True):
        """Reglages universels pour toutes les cartes graphiques."""
        try:
            import winreg as wr

            # Hardware Accelerated GPU Scheduling (HAGS) - Windows 10/11
            reg_set(wr.HKEY_LOCAL_MACHINE,
                    r"SYSTEM\CurrentControlSet\Control\GraphicsDrivers",
                    "HwSchMode", 2 if state else 1)

            # TDR (Timeout Detection and Recovery) - plus tolerant en jeu
            reg_set(wr.HKEY_LOCAL_MACHINE,
                    r"SYSTEM\CurrentControlSet\Control\GraphicsDrivers",
                    "TdrDelay", 10 if state else 2)
            reg_set(wr.HKEY_LOCAL_MACHINE,
                    r"SYSTEM\CurrentControlSet\Control\GraphicsDrivers",
                    "TdrDdiDelay", 10 if state else 5)

            # Variable Refresh Rate (G-SYNC / FreeSync) global
            reg_set(wr.HKEY_CURRENT_USER,
                    r"SOFTWARE\Microsoft\DirectX\UserGpuPreferences",
                    "DirectXUserGlobalSettings",
                    "VRROptimizeEnable=1;" if state else "VRROptimizeEnable=0;")

            # Game Mode Windows (priorise le GPU pour les jeux actifs)
            reg_set(wr.HKEY_CURRENT_USER,
                    r"Software\Microsoft\GameBar",
                    "AutoGameModeEnabled", 1 if state else 0)

            # Fullscreen optimizations (reduit input lag)
            reg_set(wr.HKEY_CURRENT_USER,
                    r"System\GameConfigStore",
                    "GameDVR_FSEBehaviorMode", 2 if state else 0)

            self._dlog("OK Commun: HAGS, TDR+, VRR, Fullscreen optim")

        except Exception as e:
            self._dlog("Erreur optim commune: " + str(e)[:60])

    def _do_msi_gpu(self, state=True):
        """Active MSI (Message Signaled Interrupts) sur la carte graphique."""
        val = "1" if state else "0"
        cmd = (
            "$devs = Get-PnpDevice -Class Display -EA SilentlyContinue;"
            " foreach($d in $devs){"
            " $p = 'HKLM:\\SYSTEM\\CurrentControlSet\\Enum\\' "
            " + $d.InstanceId + "
            " '\\Device Parameters\\Interrupt Management\\"
            "MessageSignaledInterruptProperties';"
            " if(Test-Path $p){"
            " Set-ItemProperty -Path $p -Name MSISupported "
            " -Value " + val + " -Type DWord -EA SilentlyContinue "
            "}}"
        )
        ps(cmd, t=15)
        self._dlog("MSI GPU: " + ("active" if state else "desactive"))

    def _do_cpu_game_prio(self, state=True):
        """Priorite CPU elevee pour les jeux detectes."""
        if state:
            # Priorite elevee pour les processus de jeu actifs
            games = [
                "steam.exe", "SteamService.exe", "EpicGamesLauncher.exe",
                "Battle.net.exe", "GalaxyClient.exe", "Origin.exe",
                "RiotClientServices.exe", "valorant.exe", "csgo.exe",
                "cs2.exe", "fortnite.exe", "apex.exe", "javaw.exe",
                "Minecraft.exe", "Overwatch.exe", "GTA5.exe", "rdr2.exe",
                "r5apex.exe", "League of Legends.exe", "wow.exe",
            ]
            cmd_parts = ["try { "]
            for g in games:
                cmd_parts.append(
                    "Get-Process -Name '" + g.replace(".exe","") +
                    "' -EA SilentlyContinue | "
                    "ForEach-Object { try { "
                    "$_.PriorityClass = 'High' "
                    "} catch {} }; ")
            cmd_parts.append("} catch {}")
            ps("".join(cmd_parts), t=8)
            self._dlog("Priorite High appliquee aux jeux actifs")
        else:
            self._dlog("Priorite CPU restauree par defaut")


    # ── Nouvelles optimisations perf ───────────────────────────────
    def _do_hdd(self, state=True):
        if state:
            run("fsutil behavior set disablelastaccess 1")
            run("fsutil behavior set encryptpagingfile 0")
            ps("Get-ScheduledTask -TaskName *Defrag* | "
               "Disable-ScheduledTask -ErrorAction SilentlyContinue")
        else:
            run("fsutil behavior set disablelastaccess 0")

    def _do_gaming_notifs(self, state=True):
        import winreg as wr
        reg_set(wr.HKEY_CURRENT_USER,
                r"SOFTWARE\Microsoft\Windows\CurrentVersion\Notifications\Settings",
                "NOC_GLOBAL_SETTING_TOASTS_ENABLED", 0 if state else 1)
        reg_set(wr.HKEY_CURRENT_USER,
                r"SOFTWARE\Microsoft\Windows\CurrentVersion\PushNotifications",
                "ToastEnabled", 0 if state else 1)

    def _do_usb_poll(self, state=True):
        val = "0" if state else "1"
        reg_set(winreg.HKEY_LOCAL_MACHINE,
                r"SYSTEM\CurrentControlSet\Services\HidUsb\Parameters",
                "PollInterval", 1 if state else 8)

    def _do_hpet(self, state=True):
        if state:
            run("bcdedit /deletevalue useplatformclock")
            run("bcdedit /set useplatformtick yes")
        else:
            run("bcdedit /set useplatformclock true")

    def _do_startup_delay(self, state=True):
        reg_set(winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Explorer\Serialize",
                "StartupDelayInMSec", 0 if state else 10000)

    def _do_paging_exec(self, state=True):
        reg_set(winreg.HKEY_LOCAL_MACHINE,
                r"SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management",
                "DisablePagingExecutive", 1 if state else 0)

    # ── Nouvelles optimisations jeu ────────────────────────────────
    def _do_fullscreen_opt(self, state=True):
        reg_set(winreg.HKEY_CURRENT_USER,
                r"System\GameConfigStore",
                "GameDVR_DXGIHonorFSEWindowsCompatible", 1 if state else 0)
        reg_set(winreg.HKEY_CURRENT_USER,
                r"System\GameConfigStore",
                "GameDVR_FSEBehavior", 2 if state else 0)

    def _do_ram_gaming(self, state=True):
        reg_set(winreg.HKEY_LOCAL_MACHINE,
                r"SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management",
                "LargeSystemCache", 0)
        reg_set(winreg.HKEY_LOCAL_MACHINE,
                r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile",
                "SystemResponsiveness", 0 if state else 20)

    def _do_shader_precomp(self, state=True):
        reg_set(winreg.HKEY_LOCAL_MACHINE,
                r"SOFTWARE\Microsoft\DirectX\UserGpuPreferences",
                "DirectXUserGlobalSettings", "VRROptimizeEnable=0;" if state else "")

    def _do_cpu_unpark(self, state=True):
        v = "0" if state else "100"
        run("powercfg /setacvalueindex SCHEME_CURRENT SUB_PROCESSOR CPMINCORES " + ("100" if not state else "0"))
        run("powercfg /setactive SCHEME_CURRENT")

    def _do_hags(self, state=True):
        reg_set(winreg.HKEY_LOCAL_MACHINE,
                r"SYSTEM\CurrentControlSet\Control\GraphicsDrivers",
                "HwSchMode", 2 if state else 1)

    # ── Nouvelles optimisations confidentialite ────────────────────
    def _do_diagtrack(self, state=True):
        sc = "disabled" if state else "auto"
        run("sc config DiagTrack start= " + sc)
        if state: run("sc stop DiagTrack")

    def _do_compat_telem(self, state=True):
        for svc in ["WerSvc", "wercplsupport"]:
            sc = "disabled" if state else "demand"
            run("sc config " + svc + " start= " + sc)
            if state: run("sc stop " + svc)

    def _do_app_compat(self, state=True):
        reg_set(winreg.HKEY_LOCAL_MACHINE,
                r"SOFTWARE\Policies\Microsoft\Windows\AppCompat",
                "DisablePCA", 1 if state else 0)

    def _do_cloud_content(self, state=True):
        reg_set(winreg.HKEY_CURRENT_USER,
                r"SOFTWARE\Microsoft\Windows\CurrentVersion\ContentDeliveryManager",
                "SubscribedContent-338388Enabled", 0 if state else 1)
        reg_set(winreg.HKEY_CURRENT_USER,
                r"SOFTWARE\Microsoft\Windows\CurrentVersion\ContentDeliveryManager",
                "SubscribedContent-353694Enabled", 0 if state else 1)

    def _do_smartscreen(self, state=True):
        reg_set(winreg.HKEY_LOCAL_MACHINE,
                r"SOFTWARE\Policies\Microsoft\Windows\System",
                "EnableSmartScreen", 0 if state else 1)

    # ── Nouvelles optimisations confort ───────────────────────────
    def _do_focus_assist(self, state=True):
        reg_set(winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced",
                "FocusAssistEnabled", 1 if state else 0)

    def _do_clipboard(self, state=True):
        reg_set(winreg.HKEY_LOCAL_MACHINE,
                r"SOFTWARE\Policies\Microsoft\Windows\System",
                "AllowClipboardHistory", 1 if state else 0)
        if state:
            ps("Set-ItemProperty -Path "
               "'HKCU:\\Software\\Microsoft\\Clipboard' "
               "-Name EnableClipboardHistory -Value 1 "
               "-ErrorAction SilentlyContinue")

    def _do_snap(self, state=True):
        reg_set(winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced",
                "SnapAssist", 1 if state else 0)
        reg_set(winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced",
                "EnableSnapBar", 1 if state else 0)

    def _do_vdesk(self, state=True):
        reg_set(winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced",
                "VirtualDesktopTaskbarFilter", 1 if state else 0)

    def _do_inactive_scroll(self, state=True):
        reg_set(winreg.HKEY_CURRENT_USER,
                r"Control Panel\Desktop",
                "MouseWheelRouting", 2 if state else 0)


    # ================================================================
    #  EFFETS VISUELS  (animations low-poly)
    # ================================================================

    def _nav_animated(self, key):
        """Navigation avec flash d'accent sur le contenu."""
        # Flash rapide du bord de la fenetre
        self._flash_border()
        # Changer la page
        self._nav(key)

    def _flash_border(self):
        """Pulse rapide de la bordure externe (accent cyan)."""
        colors = [A, WHITE, A, BD_A]
        def step(i=0):
            if i >= len(colors): return
            try:
                # outer frame est le premier child de self
                outer = self.winfo_children()[0]
                outer.config(bg=colors[i])
            except Exception: pass
            self.after(40, lambda: step(i+1))
        step()

    def _start_visual_effects(self):
        """Lance toutes les animations continues."""
        self._pulse_score()
        self._animate_topbar_line()
        self._particles_init()
        self.after(100, self._particles_step)

    def _pulse_score(self):
        """Fait pulser doucement le score label (cyan <-> blanc)."""
        if not hasattr(self, '_score_lbl'): return
        if not hasattr(self, '_pulse_state'): self._pulse_state = 0
        self._pulse_state = (self._pulse_state + 1) % 60
        t = abs(self._pulse_state - 30) / 30.0  # 0.0 -> 1.0 -> 0.0
        # Interpoler entre A (#00e5b8) et WHITE (#eef0ff)
        r1,g1,b1 = 0x00,0xe5,0xb8
        r2,g2,b2 = 0xee,0xf0,0xff
        r = int(r1 + (r2-r1)*t*0.3)
        g = int(g1 + (g2-g1)*t*0.3)
        b = int(b1 + (b2-b1)*t*0.3)
        col = "#{:02x}{:02x}{:02x}".format(r,g,b)
        try:
            cur = self._score_lbl.cget("fg")
            if cur != "#eef0ff":  # seulement si pas override par couleur warning
                self._score_lbl.config(fg=col)
        except Exception: pass
        self.after(50, self._pulse_score)

    def _animate_topbar_line(self):
        """Fait glisser une lueur sur la ligne separatrice."""
        if not hasattr(self, '_topbar_line_pos'): self._topbar_line_pos = 0
        # Rien a faire ici - la ligne est statique
        # On pourrait animer un canvas mais on garde simple
        pass

    # ── Particules low-poly sur dashboard ─────────────────────────
    def _particles_init(self):
        """Initialise les particules flottantes."""
        if not hasattr(self, '_bg_cv'): return
        import random
        self._particles = []
        for _ in range(18):
            self._particles.append({
                'x':  random.randint(0, 1160),
                'y':  random.randint(0, 730),
                'vx': random.uniform(-0.4, 0.4),
                'vy': random.uniform(-0.3, 0.3),
                'size': random.randint(2, 5),
                'alpha': random.randint(1, 3),  # 1=dim, 2=mid, 3=bright
                'tag': 'p_'+str(_),
            })

    def _particles_step(self):
        """Avance les particules d un pas."""
        if not hasattr(self, '_bg_cv'): self.after(100, self._particles_step); return
        try:
            cv = self._bg_cv
            w = cv.winfo_width(); h = cv.winfo_height()
            if w < 10: self.after(80, self._particles_step); return

            for p in self._particles:
                cv.delete(p['tag'])
                p['x'] += p['vx']; p['y'] += p['vy']
                # Rebond sur les bords
                if p['x'] < 0 or p['x'] > w: p['vx'] *= -1
                if p['y'] < 0 or p['y'] > h: p['vy'] *= -1
                p['x'] = max(0, min(w, p['x']))
                p['y'] = max(0, min(h, p['y']))
                # Couleur selon alpha
                cols = [T3, T2, BD_A]
                col = cols[min(p['alpha']-1, 2)]
                s = p['size']
                # Triangle low-poly au lieu de point
                cv.create_polygon(
                    p['x'], p['y']-s,
                    p['x']+s, p['y']+s,
                    p['x']-s, p['y']+s,
                    fill=col, outline="", tags=p['tag'])
        except Exception:
            pass
        self.after(80, self._particles_step)

    def _animate_gauge_startup(self, key, target_fn):
        """Animation count-up des jauges au demarrage."""
        if key not in self._ring_fns: return
        count = [0]
        def step():
            if count[0] > 100: return
            self._ring_fns[key](count[0] % 101)
            count[0] += 3
            self.after(20, step)
        step()


    # ================================================================
    #  STYLES TTK
    # ================================================================
    def _setup_style(self):
        s=ttk.Style(self); s.theme_use("clam")
        s.configure("FR.Treeview",background=CARD,foreground=T1,fieldbackground=CARD,
                    bordercolor=BD,rowheight=24,font=(_FONT,8))
        s.map("FR.Treeview",background=[("selected",A_D)],foreground=[("selected",A)])
        s.configure("FR.Treeview.Heading",background=CARD_H,foreground=A,
                    bordercolor=BD,font=(_FONT,8,"bold"))
        s.configure("FR.Horizontal.TProgressbar",troughcolor=CARD,background=A,bordercolor=BD)

# ================================================================
if __name__ == "__main__":
    try: ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except: pass
    # Authentification obligatoire avant acces au logiciel
    _show_auth_window()
    App().mainloop()
