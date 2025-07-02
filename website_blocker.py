import tkinter as tk
from tkinter import Listbox, END
import os
import re
import sys
import ctypes

HOSTS_PATH = r"C:\Windows\System32\drivers\etc\hosts"
REDIRECT_IP = "127.0.0.1"

# Regex to match blocked sites (excluding .test domains)
BLOCKED_SITE_REGEX = re.compile(r"^127\.0\.0\.1\s+([\w.-]+)$", re.MULTILINE)

def custom_messagebox(root, title, message, icon="info", type="ok"):
    # icon: "info", "warning", "error", "question"
    # type: "ok", "yesno"
    win = tk.Toplevel(root)
    win.title(title)
    win.configure(bg="#282a36")
    win.resizable(False, False)
    win.grab_set()
    win.transient(root)

    # Centrage dynamique sur la fenêtre principale
    root.update_idletasks()
    root_x = root.winfo_rootx()
    root_y = root.winfo_rooty()
    root_w = root.winfo_width()
    root_h = root.winfo_height()
    win_w = 360
    win_h = 180
    x = root_x + (root_w // 2) - (win_w // 2)
    y = root_y + (root_h // 2) - (win_h // 2)
    win.geometry(f"{win_w}x{win_h}+{x}+{y}")

    icon_map = {
        "info": "\u2139",
        "warning": "\u26A0",
        "error": "\u2716",
        "question": "\u2753"
    }
    icon_label = tk.Label(win, text=icon_map.get(icon, ""), font=("Segoe UI", 32), bg="#282a36", fg="#50fa7b")
    icon_label.pack(pady=(18, 0))

    msg_label = tk.Label(win, text=message, font=("Segoe UI", 12), bg="#282a36", fg="#f8f8f2", wraplength=320, justify="center")
    msg_label.pack(padx=24, pady=(12, 18))

    result = {"value": None}

    def on_ok():
        result["value"] = True
        win.destroy()
    def on_cancel():
        result["value"] = False
        win.destroy()

    btn_frame = tk.Frame(win, bg="#282a36")
    btn_frame.pack(pady=(0, 18))
    if type == "ok":
        ok_btn = tk.Button(btn_frame, text="OK", font=("Segoe UI", 11, "bold"), bg="#44475a", fg="#f8f8f2",
                           activebackground="#6272a4", activeforeground="#f8f8f2", bd=0, relief="flat", width=10, command=on_ok)
        ok_btn.pack()
        win.bind("<Return>", lambda e: on_ok())
    elif type == "yesno":
        yes_btn = tk.Button(btn_frame, text="Oui", font=("Segoe UI", 11, "bold"), bg="#50fa7b", fg="#23272f",
                            activebackground="#6272a4", activeforeground="#f8f8f2", bd=0, relief="flat", width=10, command=on_ok)
        yes_btn.pack(side=tk.LEFT, padx=8)
        no_btn = tk.Button(btn_frame, text="Non", font=("Segoe UI", 11, "bold"), bg="#44475a", fg="#f8f8f2",
                           activebackground="#6272a4", activeforeground="#f8f8f2", bd=0, relief="flat", width=10, command=on_cancel)
        no_btn.pack(side=tk.LEFT, padx=8)
        win.bind("<Return>", lambda e: on_ok())
        win.bind("<Escape>", lambda e: on_cancel())

    win.wait_window()
    return result["value"]

def custom_askstring(root, title, prompt):
    win = tk.Toplevel(root)
    win.title(title)
    win.configure(bg="#282a36")
    win.resizable(False, False)
    win.grab_set()
    win.transient(root)

    # Centrage dynamique sur la fenêtre principale
    root.update_idletasks()
    root_x = root.winfo_rootx()
    root_y = root.winfo_rooty()
    root_w = root.winfo_width()
    root_h = root.winfo_height()
    win_w = 360
    win_h = 160
    x = root_x + (root_w // 2) - (win_w // 2)
    y = root_y + (root_h // 2) - (win_h // 2)
    win.geometry(f"{win_w}x{win_h}+{x}+{y}")

    label = tk.Label(win, text=prompt, font=("Segoe UI", 12), bg="#282a36", fg="#f8f8f2", wraplength=320, justify="center")
    label.pack(padx=24, pady=(18, 8))

    entry = tk.Entry(win, font=("Segoe UI", 12), bg="#44475a", fg="#f8f8f2", insertbackground="#f8f8f2", width=32, relief="flat")
    entry.pack(padx=24, pady=(0, 18))
    entry.focus_set()

    result = {"value": None}
    def on_ok():
        result["value"] = entry.get()
        win.destroy()
    def on_cancel():
        win.destroy()

    btn_frame = tk.Frame(win, bg="#282a36")
    btn_frame.pack(pady=(0, 18))
    ok_btn = tk.Button(btn_frame, text="Valider", font=("Segoe UI", 11, "bold"), bg="#50fa7b", fg="#23272f",
                       activebackground="#6272a4", activeforeground="#f8f8f2", bd=0, relief="flat", width=10, command=on_ok)
    ok_btn.pack(side=tk.LEFT, padx=8)
    cancel_btn = tk.Button(btn_frame, text="Annuler", font=("Segoe UI", 11, "bold"), bg="#44475a", fg="#f8f8f2",
                           activebackground="#6272a4", activeforeground="#f8f8f2", bd=0, relief="flat", width=10, command=on_cancel)
    cancel_btn.pack(side=tk.LEFT, padx=8)

    win.bind("<Return>", lambda e: on_ok())
    win.bind("<Escape>", lambda e: on_cancel())

    win.wait_window()
    return result["value"]

class WebsiteBlockerApp:
    def __init__(self, root):
        self.root = root
        # Fenêtre sans bordure et taille fixe
        self.root.overrideredirect(True)
        self.root.resizable(False, False)
        self.root.geometry("520x540")  # Taille fixe
        #self.root.title("Website Blocker")
        # Ajout d'une icône à la fenêtre principale (optionnel, Windows .ico)
        # self.root.iconbitmap("lock.ico")  # Si vous avez un .ico
        self.is_maximized = False
        self.normal_geometry = self.root.geometry()
        self.sites = []
        self.create_widgets()
        self.load_blocked_sites()

    def create_widgets(self):
        self.root.configure(bg="#23272f")

        # En-tête custom avec boutons réduire/aggrandir/fermer
        self.header_bar = tk.Frame(self.root, bg="#181a20", height=38)
        self.header_bar.pack(fill="x", side="top")
        self.header_bar.pack_propagate(False)

        # Icône bouclier dans l'en-tête
        icon_canvas = tk.Canvas(self.header_bar, width=32, height=32, bg="#181a20", highlightthickness=0)
        icon_canvas.pack(side=tk.LEFT, padx=(10, 0), pady=3)
        icon_canvas.create_polygon(
            16, 3, 29, 10, 26, 26, 16, 31, 6, 26, 3, 10,
            fill="#50fa7b", outline="#282a36", width=2
        )
        icon_canvas.create_line(16, 6, 16, 28, fill="#282a36", width=2)

        # Titre dans l'en-tête
        title = tk.Label(self.header_bar, text="Gestionnaire de blocage de sites web", font=("Segoe UI", 13, "bold"),
                         bg="#181a20", fg="#50fa7b")
        title.pack(side=tk.LEFT, padx=(10, 0))

        # Boutons réduire, aggrandir, fermer (style Windows)
        btn_style = {"bd": 0, "relief": "flat", "width": 3, "height": 1, "font": ("Segoe UI", 12, "bold")}
        close_btn = tk.Button(self.header_bar, text="✕", command=self.close_window,
                              bg="#181a20", fg="#ff5555", activebackground="#282a36", activeforeground="#ff5555", **btn_style, cursor="hand2")
        close_btn.pack(side=tk.RIGHT, padx=(0, 8), pady=4)
        maximize_btn = tk.Button(self.header_bar, text="🗖", command=self.toggle_maximize_window,
                                 bg="#181a20", fg="#f8f8f2", activebackground="#282a36", activeforeground="#50fa7b", **btn_style, cursor="hand2")
        maximize_btn.pack(side=tk.RIGHT, padx=(0, 2), pady=4)
        minimize_btn = tk.Button(self.header_bar, text="🗕", command=self.minimize_window,
                                 bg="#181a20", fg="#f8f8f2", activebackground="#282a36", activeforeground="#50fa7b", **btn_style, cursor="hand2")
        minimize_btn.pack(side=tk.RIGHT, padx=(0, 2), pady=4)

        # Permet de déplacer la fenêtre en glissant l'en-tête
        self.header_bar.bind("<ButtonPress-1>", self.start_move)
        self.header_bar.bind("<B1-Motion>", self.do_move)
        title.bind("<ButtonPress-1>", self.start_move)
        title.bind("<B1-Motion>", self.do_move)
        icon_canvas.bind("<ButtonPress-1>", self.start_move)
        icon_canvas.bind("<B1-Motion>", self.do_move)

        # Encadrement de la liste
        list_frame = tk.Frame(self.root, bg="#282a36", bd=2, relief="groove")
        list_frame.pack(padx=30, pady=(20, 10), fill="both", expand=True)  # fill both & expand

        self.listbox = Listbox(
            list_frame, width=50, font=("Segoe UI", 13), bg="#282a36", fg="#f8f8f2",
            selectbackground="#6272a4", selectforeground="#f8f8f2", borderwidth=0,
            highlightthickness=0, relief="flat", activestyle="none"
        )
        self.listbox.pack(padx=10, pady=10, fill="both", expand=True)  # fill both & expand

        # Scrollbar stylée
        scrollbar = tk.Scrollbar(
            list_frame, orient="vertical", command=self.listbox.yview,
            bg="#44475a", troughcolor="#23272f", bd=0, highlightthickness=0
        )
        scrollbar.pack(side="right", fill="y")
        self.listbox.config(yscrollcommand=scrollbar.set)

        # Permet au list_frame de propager la taille à ses enfants
        list_frame.pack_propagate(True)

        btn_frame = tk.Frame(self.root, bg="#23272f")
        btn_frame.pack(pady=10, fill="x")
        btn_frame.pack_propagate(False)
        btn_frame.grid_columnconfigure(0, weight=1)
        btn_frame.grid_columnconfigure(1, weight=1)

        style_btn = {"font": ("Segoe UI", 11, "bold"), "bg": "#44475a", "fg": "#f8f8f2", "activebackground": "#6272a4", "activeforeground": "#f8f8f2", "bd": 0, "relief": "flat", "width": 18, "height": 2, "cursor": "hand2"}

        self.add_btn = tk.Button(btn_frame, text="Ajouter un blocage", command=self.add_site, **style_btn)
        self.add_btn.grid(row=0, column=0, padx=8, pady=0, sticky="e")

        self.remove_btn = tk.Button(btn_frame, text="Supprimer le blocage", command=self.remove_site, **style_btn)
        self.remove_btn.grid(row=0, column=1, padx=8, pady=0, sticky="w")

        # Footer
        footer = tk.Label(self.root, text="par MultiHServices", font=("Segoe UI", 9), bg="#23272f", fg="#6272a4")
        footer.pack(side=tk.BOTTOM, pady=5, fill="x")  # fill x pour suivre la largeur

        # Ajout d'un binding pour resize dynamique
        self.root.bind("<Configure>", self.on_resize)

    def load_blocked_sites(self):
        self.sites = []
        self.listbox.delete(0, END)
        if not os.path.exists(HOSTS_PATH):
            custom_messagebox("Erreur", f"Fichier hosts introuvable: {HOSTS_PATH}", icon="error")
            return
        with open(HOSTS_PATH, "r", encoding="utf-8") as f:
            for line in f:
                match = BLOCKED_SITE_REGEX.match(line.strip())
                if match:
                    site = match.group(1)
                    if site.startswith("www."):
                        site = site[4:]
                    if not (site.endswith(".test") or site == "kubernetes.docker.internal") and site not in self.sites:
                        self.sites.append(site)
        for site in self.sites:
            self.listbox.insert(END, site)

    def add_site(self):
        site = custom_askstring(self.root, "Ajouter un site", "Nom du site à bloquer (ex: site.com):")
        if site:
            site = site.strip().lower()
            if site.startswith("www."):
                site = site[4:]
            # Vérifie que le site a une extension (ex: .com, .fr, etc.)
            if not re.match(r"^[\w.-]+\.[a-zA-Z]{2,}$", site):
                custom_messagebox(self.root, "Refusé", "Le site doit contenir une extension valide (ex: .com, .fr, .net, etc.)", icon="warning")
                return
            if site.endswith(".test") or site == "kubernetes.docker.internal":
                custom_messagebox(self.root, "Refusé", "Ce domaine ne peut pas être bloqué.", icon="warning")
                return
            if site in self.sites:
                custom_messagebox(self.root, "Déjà bloqué", f"{site} est déjà bloqué.", icon="info")
                return
            try:
                with open(HOSTS_PATH, "a", encoding="utf-8") as f:
                    f.write(f"{REDIRECT_IP} {site}\n")
                    f.write(f"{REDIRECT_IP} www.{site}\n")
                self.load_blocked_sites()
                custom_messagebox(self.root, "Succès", f"{site} bloqué avec succès.", icon="info")
            except PermissionError:
                custom_messagebox(self.root, "Erreur", "Permission refusée. Lancez ce programme en tant qu'administrateur.", icon="error")

    def remove_site(self):
        selection = self.listbox.curselection()
        if not selection:
            custom_messagebox(self.root, "Sélection", "Sélectionnez un site à débloquer.", icon="info")
            return
        site = self.listbox.get(selection[0])
        confirm = custom_messagebox(
            self.root,
            "Confirmation du déblocage",
            f"Voulez-vous vraiment débloquer {site} ?",
            icon="question",
            type="yesno"
        )
        if not confirm:
            return
        try:
            with open(HOSTS_PATH, "r", encoding="utf-8") as f:
                lines = f.readlines()
            with open(HOSTS_PATH, "w", encoding="utf-8") as f:
                for line in lines:
                    # Correction ici : 127\.0\.0\.1 au lieu de 127\.0\.1
                    if not (
                        re.match(rf"127\.0\.0\.1\s+{re.escape(site)}$", line.strip()) or
                        re.match(rf"127\.0\.0\.1\s+www\.{re.escape(site)}$", line.strip())
                    ):
                        f.write(line)
            # Rafraîchissement automatique après suppression
            self.load_blocked_sites()
            custom_messagebox(self.root, "Succès", f"{site} débloqué.", icon="info")
        except PermissionError:
            custom_messagebox(self.root, "Erreur", "Permission refusée. Lancez ce programme en tant qu'administrateur.", icon="error")

    # Fonctions pour déplacer la fenêtre
    def start_move(self, event):
        self.x = event.x
        self.y = event.y

    def do_move(self, event):
        x = event.x_root - self.x
        y = event.y_root - self.y
        self.root.geometry(f"+{x}+{y}")

    # Bouton réduire
    def minimize_window(self):
        self.root.update_idletasks()
        self.root.overrideredirect(False)
        self.root.iconify()
        self.root.after(10, lambda: self.root.overrideredirect(True))

    # Bouton aggrandir/restaurer
    def toggle_maximize_window(self):
        if not self.is_maximized:
            self.normal_geometry = self.root.geometry()
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()
            self.root.geometry(f"{screen_width}x{screen_height}+0+0")
            self.is_maximized = True
        else:
            self.root.geometry(self.normal_geometry)
            self.is_maximized = False
        # Force le redimensionnement des widgets
        self.root.update_idletasks()

    # Bouton fermer
    def close_window(self):
        self.root.destroy()

    def on_resize(self, event):
        # Ajuste la taille de la listbox si la fenêtre est agrandie
        # (optionnel, car pack(fill="both", expand=True) gère déjà la plupart des cas)
        pass

if __name__ == "__main__":
    # Vérifie si le script est lancé en tant qu'administrateur
    try:
        is_admin = ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        is_admin = False

    if not is_admin:
        pythonw = sys.executable.replace("python.exe", "pythonw.exe")
        if not os.path.exists(pythonw):
            pythonw = sys.executable
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", pythonw, '"' + __file__ + '"', None, 1)
        sys.exit()
        
    root = tk.Tk()
    app = WebsiteBlockerApp(root)
    root.update_idletasks()
    # Centrage de la fenêtre principale
    width = 520
    height = 540
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)
    root.geometry(f"{width}x{height}+{x}+{y}")
    root.deiconify()  # Réaffiche la fenêtre principale après configuration
    root.lift()  # Met la fenêtre au premier plan
    root.focus_force()  # Force le focus sur la fenêtre principale
    root.mainloop()
