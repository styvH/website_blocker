import sys
import os
import re
import ctypes
from PyQt5 import QtWidgets, QtCore, QtGui

HOSTS_PATH = r"C:\Windows\System32\drivers\etc\hosts"
REDIRECT_IP = "127.0.0.1"
BLOCKED_SITE_REGEX = re.compile(r"^127\.0\.0\.1\s+([\w.-]+)$", re.MULTILINE)

# Dialogues personnalisés
class CustomMessageBox(QtWidgets.QDialog):
    def __init__(self, parent, title, message, icon="info", type_="ok"):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.FramelessWindowHint)
        self.setStyleSheet("background-color: #282a36; color: #f8f8f2;")
        self.result = None
        layout = QtWidgets.QVBoxLayout(self)
        icon_map = {
            "info": "\u2139",
            "warning": "\u26A0",
            "error": "\u2716",
            "question": "\u2753"
        }
        icon_label = QtWidgets.QLabel(icon_map.get(icon, ""))
        icon_label.setAlignment(QtCore.Qt.AlignCenter)
        icon_label.setStyleSheet("font-size: 38px; color: #50fa7b;")
        layout.addWidget(icon_label)
        msg_label = QtWidgets.QLabel(message)
        msg_label.setAlignment(QtCore.Qt.AlignCenter)
        msg_label.setWordWrap(True)
        msg_label.setStyleSheet("font-size: 14px;")
        layout.addWidget(msg_label)
        btn_layout = QtWidgets.QHBoxLayout()
        if type_ == "ok":
            ok_btn = QtWidgets.QPushButton("OK")
            ok_btn.setStyleSheet("background:#44475a; color:#f8f8f2; font-weight:bold; padding:8px 24px; border:none;")
            ok_btn.clicked.connect(self.accept)
            btn_layout.addWidget(ok_btn)
        elif type_ == "yesno":
            yes_btn = QtWidgets.QPushButton("Oui")
            yes_btn.setStyleSheet("background:#50fa7b; color:#23272f; font-weight:bold; padding:8px 24px; border:none;")
            yes_btn.clicked.connect(self.accept)
            btn_layout.addWidget(yes_btn)
            no_btn = QtWidgets.QPushButton("Non")
            no_btn.setStyleSheet("background:#44475a; color:#f8f8f2; font-weight:bold; padding:8px 24px; border:none;")
            no_btn.clicked.connect(self.reject)
            btn_layout.addWidget(no_btn)
        layout.addLayout(btn_layout)
        self.setFixedSize(360, 180)
        self.setWindowModality(QtCore.Qt.ApplicationModal)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

    @staticmethod
    def show(parent, title, message, icon="info", type_="ok"):
        dlg = CustomMessageBox(parent, title, message, icon, type_)
        result = dlg.exec_()
        return result == QtWidgets.QDialog.Accepted

class CustomAskString(QtWidgets.QDialog):
    def __init__(self, parent, title, prompt):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.FramelessWindowHint)
        self.setStyleSheet("background-color: #282a36; color: #f8f8f2;")
        self.value = None
        layout = QtWidgets.QVBoxLayout(self)
        label = QtWidgets.QLabel(prompt)
        label.setAlignment(QtCore.Qt.AlignCenter)
        label.setStyleSheet("font-size: 14px;")
        layout.addWidget(label)
        self.entry = QtWidgets.QLineEdit()
        self.entry.setStyleSheet("background:#44475a; color:#f8f8f2; padding:8px; border:none; font-size:14px;")
        layout.addWidget(self.entry)
        btn_layout = QtWidgets.QHBoxLayout()
        ok_btn = QtWidgets.QPushButton("Valider")
        ok_btn.setStyleSheet("background:#50fa7b; color:#23272f; font-weight:bold; padding:8px 24px; border:none;")
        ok_btn.clicked.connect(self.accept)
        btn_layout.addWidget(ok_btn)
        cancel_btn = QtWidgets.QPushButton("Annuler")
        cancel_btn.setStyleSheet("background:#44475a; color:#f8f8f2; font-weight:bold; padding:8px 24px; border:none;")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)
        self.setFixedSize(360, 160)
        self.setWindowModality(QtCore.Qt.ApplicationModal)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

    @staticmethod
    def get(parent, title, prompt):
        dlg = CustomAskString(parent, title, prompt)
        if dlg.exec_() == QtWidgets.QDialog.Accepted:
            return dlg.entry.text()
        return None

class TitleBar(QtWidgets.QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.setFixedHeight(38)
        self.setStyleSheet("background:transparent;")
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(8, 0, 8, 0)
        # Icône bouclier
        icon = QtWidgets.QLabel()
        pix = QtGui.QPixmap(32, 32)
        pix.fill(QtCore.Qt.transparent)
        painter = QtGui.QPainter(pix)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.setBrush(QtGui.QColor("#50fa7b"))
        painter.setPen(QtGui.QPen(QtGui.QColor("#282a36"), 2))
        points = [QtCore.QPointF(16,3), QtCore.QPointF(29,10), QtCore.QPointF(26,26), QtCore.QPointF(16,31), QtCore.QPointF(6,26), QtCore.QPointF(3,10)]
        painter.drawPolygon(QtGui.QPolygonF(points))
        painter.setPen(QtGui.QPen(QtGui.QColor("#282a36"), 2))
        painter.drawLine(16,6,16,28)
        painter.end()
        icon.setPixmap(pix)
        icon.setStyleSheet("background:transparent;")
        layout.addWidget(icon)
        # Titre
        title = QtWidgets.QLabel("Gestionnaire de blocage de sites web")
        title.setStyleSheet("color:#50fa7b; font-size:15px; font-weight:bold; background:transparent;")
        layout.addWidget(title)
        layout.addStretch()
        # Boutons
        btn_style = (
            "QPushButton {border:none; background:transparent; color:#bcbcbc; font-size:16px; width:32px; height:32px;} "
            "QPushButton:hover {background:#44475a; color:#23272f;}"
        )
        self.min_btn = QtWidgets.QPushButton("🗕")
        self.min_btn.setStyleSheet(btn_style)
        self.min_btn.clicked.connect(self.parent.showMinimized)
        layout.addWidget(self.min_btn)
        self.max_btn = QtWidgets.QPushButton("🗖")
        self.max_btn.setStyleSheet(btn_style)
        self.max_btn.clicked.connect(self.toggle_max)
        layout.addWidget(self.max_btn)
        close_btn_style = (
            "QPushButton {border:none; background:transparent; color:#bcbcbc; font-size:16px; width:32px; height:32px;} "
            "QPushButton:hover {background:#ff5555; color:#fff;}"
        )
        self.close_btn = QtWidgets.QPushButton("✕")
        self.close_btn.setStyleSheet(close_btn_style)
        self.close_btn.clicked.connect(self.parent.close)
        layout.addWidget(self.close_btn)
        self._mouse_pos = None

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self._mouse_pos = event.globalPos() - self.parent.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if self._mouse_pos and event.buttons() == QtCore.Qt.LeftButton:
            self.parent.move(event.globalPos() - self._mouse_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        self._mouse_pos = None

    def toggle_max(self):
        if self.parent.isMaximized():
            self.parent.showNormal()
        else:
            self.parent.showMaximized()

class WebsiteBlockerApp(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setFixedSize(520, 540)
        self.setStyleSheet("background:#23272f;")
        self.setWindowIcon(QtGui.QIcon("app_icon.ico"))  # Ajout de l'icône à la fenêtre
        self.sites = []
        self.init_ui()
        self.load_blocked_sites()

    def init_ui(self):
        vbox = QtWidgets.QVBoxLayout(self)
        vbox.setContentsMargins(0,0,0,0)
        vbox.setSpacing(0)
        self.title_bar = TitleBar(self)
        vbox.addWidget(self.title_bar)
        # Liste
        list_frame = QtWidgets.QFrame()
        list_frame.setStyleSheet("background:#282a36; border:2px groove #44475a; border-radius:6px;")
        list_layout = QtWidgets.QVBoxLayout(list_frame)
        list_layout.setContentsMargins(10,10,10,10)
        self.listbox = QtWidgets.QListWidget()
        self.listbox.setStyleSheet("QListWidget {background:#282a36; color:#f8f8f2; font-size:15px; border:none;} QListWidget::item:selected {background:#6272a4; color:#f8f8f2;}")
        list_layout.addWidget(self.listbox)
        vbox.addWidget(list_frame, 1)
        # Boutons
        btn_frame = QtWidgets.QWidget()
        btn_layout = QtWidgets.QHBoxLayout(btn_frame)
        btn_layout.setContentsMargins(30,0,30,0)
        style_btn = "QPushButton {background:#44475a; color:#f8f8f2; font-weight:bold; font-size:13px; border:none; border-radius:5px; padding:12px 0;} QPushButton:hover {background:#6272a4;}"
        self.add_btn = QtWidgets.QPushButton("Ajouter un blocage")
        self.add_btn.setStyleSheet(style_btn)
        self.add_btn.clicked.connect(self.add_site)
        btn_layout.addWidget(self.add_btn)
        self.remove_btn = QtWidgets.QPushButton("Supprimer le blocage")
        self.remove_btn.setStyleSheet(style_btn)
        self.remove_btn.clicked.connect(self.remove_site)
        btn_layout.addWidget(self.remove_btn)
        vbox.addWidget(btn_frame)
        # Footer
        footer = QtWidgets.QLabel("par MultiHServices")
        footer.setAlignment(QtCore.Qt.AlignCenter)
        footer.setStyleSheet("color:#6272a4; font-size:11px;")
        vbox.addWidget(footer)

    def load_blocked_sites(self):
        self.sites = []
        self.listbox.clear()
        if not os.path.exists(HOSTS_PATH):
            CustomMessageBox.show(self, "Erreur", f"Fichier hosts introuvable: {HOSTS_PATH}", icon="error")
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
            self.listbox.addItem(site)

    def add_site(self):
        site = CustomAskString.get(self, "Ajouter un site", "Nom du site à bloquer (ex: site.com):")
        if site:
            site = site.strip().lower()
            if site.startswith("www."):
                site = site[4:]
            if not re.match(r"^[\w.-]+\.[a-zA-Z]{2,}$", site):
                CustomMessageBox.show(self, "Refusé", "Le site doit contenir une extension valide (ex: .com, .fr, .net, etc.)", icon="warning")
                return
            if site.endswith(".test") or site == "kubernetes.docker.internal":
                CustomMessageBox.show(self, "Refusé", "Ce domaine ne peut pas être bloqué.", icon="warning")
                return
            if site in self.sites:
                CustomMessageBox.show(self, "Déjà bloqué", f"{site} est déjà bloqué.", icon="info")
                return
            try:
                with open(HOSTS_PATH, "a", encoding="utf-8") as f:
                    f.write(f"{REDIRECT_IP} {site}\n")
                    f.write(f"{REDIRECT_IP} www.{site}\n")
                self.load_blocked_sites()
                CustomMessageBox.show(self, "Succès", f"{site} bloqué avec succès.", icon="info")
            except PermissionError:
                CustomMessageBox.show(self, "Erreur", "Permission refusée. Lancez ce programme en tant qu'administrateur.", icon="error")

    def remove_site(self):
        items = self.listbox.selectedItems()
        if not items:
            CustomMessageBox.show(self, "Sélection", "Sélectionnez un site à débloquer.", icon="info")
            return
        site = items[0].text()
        confirm = CustomMessageBox.show(
            self,
            "Confirmation du déblocage",
            f"Voulez-vous vraiment débloquer {site} ?",
            icon="question",
            type_="yesno"
        )
        if not confirm:
            return
        try:
            with open(HOSTS_PATH, "r", encoding="utf-8") as f:
                lines = f.readlines()
            with open(HOSTS_PATH, "w", encoding="utf-8") as f:
                for line in lines:
                    if not (
                        re.match(rf"127\.0\.0\.1\s+{re.escape(site)}$", line.strip()) or
                        re.match(rf"127\.0\.0\.1\s+www\.{re.escape(site)}$", line.strip())
                    ):
                        f.write(line)
            self.load_blocked_sites()
            CustomMessageBox.show(self, "Succès", f"{site} débloqué.", icon="info")
        except PermissionError:
            CustomMessageBox.show(self, "Erreur", "Permission refusée. Lancez ce programme en tant qu'administrateur.", icon="error")

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
    app = QtWidgets.QApplication(sys.argv)
    win = WebsiteBlockerApp()
    # Centrage de la fenêtre
    screen = app.primaryScreen().geometry()
    x = (screen.width() - win.width()) // 2
    y = (screen.height() - win.height()) // 2
    win.move(x, y)
    win.show()
    sys.exit(app.exec_())
