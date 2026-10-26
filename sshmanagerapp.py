#!/usr/bin/env python3
"""
SSH Manager App - graphical interface for sshmanager (Windows & Linux).
Interfaz gráfica de sshmanager: servidores guardados, dos paneles con arrastrar y soltar,
fila de transferencias y consola. Comparte servidores, fila y ajustes con la terminal.

Dependencies are installed automatically on first run.
Las dependencias se instalan solas la primera vez.
"""
from __future__ import annotations

import json
import os
import posixpath
import shutil
import subprocess
import sys
import threading
import time
from pathlib import Path

__version__ = "1.0.0"
REPO_URL = "https://github.com/superc839e/sshmanagerapp"
HERE = Path(__file__).resolve().parent
CORE_URL = "https://raw.githubusercontent.com/superc839e/sshmanager/main/sshmanager_core.py"
NEEDED_CORE_API = 1


# ───────────────── Localizar (o descargar) el núcleo de sshmanager ─────────


def _tui_dir() -> Path:
    if os.name == "nt":
        local = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
        return local / "sshmanager"
    return Path.home() / ".local/share/sshmanager"


def _download_core(dest_dir: Path) -> Path:
    import urllib.request

    es = (os.environ.get("LC_ALL") or os.environ.get("LANG") or "").lower().startswith("es")
    print("Descargando el núcleo de sshmanager ..." if es else "Downloading the sshmanager core ...")
    dest_dir.mkdir(parents=True, exist_ok=True)
    last = None
    for i in range(3):
        try:
            data = urllib.request.urlopen(CORE_URL, timeout=10).read()
            (dest_dir / "sshmanager_core.py").write_bytes(data)
            return dest_dir
        except Exception as e:  # noqa: BLE001
            last = e
            time.sleep(1.5 * (i + 1))
    print(f"ERROR: {last}")
    sys.exit(1)


def load_core():
    """Usa el núcleo de sshmanager si está instalado; si no, lo descarga junto a esta app."""
    import importlib

    candidates = [_tui_dir(), HERE, HERE / "core"]
    for d in candidates:
        if (d / "sshmanager_core.py").exists():
            sys.path.insert(0, str(d))
            mod = importlib.import_module("sshmanager_core")
            if getattr(mod, "CORE_API", 0) >= NEEDED_CORE_API:
                return mod
            sys.modules.pop("sshmanager_core", None)  # demasiado viejo: se prueba con otro
            sys.path.remove(str(d))
    sys.path.insert(0, str(_download_core(HERE / "core")))
    return importlib.import_module("sshmanager_core")


core = load_core()
tr = core.tr
APP_DIR = core.gui_install_paths()[0]
VENV_DIR = APP_DIR / "venv"
REQS = [("PySide6", "PySide6-Essentials>=6.5"), ("paramiko", "paramiko>=3.0")]
PROJECT = core.Project("sshmanagerapp", "superc839e/sshmanagerapp", ["sshmanagerapp.py"], "sshmanagerapp.py", HERE)

core.TR.update(
    {
        "g_app": ("SSH Manager App", "SSH Manager App"),
        "g_servers": ("Servidores", "Servers"),
        "g_new": ("Nuevo", "New"),
        "g_edit": ("Editar", "Edit"),
        "g_delete": ("Borrar", "Delete"),
        "g_connect": ("Conectar", "Connect"),
        "g_disconnect": ("Desconectar", "Disconnect"),
        "g_add_server": ("Añadir servidor", "Add server"),
        "g_welcome_title": ("Bienvenido a SSH Manager App", "Welcome to SSH Manager App"),
        "g_welcome_empty": (
            "Aún no tienes servidores. Añade el primero para empezar.",
            "You have no servers yet. Add your first one to get started.",
        ),
        "g_welcome_pick": (
            "Elige un servidor de la lista y pulsa Conectar (o haz doble clic).",
            "Pick a server from the list and press Connect (or double-click).",
        ),
        "g_modified": ("Modificado", "Modified"),
        "g_upload": ("Subir", "Upload"),
        "g_download": ("Bajar", "Download"),
        "g_upload_tip": ("Subir lo seleccionado del PC al servidor", "Upload the selection from this PC to the server"),
        "g_download_tip": ("Bajar lo seleccionado del servidor al PC", "Download the selection from the server to this PC"),
        "g_queue_add": ("A la fila", "Add to queue"),
        "g_mkdir": ("Carpeta nueva", "New folder"),
        "g_rename": ("Renombrar", "Rename"),
        "g_refresh": ("Actualizar", "Refresh"),
        "g_hidden": ("Ocultos", "Hidden"),
        "g_terminal": ("Abrir en terminal", "Open in terminal"),
        "g_terminal_short": ("Terminal", "Terminal"),
        "g_up_tip": ("Carpeta superior", "Parent folder"),
        "g_open": ("Abrir", "Open"),
        "g_tab_transfers": ("Transferencias", "Transfers"),
        "g_tab_console": ("Consola", "Console"),
        "g_q_start": ("Iniciar", "Start"),
        "g_q_stop": ("Detener", "Stop"),
        "g_q_retry": ("Reintentar fallidos", "Retry failed"),
        "g_q_remove": ("Quitar", "Remove"),
        "g_q_clear": ("Limpiar terminados", "Clear finished"),
        "g_cmd_placeholder": (
            "Escribe un comando para el servidor y pulsa Enter (se ejecuta en la carpeta abierta)",
            "Type a command for the server and press Enter (runs in the open folder)",
        ),
        "g_cmd_cancel": ("Cancelar comando", "Cancel command"),
        "g_menu_file": ("Archivo", "File"),
        "g_menu_view": ("Ver", "View"),
        "g_menu_tools": ("Herramientas", "Tools"),
        "g_menu_help": ("Ayuda", "Help"),
        "g_quit": ("Salir", "Quit"),
        "g_lang": ("Idioma", "Language"),
        "g_theme": ("Tema", "Theme"),
        "g_theme_auto": ("Automático", "Automatic"),
        "g_theme_light": ("Claro", "Light"),
        "g_theme_dark": ("Oscuro", "Dark"),
        "g_check_updates": ("Buscar actualizaciones de la app", "Check for app updates"),
        "g_update_tui": ("Actualizar sshmanager (terminal)", "Update sshmanager (terminal)"),
        "g_about": ("Acerca de", "About"),
        "g_about_text": (
            "SSH Manager App v{v}\\nInterfaz gráfica de sshmanager.\\nNúcleo sshmanager v{core}\\n{repo}",
            "SSH Manager App v{v}\\nGraphical interface for sshmanager.\\nsshmanager core v{core}\\n{repo}",
        ),
        "g_server_title": ("Servidor", "Server"),
        "g_browse": ("Examinar...", "Browse..."),
        "g_show_pass": ("Mostrar contraseña", "Show password"),
        "g_test": ("Probar conexión", "Test connection"),
        "g_test_ok": ("Conexión correcta", "Connection successful"),
        "g_test_fail": ("No se pudo conectar: {e}", "Could not connect: {e}"),
        "g_rename_prompt": ("Nuevo nombre para '{name}':", "New name for '{name}':"),
        "g_link_on": ("Terminal (TUI) conectada", "Terminal (TUI) connected"),
        "g_link_off": ("Terminal cerrada", "Terminal closed"),
        "g_update_available": (
            "Actualización disponible: v{v} (clic para instalar)",
            "Update available: v{v} (click to install)",
        ),
        "g_up_to_date": ("Tienes la última versión (v{v})", "You have the latest version (v{v})"),
        "g_update_done": (
            "Actualizado a v{v}. Cierra y abre la app de nuevo.",
            "Updated to v{v}. Close and reopen the app.",
        ),
        "g_no_tui": ("sshmanager (terminal) no está instalado.", "sshmanager (terminal) is not installed."),
        "g_drop_hint": (
            "Arrastra archivos de un panel al otro para transferirlos",
            "Drag files from one panel to the other to transfer them",
        ),
        "g_checking": ("Buscando actualizaciones...", "Checking for updates..."),
        "g_conn_error": ("No se pudo conectar", "Could not connect"),
        "g_not_connected": ("No hay conexión con el servidor", "Not connected to the server"),
        "g_no_display": (
            "No hay entorno gráfico (DISPLAY/WAYLAND_DISPLAY). Esta app necesita un escritorio; en un servidor usa 'sshmanager' (terminal).",
            "No graphical environment (DISPLAY/WAYLAND_DISPLAY). This app needs a desktop; on a server use 'sshmanager' (terminal).",
        ),
        "g_qt_libs": (
            "Faltan librerías del sistema para abrir la ventana: {libs}",
            "System libraries needed to open the window are missing: {libs}",
        ),
        "g_qt_install": ("Instálalas con: {cmd}", "Install them with: {cmd}"),
        "g_d_qt": ("Librerías del sistema para Qt", "System libraries for Qt"),
        "g_selected": ("{n} seleccionado(s)", "{n} selected"),
    }
)

# ───────────────────────── Línea de comandos ──────────────────────────────

MANUAL_ES = """\
SSH Manager App v{ver} - interfaz gráfica de sshmanager

USO
  sshmanagerapp                   Abre la aplicación
  sshmanagerapp --connect NOMBRE  Abre y conecta directo a un servidor guardado
  sshmanagerapp --tui [NOMBRE]    Abre sshmanager (terminal), opcionalmente en un servidor
  sshmanagerapp -h [es|en]        Muestra este manual
  sshmanagerapp -v                Muestra la versión
  sshmanagerapp -u                Actualiza la app desde GitHub
  sshmanagerapp -d                Desinstala la app (no toca tus servidores)
  sshmanagerapp -l [es|en]        Muestra o cambia el idioma
  sshmanagerapp --doctor          Diagnostica problemas comunes
  sshmanagerapp --repair          Repara las dependencias (limpia caché y reinstala)

QUÉ HACE
  - Servidores guardados con nombre (los mismos que en la terminal).
  - Dos paneles: tu PC y el servidor. Arrastra archivos de uno al otro para
    transferirlos, o usa Subir / Bajar. También puedes arrastrar desde el
    explorador de archivos de tu sistema al panel del servidor.
  - Fila de transferencias con progreso; recuerda de dónde viene cada archivo
    y a dónde va, y lo pendiente se guarda al cerrar.
  - Consola: ver lo que pasa y ejecutar comandos en el servidor.
  - Menú Ver: idioma (español/inglés) y tema (claro/oscuro).

DEPENDENCIAS AUTOMÁTICAS
  La primera vez instala solo lo que falta (PySide6 y paramiko) y corrige los
  errores comunes de descarga. En Linux avisa si faltan librerías del sistema
  y te dice el comando exacto. Prueba --doctor y --repair.

ENLACE CON LA TERMINAL (sshmanager)
  Usan los mismos servidores, fila y ajustes. Si ambas están abiertas, se
  avisan al instante los cambios, y cada una puede abrir la otra.

Proyecto: {repo}
"""

MANUAL_EN = """\
SSH Manager App v{ver} - graphical interface for sshmanager

USAGE
  sshmanagerapp                   Open the application
  sshmanagerapp --connect NAME    Open and connect straight to a saved server
  sshmanagerapp --tui [NAME]      Open sshmanager (terminal), optionally on a server
  sshmanagerapp -h [es|en]        Show this manual
  sshmanagerapp -v                Show the version
  sshmanagerapp -u                Update the app from GitHub
  sshmanagerapp -d                Uninstall the app (your servers are kept)
  sshmanagerapp -l [es|en]        Show or change the language
  sshmanagerapp --doctor          Diagnose common problems
  sshmanagerapp --repair          Repair dependencies (clear cache and reinstall)

WHAT IT DOES
  - Saved servers with names (the same ones as in the terminal).
  - Two panels: your PC and the server. Drag files from one to the other to
    transfer them, or use Upload / Download. You can also drag from your
    system's file manager onto the server panel.
  - Transfer queue with progress; it remembers where each file comes from and
    where it goes, and pending items are saved when you close.
  - Console: see what happens and run commands on the server.
  - View menu: language (Spanish/English) and theme (light/dark).

AUTOMATIC DEPENDENCIES
  On first run it installs only what is missing (PySide6 and paramiko) and
  fixes common download errors. On Linux it warns about missing system
  libraries and tells you the exact command. Try --doctor and --repair.

LINK WITH THE TERMINAL (sshmanager)
  They share the same servers, queue and settings. If both are open they
  notify each other instantly about changes, and each can open the other.

Project: {repo}
"""


def manual(lang: str | None = None) -> str:
    text = MANUAL_ES if (lang or core.LANG) == "es" else MANUAL_EN
    return text.format(ver=__version__, repo=REPO_URL)


def cli_update() -> int:
    print(tr("cli_checking", cur=__version__).replace("SSH Manager", "SSH Manager App"))
    try:
        remote, src = core.fetch_update(PROJECT, __version__)
    except core.NetworkError as e:
        print(tr("cli_net_err", e=e))
        return 1
    except core.UpdateError as e:
        print(f"ERROR {e}")
        return 1
    if src is None:
        print(tr("cli_latest", cur=__version__))
        return 0
    print(tr("cli_new", v=remote))
    try:
        core.apply_update(PROJECT, src)
    except Exception as e:  # noqa: BLE001
        print(tr("cli_update_fail", e=e))
        return 1
    print(tr("cli_updated", v=remote))
    return 0


def cli_uninstall() -> int:
    app_dir, launcher = core.gui_install_paths()
    extras = [Path.home() / ".local/share/applications/sshmanagerapp.desktop"] if os.name != "nt" else []
    has_app = (app_dir / "sshmanagerapp.py").exists()
    found = [p for p in [launcher] + extras if p.exists()]
    if not (has_app or found):
        print(tr("cli_no_install"))
        return 1
    print(tr("cli_will_remove"))
    for p in ([app_dir] if has_app else []) + found:
        print(f"  - {p}")
    try:
        ans = input(f"{tr('cli_ask_uninstall')} {tr('yn')} ").strip().lower()
    except EOFError:
        ans = ""
    if ans not in tr("yes_words"):
        print(tr("cli_cancelled"))
        return 0
    if os.name == "nt":
        parts = ["ping -n 3 127.0.0.1 >nul"]
        if has_app:
            parts.append(f'rmdir /s /q "{app_dir}"')
        parts += [f'del /f /q "{p}"' for p in found]
        subprocess.Popen('cmd /c "' + " & ".join(parts) + '"', creationflags=0x08000000 | 0x00000008, close_fds=True)
        print(tr("cli_win_wait"))
    else:
        for p in found:
            p.unlink()
        if has_app:
            shutil.rmtree(app_dir)
    print(tr("cli_uninstalled") + tr("cli_kept"))
    return 0


def cli_lang(value):
    if value is None:
        print(tr("cli_lang_now", l=core.LANG))
        return 0
    if value not in core.LANGS:
        print(tr("cli_lang_bad"))
        return 2
    core.apply_settings(value, core.CHARS)
    print(tr("cli_lang_set", l=core.LANG_NAMES[value]))
    return 0


def cli_tui(name):
    ok, msg = core.launch_tui(name)
    print(msg)
    return 0 if ok else 1


def early_cli(args: list):
    """Comandos que no necesitan la ventana ni las dependencias."""
    if not args:
        return None
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:  # noqa: BLE001
            pass
    a, arg = args[0], (args[1] if len(args) > 1 else None)
    if a in ("-h", "--help"):
        print(manual(arg if arg in core.LANGS else None))
        return 0
    if a in ("-v", "--version"):
        print(f"SSH Manager App v{__version__}")
        return 0
    if a in ("-u", "--update"):
        return cli_update()
    if a in ("-d", "--delete", "--uninstall"):
        return cli_uninstall()
    if a in ("-l", "--lang"):
        return cli_lang(arg)
    if a == "--tui":
        return cli_tui(arg)
    if a == "--check-system":  # lo usa el instalador: avisa de librerías del sistema que falten
        libs = missing_qt_libs()
        if libs:
            print("\n".join(qt_hint_lines(libs)))
        return 0
    if a == "--doctor":
        code = core.doctor("SSH Manager App", REQS, "tui")
        libs = missing_qt_libs()
        print(f"  [{'FAIL' if libs else 'OK'}] {tr('g_d_qt')}" + (f": {', '.join(libs)}" if libs else ""))
        return 1 if (code or libs) else 0
    if a == "--repair":
        return core.repair_dependencies(REQS, VENV_DIR)
    if a == "--install-deps":
        already = not core.modules_missing(REQS)
        core.ensure_dependencies(REQS, str(Path(__file__).resolve()), [], VENV_DIR)
        if already:
            print(tr("deps_ok"))
        return 0
    if a == "--connect":
        return None
    print(tr("cli_unknown", a=a).replace("sshmanager -h", "sshmanagerapp -h"))
    return 2


# Librerías del sistema que Qt necesita en Linux (X11) y su paquete según la distribución
QT_LIB_PACKAGES = {
    "libxcb-cursor.so.0": {"debian": "libxcb-cursor0", "arch": "xcb-util-cursor", "fedora": "xcb-util-cursor", "suse": "libxcb-cursor0"},
    "libxkbcommon-x11.so.0": {"debian": "libxkbcommon-x11-0", "arch": "libxkbcommon-x11", "fedora": "libxkbcommon-x11", "suse": "libxkbcommon-x11-0"},
    "libxcb-icccm.so.4": {"debian": "libxcb-icccm4", "arch": "xcb-util-wm", "fedora": "xcb-util-wm", "suse": "libxcb-icccm4"},
    "libxcb-image.so.0": {"debian": "libxcb-image0", "arch": "xcb-util-image", "fedora": "xcb-util-image", "suse": "libxcb-image0"},
    "libxcb-keysyms.so.1": {"debian": "libxcb-keysyms1", "arch": "xcb-util-keysyms", "fedora": "xcb-util-keysyms", "suse": "libxcb-keysyms1"},
    "libxcb-render-util.so.0": {"debian": "libxcb-render-util0", "arch": "xcb-util-renderutil", "fedora": "xcb-util-renderutil", "suse": "libxcb-render-util0"},
    "libxcb-shape.so.0": {"debian": "libxcb-shape0", "arch": "libxcb", "fedora": "libxcb", "suse": "libxcb-shape0"},
    "libxcb-xinerama.so.0": {"debian": "libxcb-xinerama0", "arch": "libxcb", "fedora": "libxcb", "suse": "libxcb-xinerama0"},
    "libxcb-xkb.so.1": {"debian": "libxcb-xkb1", "arch": "libxcb", "fedora": "libxcb", "suse": "libxcb-xkb1"},
    "libEGL.so.1": {"debian": "libegl1", "arch": "libglvnd", "fedora": "libglvnd-egl", "suse": "libEGL1"},
    "libGL.so.1": {"debian": "libgl1", "arch": "libglvnd", "fedora": "libglvnd-glx", "suse": "libGL1"},
    "libfontconfig.so.1": {"debian": "libfontconfig1", "arch": "fontconfig", "fedora": "fontconfig", "suse": "libfontconfig1"},
}


def distro_family() -> str:
    try:
        text = Path("/etc/os-release").read_text().lower()
    except OSError:
        return "debian"
    ids = " ".join(l.split("=", 1)[1].strip('"') for l in text.splitlines() if l.startswith(("id=", "id_like=")))
    for fam, keys in (("arch", ("arch", "cachyos", "manjaro", "endeavouros")), ("fedora", ("fedora", "rhel", "centos")),
                      ("suse", ("suse",)), ("debian", ("debian", "ubuntu", "mint", "pop"))):
        if any(k in ids for k in keys):
            return fam
    return "debian"


def missing_qt_libs() -> list:
    """Librerías que le faltan al plugin gráfico de Qt (Linux): lista de nombres de .so."""
    if not sys.platform.startswith("linux") or not shutil.which("ldd"):
        return []
    try:
        import PySide6

        plugin = Path(PySide6.__file__).parent / "Qt" / "plugins" / "platforms" / "libqxcb.so"
        if not plugin.exists():
            return []
        out = subprocess.run(["ldd", str(plugin)], capture_output=True, text=True, timeout=30).stdout
    except Exception:  # noqa: BLE001
        return []
    return list(dict.fromkeys(ln.split("=>")[0].strip() for ln in out.splitlines() if "not found" in ln))


def qt_hint_lines(libs: list) -> list:
    fam = distro_family()
    pkgs = sorted({QT_LIB_PACKAGES.get(l, {}).get(fam, "") for l in libs} - {""})
    cmd = {"debian": "sudo apt install ", "arch": "sudo pacman -S ", "fedora": "sudo dnf install ", "suse": "sudo zypper install "}[fam]
    lines = [tr("g_qt_libs", libs=", ".join(libs))]
    if pkgs:
        lines.append(tr("g_qt_install", cmd=cmd + " ".join(pkgs)))
    return lines


def qt_preflight() -> None:
    """En Linux: avisa antes de abrir la ventana si falta algo del sistema (Qt aborta sin explicar)."""
    if not sys.platform.startswith("linux") or os.environ.get("QT_QPA_PLATFORM"):
        return
    wayland, x11 = bool(os.environ.get("WAYLAND_DISPLAY")), bool(os.environ.get("DISPLAY"))
    if not wayland and not x11:
        print(tr("g_no_display"))
        sys.exit(1)
    if wayland:
        return  # Qt usa su plugin de Wayland, que no necesita estas librerías
    libs = missing_qt_libs()
    if libs:
        print("\n".join(qt_hint_lines(libs)))
        sys.exit(1)


if __name__ == "__main__":
    _args = sys.argv[1:]
    _code = early_cli(_args)
    if _code is not None:
        sys.exit(_code)
    core.ensure_dependencies(REQS, str(Path(__file__).resolve()), _args, VENV_DIR)
    qt_preflight()

# ───────────────────────── Interfaz gráfica (PySide6) ─────────────────────

import html  # noqa: E402

import paramiko  # noqa: E402
from PySide6.QtCore import QByteArray, QMimeData, QObject, QPointF, QSize, Qt, QTimer, Signal  # noqa: E402
from PySide6.QtGui import QAction, QColor, QFont, QIcon, QKeySequence, QLinearGradient, QPainter, QPalette, QPixmap  # noqa: E402
from PySide6.QtWidgets import (  # noqa: E402
    QAbstractItemView,
    QApplication,
    QDialog,
    QFileDialog,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QInputDialog,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMenu,
    QMessageBox,
    QPlainTextEdit,
    QProgressBar,
    QPushButton,
    QSpinBox,
    QSplitter,
    QStackedWidget,
    QStyle,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QToolBar,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
    QCheckBox,
    QDialogButtonBox,
)

MIME = "application/x-sshmanager-items"
STATUS_COLOR = {"pendiente": "#d9a300", "en curso": "#2a82da", "listo": "#2e9e4f", "error": "#d9534f"}
STATUS_KEY = {"pendiente": "s_pending", "en curso": "s_running", "listo": "s_done", "error": "s_error"}
LOG_COLORS = {"red": "#e5534b", "yellow": "#d9a300", "green": "#3fb950", "dim": "#8b949e", "bold green": "#3fb950"}


class Bridge(QObject):
    """Permite ejecutar una función en el hilo de la interfaz desde cualquier otro hilo."""

    call = Signal(object)

    def __init__(self):
        super().__init__()
        self.call.connect(self._run, Qt.QueuedConnection)

    def _run(self, fn):
        try:
            fn()
        except Exception as e:  # noqa: BLE001
            print("UI error:", repr(e), file=sys.stderr)


BRIDGE: Bridge | None = None


def ui(fn) -> None:
    BRIDGE.call.emit(fn)


def run_bg(work, on_ok=None, on_err=None) -> None:
    """Ejecuta work() en un hilo; el resultado vuelve al hilo de la interfaz."""

    def job():
        try:
            res = work()
        except Exception as e:  # noqa: BLE001
            err = e  # 'e' se borra al salir del except: el callback necesita su propia copia
            if on_err:
                ui(lambda: on_err(err))
            return
        if on_ok:
            ui(lambda: on_ok(res))

    threading.Thread(target=job, daemon=True).start()


def fmt_time(ts: float) -> str:
    return time.strftime("%Y-%m-%d %H:%M", time.localtime(ts)) if ts else ""


def make_app_icon() -> QIcon:
    pm = QPixmap(256, 256)
    pm.fill(Qt.transparent)
    p = QPainter(pm)
    p.setRenderHint(QPainter.Antialiasing)
    g = QLinearGradient(QPointF(0, 0), QPointF(256, 256))
    g.setColorAt(0, QColor("#3b82f6"))
    g.setColorAt(1, QColor("#1e40af"))
    p.setBrush(g)
    p.setPen(Qt.NoPen)
    p.drawRoundedRect(8, 8, 240, 240, 52, 52)
    p.setPen(QColor("white"))
    f = QFont("monospace")
    f.setStyleHint(QFont.Monospace)
    f.setBold(True)
    f.setPixelSize(120)
    p.setFont(f)
    p.drawText(pm.rect(), Qt.AlignCenter, ">_")
    p.end()
    return QIcon(pm)


def dark_palette() -> QPalette:
    p = QPalette()
    for role, c in {
        QPalette.Window: (45, 48, 54), QPalette.WindowText: (230, 230, 230), QPalette.Base: (30, 32, 36),
        QPalette.AlternateBase: (38, 41, 46), QPalette.ToolTipBase: (60, 63, 70), QPalette.ToolTipText: (230, 230, 230),
        QPalette.Text: (230, 230, 230), QPalette.Button: (58, 61, 68), QPalette.ButtonText: (230, 230, 230),
        QPalette.BrightText: (255, 80, 80), QPalette.Link: (88, 166, 255), QPalette.Highlight: (47, 111, 214),
        QPalette.HighlightedText: (255, 255, 255), QPalette.PlaceholderText: (140, 144, 152),
    }.items():
        p.setColor(role, QColor(*c))
    for role in (QPalette.WindowText, QPalette.Text, QPalette.ButtonText):
        p.setColor(QPalette.Disabled, role, QColor(120, 124, 132))
    return p


def light_palette() -> QPalette:
    p = QPalette()
    for role, c in {
        QPalette.Window: (241, 243, 246), QPalette.WindowText: (30, 32, 36), QPalette.Base: (255, 255, 255),
        QPalette.AlternateBase: (246, 248, 250), QPalette.ToolTipBase: (255, 255, 220), QPalette.ToolTipText: (30, 32, 36),
        QPalette.Text: (30, 32, 36), QPalette.Button: (232, 235, 240), QPalette.ButtonText: (30, 32, 36),
        QPalette.BrightText: (200, 30, 30), QPalette.Link: (9, 105, 218), QPalette.Highlight: (47, 111, 214),
        QPalette.HighlightedText: (255, 255, 255), QPalette.PlaceholderText: (120, 124, 132),
    }.items():
        p.setColor(role, QColor(*c))
    for role in (QPalette.WindowText, QPalette.Text, QPalette.ButtonText):
        p.setColor(QPalette.Disabled, role, QColor(150, 154, 160))
    return p


STYLE = """
QToolBar { spacing: 4px; padding: 4px; border: none; }
QToolButton { padding: 4px 6px; border-radius: 6px; }
QToolButton:hover { background: palette(midlight); }
QToolButton:checked { background: palette(highlight); color: palette(highlighted-text); }
QListWidget#servers { border: none; background: transparent; outline: 0; }
QListWidget#servers::item { padding: 8px 10px; margin: 2px 4px; border-radius: 8px; }
QListWidget#servers::item:selected { background: palette(highlight); color: palette(highlighted-text); }
QTreeWidget, QTableWidget, QPlainTextEdit { border: 1px solid palette(mid); border-radius: 6px; }
QLabel#paneTitle { font-weight: bold; padding: 2px 2px; }
QLabel#h1 { font-size: 22px; font-weight: bold; }
QLabel#muted { color: palette(placeholder-text); }
QPushButton { padding: 5px 12px; border-radius: 6px; border: 1px solid palette(mid); background: palette(button); }
QPushButton:hover { border-color: palette(highlight); }
QPushButton#primary { background: palette(highlight); color: palette(highlighted-text); border-color: palette(highlight); }
QLineEdit { padding: 4px 6px; border-radius: 6px; border: 1px solid palette(mid); }
QLineEdit:focus { border-color: palette(highlight); }
QProgressBar { border: 1px solid palette(mid); border-radius: 5px; text-align: center; height: 14px; }
QProgressBar::chunk { background: palette(highlight); border-radius: 4px; }
QTabBar::tab { padding: 6px 14px; }
QStatusBar QLabel { padding: 0 6px; }
"""


# ───────────────────────────── Diálogo de servidor ────────────────────────


class ServerDialog(QDialog):
    def __init__(self, parent, srv: dict | None = None):
        super().__init__(parent)
        s = srv or {}
        self.setWindowTitle(tr("g_server_title"))
        self.setMinimumWidth(440)
        self.name = QLineEdit(s.get("name", ""))
        self.host = QLineEdit(s.get("host", ""))
        self.port = QSpinBox()
        self.port.setRange(1, 65535)
        self.port.setValue(int(s.get("port", 22)))
        self.user = QLineEdit(s.get("user", ""))
        self.password = QLineEdit(s.get("password", ""))
        self.password.setEchoMode(QLineEdit.Password)
        self.show_pass = QCheckBox(tr("g_show_pass"))
        self.show_pass.toggled.connect(lambda on: self.password.setEchoMode(QLineEdit.Normal if on else QLineEdit.Password))
        self.key = QLineEdit(s.get("key", ""))
        browse = QPushButton(tr("g_browse"))
        browse.clicked.connect(self._browse)
        keyrow = QHBoxLayout()
        keyrow.addWidget(self.key, 1)
        keyrow.addWidget(browse)
        form = QFormLayout()
        form.addRow(tr("f_name"), self.name)
        form.addRow(tr("f_host"), self.host)
        form.addRow(tr("f_port"), self.port)
        form.addRow(tr("f_user"), self.user)
        form.addRow(tr("f_pass"), self.password)
        form.addRow("", self.show_pass)
        form.addRow(tr("f_key"), keyrow)
        self.result_label = QLabel("")
        self.result_label.setWordWrap(True)
        test = QPushButton(tr("g_test"))
        test.clicked.connect(self._test)
        buttons = QDialogButtonBox()
        ok = buttons.addButton(tr("save"), QDialogButtonBox.AcceptRole)
        ok.setObjectName("primary")
        buttons.addButton(tr("cancel"), QDialogButtonBox.RejectRole)
        buttons.accepted.connect(self._accept)
        buttons.rejected.connect(self.reject)
        lay = QVBoxLayout(self)
        lay.addLayout(form)
        row = QHBoxLayout()
        row.addWidget(test)
        row.addWidget(self.result_label, 1)
        lay.addLayout(row)
        lay.addWidget(buttons)

    def _browse(self):
        path, _ = QFileDialog.getOpenFileName(self, tr("f_key"), str(Path.home() / ".ssh"))
        if path:
            self.key.setText(path)

    def data(self) -> dict:
        return {
            "name": self.name.text().strip(),
            "host": self.host.text().strip(),
            "port": self.port.value(),
            "user": self.user.text().strip(),
            "password": self.password.text(),
            "key": self.key.text().strip(),
        }

    def _accept(self):
        d = self.data()
        if not (d["name"] and d["host"] and d["user"]):
            QMessageBox.warning(self, tr("g_server_title"), tr("form_required"))
            return
        self.accept()

    def _test(self):
        d = self.data()
        if not (d["host"] and d["user"]):
            self.result_label.setText(tr("form_required"))
            return
        self.result_label.setText(tr("connecting", name=d["host"]))

        def work():
            c = core.Connection(d)
            c.close()

        run_bg(
            work,
            lambda _r: self.result_label.setText("OK  " + tr("g_test_ok")),
            lambda e: self.result_label.setText(tr("g_test_fail", e=str(e) or type(e).__name__)),
        )


# ───────────────────────────── Panel de archivos ──────────────────────────


class FileTree(QTreeWidget):
    """Lista de archivos que se puede arrastrar hacia el otro panel (o desde el explorador del sistema)."""

    dropped = Signal(dict, str)  # datos del arrastre, carpeta de destino dentro del panel ('' = la actual)
    dropped_files = Signal(list, str)  # rutas locales soltadas desde fuera de la app

    def __init__(self, pane: "FilePane"):
        super().__init__()
        self.pane = pane
        self.setColumnCount(3)
        self.setRootIsDecorated(False)
        self.setAlternatingRowColors(True)
        self.setUniformRowHeights(True)
        self.setAllColumnsShowFocus(True)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setDragDropMode(QAbstractItemView.DragDrop)
        self.setDefaultDropAction(Qt.CopyAction)
        self.header().setStretchLastSection(False)
        self.header().setSectionResizeMode(0, QHeaderView.Stretch)
        self.header().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.header().setSectionResizeMode(2, QHeaderView.ResizeToContents)

    def supportedDropActions(self):
        return Qt.CopyAction

    def mimeTypes(self):
        return [MIME, "text/uri-list"]

    def mimeData(self, items):
        names = [i.data(0, Qt.UserRole)["name"] for i in items if i.data(0, Qt.UserRole)["name"] != ".."]
        md = QMimeData()
        payload = {"kind": self.pane.kind, "dir": self.pane.path, "names": names}
        md.setData(MIME, QByteArray(json.dumps(payload).encode("utf-8")))
        return md

    def _acceptable(self, md) -> bool:
        if md.hasFormat(MIME):
            return json.loads(bytes(md.data(MIME)).decode("utf-8")).get("kind") != self.pane.kind
        return md.hasUrls() and self.pane.kind == "remote"

    def dragEnterEvent(self, e):
        e.acceptProposedAction() if self._acceptable(e.mimeData()) else e.ignore()

    def dragMoveEvent(self, e):
        e.acceptProposedAction() if self._acceptable(e.mimeData()) else e.ignore()

    def dropEvent(self, e):
        md = e.mimeData()
        if not self._acceptable(md):
            e.ignore()
            return
        item = self.itemAt(e.position().toPoint())
        sub = ""
        if item is not None:
            d = item.data(0, Qt.UserRole)
            if d["is_dir"] and d["name"] != "..":
                sub = d["name"]  # soltado sobre una carpeta: va dentro de ella
        if md.hasFormat(MIME):
            self.dropped.emit(json.loads(bytes(md.data(MIME)).decode("utf-8")), sub)
        else:
            self.dropped_files.emit([u.toLocalFile() for u in md.urls() if u.isLocalFile()], sub)
        e.acceptProposedAction()


class FilePane(QWidget):
    """Un panel: 'local' (tu PC) o 'remote' (el servidor)."""

    focused = Signal(object)

    def __init__(self, win: "MainWindow", kind: str):
        super().__init__()
        self.win, self.kind = win, kind
        self.path = ""
        self.items: list = []
        self.entries: dict = {}
        self._seq = 0
        st = self.style()
        self.title = QLabel()
        self.title.setObjectName("paneTitle")
        self.up_btn = QPushButton(st.standardIcon(QStyle.SP_ArrowUp), "")
        self.up_btn.setFixedWidth(34)
        self.up_btn.clicked.connect(self.go_up)
        self.refresh_btn = QPushButton(st.standardIcon(QStyle.SP_BrowserReload), "")
        self.refresh_btn.setFixedWidth(34)
        self.refresh_btn.clicked.connect(self.reload)
        self.path_edit = QLineEdit()
        self.path_edit.returnPressed.connect(lambda: self.go(self.path_edit.text().strip()))
        self.tree = FileTree(self)
        self.tree.itemDoubleClicked.connect(lambda it, _c: self.open_item(it))
        self.tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self.context_menu)
        self.tree.itemSelectionChanged.connect(self._sel_changed)
        self.tree.dropped.connect(lambda payload, sub: win.on_drop(self, payload, sub))
        self.tree.dropped_files.connect(lambda paths, sub: win.on_drop_files(self, paths, sub))
        self.tree.installEventFilter(self)
        top = QHBoxLayout()
        top.addWidget(self.up_btn)
        top.addWidget(self.refresh_btn)
        top.addWidget(self.path_edit, 1)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(self.title)
        lay.addLayout(top)
        lay.addWidget(self.tree, 1)
        self.apply_texts()

    def apply_texts(self):
        self.title.setText(tr("this_pc") if self.kind == "local" else tr("server"))
        self.tree.setHeaderLabels([tr("col_name"), tr("col_size"), tr("g_modified")])
        self.up_btn.setToolTip(tr("g_up_tip"))
        self.refresh_btn.setToolTip(tr("g_refresh"))

    def eventFilter(self, obj, ev):
        from PySide6.QtCore import QEvent

        if obj is self.tree and ev.type() == QEvent.FocusIn:
            self.focused.emit(self)
        if obj is self.tree and ev.type() == QEvent.KeyPress:
            if ev.key() in (Qt.Key_Return, Qt.Key_Enter) and self.tree.currentItem():
                self.open_item(self.tree.currentItem())
                return True
            if ev.key() == Qt.Key_Backspace:
                self.go_up()
                return True
        return super().eventFilter(obj, ev)

    def _sel_changed(self):
        self.win.update_selection_status()

    # ---- listado ----
    def parent_path(self):
        return core.parent_local(self.path) if self.kind == "local" else core.parent_remote(self.path)

    def go(self, path, select: str | None = None):
        self._seq += 1
        seq = self._seq
        conn = self.win.conn

        def work():
            p = path
            if self.kind == "remote":
                if conn is None:
                    raise RuntimeError(tr("g_not_connected"))
                if p is None:
                    p = conn.sftp.normalize(".")
                return p, core.list_remote(conn.sftp, p)
            return p, core.list_local(p)

        def done(res):
            if seq == self._seq:
                self.fill(res[0], res[1], select)

        run_bg(work, done, lambda e: self.win.report(f"{tr('could_not_open')}: {e}", "red"))

    def reload(self):
        cur = self.tree.currentItem()
        sel = cur.data(0, Qt.UserRole)["name"] if cur else None
        if self.path != "" or self.kind == "local":
            self.go(self.path, select=sel)

    def go_up(self):
        par = self.parent_path()
        if par is not None:
            name = os.path.basename(self.path.rstrip("\\/")) if self.kind == "local" else posixpath.basename(self.path.rstrip("/"))
            self.go(par, select=name)

    def fill(self, path, items, select=None):
        self.path, self.items = path, items
        self.entries = {it[0]: it[1] for it in items}
        self.path_edit.setText(path or tr("drives"))
        self.render(select)

    def render(self, select=None):
        st = self.style()
        dir_icon, file_icon = st.standardIcon(QStyle.SP_DirIcon), st.standardIcon(QStyle.SP_FileIcon)
        self.tree.clear()
        if self.parent_path() is not None:
            up = QTreeWidgetItem([".."])
            up.setIcon(0, dir_icon)
            up.setData(0, Qt.UserRole, {"name": "..", "is_dir": True})
            self.tree.addTopLevelItem(up)
        chosen = None
        for name, is_dir, size, hidden, mtime in self.items:
            if hidden and not self.win.show_hidden:
                continue
            it = QTreeWidgetItem([name, "" if is_dir else core.human(size), fmt_time(mtime)])
            it.setIcon(0, dir_icon if is_dir else file_icon)
            it.setData(0, Qt.UserRole, {"name": name, "is_dir": is_dir})
            it.setTextAlignment(1, Qt.AlignRight | Qt.AlignVCenter)
            self.tree.addTopLevelItem(it)
            if name == select:
                chosen = it
        if chosen is not None:
            self.tree.setCurrentItem(chosen)
        elif self.tree.topLevelItemCount():
            self.tree.setCurrentItem(self.tree.topLevelItem(0))

    def open_item(self, it):
        d = it.data(0, Qt.UserRole)
        if d["name"] == "..":
            self.go_up()
        elif d["is_dir"]:
            self.go(os.path.join(self.path, d["name"]) if self.kind == "local" else posixpath.join(self.path, d["name"]))

    def selected_names(self) -> list:
        return [i.data(0, Qt.UserRole)["name"] for i in self.tree.selectedItems() if i.data(0, Qt.UserRole)["name"] != ".."]

    def join(self, name: str) -> str:
        return os.path.join(self.path, name) if self.kind == "local" else posixpath.join(self.path, name)

    def context_menu(self, pos):
        self.focused.emit(self)
        names = self.selected_names()
        m = QMenu(self)
        it = self.tree.itemAt(pos)
        if it is not None and it.data(0, Qt.UserRole)["is_dir"]:
            m.addAction(tr("g_open"), lambda: self.open_item(it))
        if names:
            m.addAction(tr("g_upload") if self.kind == "local" else tr("g_download"), self.win.transfer_selected)
            m.addAction(tr("g_queue_add"), lambda: self.win.transfer_selected(run=False))
            m.addSeparator()
            m.addAction(tr("g_rename"), self.win.rename_selected)
            m.addAction(tr("g_delete"), self.win.delete_selected)
            m.addSeparator()
        m.addAction(tr("g_mkdir"), self.win.mkdir_here)
        m.addAction(tr("g_refresh"), self.reload)
        m.exec(self.tree.viewport().mapToGlobal(pos))


# ───────────────────────────── Ventana principal ──────────────────────────


class GuiHooks:
    """Lo que informa el motor de transferencias (hilo aparte) llega a la ventana por el puente."""

    def __init__(self, win):
        self.win = win

    def item_update(self, it, status):
        ui(lambda: self.win.on_item_update(it, status))

    def tick(self, it, label):
        ui(lambda: self.win.on_tick(it, label))

    def done(self, ok, err, msg):
        ui(lambda: self.win.on_queue_done(ok, err, msg))


class MainWindow(QMainWindow):
    def __init__(self, connect: str | None = None):
        super().__init__()
        self.conn = None
        self.srv: dict | None = None
        self.qkey = ""
        self.queue: list = []
        self.next_id = 1
        self.stop = threading.Event()
        self.busy = False
        self.cmd = None
        self.cmd_running = False
        self.show_hidden = False
        self.connecting = False
        self.pending_update = None
        self.active: FilePane | None = None
        self.bars: dict = {}
        self.setWindowIcon(make_app_icon())
        self.resize(1280, 800)
        self._build()
        self.apply_texts()
        self.reload_servers()
        # enlace con la terminal (sshmanager)
        self.link = core.LinkServer("gui", self._link_handler, __version__)
        self.link.start()
        self.poll_timer = QTimer(self)
        self.poll_timer.timeout.connect(self._poll_tui)
        self.poll_timer.start(3000)
        self._poll_tui()
        self.say(tr("log_started", v=__version__).replace("SSH Manager", "SSH Manager App"))
        if connect:
            QTimer.singleShot(300, lambda: self.open_server_by_name(connect))
        QTimer.singleShot(2500, lambda: self.check_updates(silent=True))

    # ---- construcción ----
    def _build(self):
        st = self.style()
        # barra lateral de servidores
        self.servers = QListWidget()
        self.servers.setObjectName("servers")
        self.servers.itemDoubleClicked.connect(lambda _i: self.connect_selected())
        self.servers.setContextMenuPolicy(Qt.CustomContextMenu)
        self.servers.customContextMenuRequested.connect(self._server_menu)
        self.servers_title = QLabel()
        self.servers_title.setObjectName("paneTitle")
        self.btn_new = QPushButton()
        self.btn_new.clicked.connect(self.new_server)
        self.btn_edit = QPushButton()
        self.btn_edit.clicked.connect(self.edit_server)
        self.btn_del = QPushButton()
        self.btn_del.clicked.connect(self.delete_server)
        self.btn_connect = QPushButton()
        self.btn_connect.setObjectName("primary")
        self.btn_connect.clicked.connect(self.connect_or_disconnect)
        side = QWidget()
        sl = QVBoxLayout(side)
        sl.setContentsMargins(8, 8, 4, 8)
        sl.addWidget(self.servers_title)
        sl.addWidget(self.servers, 1)
        row = QHBoxLayout()
        for b in (self.btn_new, self.btn_edit, self.btn_del):
            row.addWidget(b)
        sl.addLayout(row)
        sl.addWidget(self.btn_connect)
        side.setMinimumWidth(230)
        side.setMaximumWidth(340)

        # página de bienvenida
        self.welcome_title = QLabel()
        self.welcome_title.setObjectName("h1")
        self.welcome_text = QLabel()
        self.welcome_text.setObjectName("muted")
        self.welcome_text.setWordWrap(True)
        self.welcome_btn = QPushButton()
        self.welcome_btn.setObjectName("primary")
        self.welcome_btn.clicked.connect(self.new_server)
        logo = QLabel()
        logo.setPixmap(make_app_icon().pixmap(96, 96))
        wl = QVBoxLayout()
        wl.addStretch(1)
        for w in (logo, self.welcome_title, self.welcome_text, self.welcome_btn):
            wl.addWidget(w, 0, Qt.AlignHCenter)
        wl.addStretch(2)
        welcome = QWidget()
        welcome.setLayout(wl)

        # página del explorador
        self.local = FilePane(self, "local")
        self.remote = FilePane(self, "remote")
        self.local.focused.connect(self._set_active)
        self.remote.focused.connect(self._set_active)
        self.active = self.local
        panes = QSplitter(Qt.Horizontal)
        panes.addWidget(self.local)
        panes.addWidget(self.remote)
        panes.setChildrenCollapsible(False)
        self.toolbar = QToolBar()
        self.toolbar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.toolbar.setIconSize(QSize(18, 18))
        self.act = {}

        def add(key, icon, slot, shortcut=None, checkable=False):
            a = QAction(st.standardIcon(icon) if icon is not None else QIcon(), "", self)
            a.setCheckable(checkable)
            if shortcut:
                a.setShortcut(QKeySequence(shortcut))
            a.triggered.connect(slot)
            self.toolbar.addAction(a)
            self.act[key] = a
            return a

        add("upload", QStyle.SP_ArrowRight, lambda: self.transfer_from(self.local), "Ctrl+U")
        add("download", QStyle.SP_ArrowLeft, lambda: self.transfer_from(self.remote), "Ctrl+D")
        add("queue", QStyle.SP_FileDialogDetailedView, lambda: self.transfer_selected(run=False))
        self.toolbar.addSeparator()
        add("mkdir", QStyle.SP_FileDialogNewFolder, self.mkdir_here, "Ctrl+Shift+N")
        add("rename", QStyle.SP_FileDialogContentsView, self.rename_selected, "F2")
        add("delete", QStyle.SP_TrashIcon, self.delete_selected, "Del")
        add("refresh", QStyle.SP_BrowserReload, self.refresh_all, "F5")
        add("hidden", QStyle.SP_FileDialogInfoView, self.toggle_hidden, None, True)
        self.toolbar.addSeparator()
        add("terminal", QStyle.SP_ComputerIcon, self.open_terminal)

        # pestañas inferiores: transferencias y consola
        self.q_table = QTableWidget(0, 6)
        self.q_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.q_table.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.q_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.q_table.verticalHeader().setVisible(False)
        self.q_table.setAlternatingRowColors(True)
        self.q_table.horizontalHeader().setStretchLastSection(False)
        for c, mode in enumerate((QHeaderView.ResizeToContents, QHeaderView.ResizeToContents, QHeaderView.Stretch,
                                  QHeaderView.Stretch, QHeaderView.Stretch, QHeaderView.Fixed)):
            self.q_table.horizontalHeader().setSectionResizeMode(c, mode)
        self.q_table.setColumnWidth(5, 170)
        self.q_start = QPushButton()
        self.q_start.setObjectName("primary")
        self.q_start.clicked.connect(self.toggle_queue)
        self.q_retry = QPushButton()
        self.q_retry.clicked.connect(self.retry_failed)
        self.q_remove = QPushButton()
        self.q_remove.clicked.connect(self.remove_selected_queue)
        self.q_clear = QPushButton()
        self.q_clear.clicked.connect(self.clear_finished)
        self.q_summary = QLabel()
        self.q_summary.setObjectName("muted")
        qrow = QHBoxLayout()
        for b in (self.q_start, self.q_retry, self.q_remove, self.q_clear):
            qrow.addWidget(b)
        qrow.addStretch(1)
        qrow.addWidget(self.q_summary)
        qw = QWidget()
        ql = QVBoxLayout(qw)
        ql.setContentsMargins(0, 4, 0, 0)
        ql.addLayout(qrow)
        ql.addWidget(self.q_table, 1)

        self.console = QPlainTextEdit()
        self.console.setReadOnly(True)
        self.console.setMaximumBlockCount(3000)
        mono = QFont("monospace")
        mono.setStyleHint(QFont.Monospace)
        self.console.setFont(mono)
        self.cmd_edit = QLineEdit()
        self.cmd_edit.returnPressed.connect(self.run_command)
        self.cmd_cancel = QPushButton()
        self.cmd_cancel.clicked.connect(self.cancel_command)
        crow = QHBoxLayout()
        crow.addWidget(self.cmd_edit, 1)
        crow.addWidget(self.cmd_cancel)
        cw = QWidget()
        cl = QVBoxLayout(cw)
        cl.setContentsMargins(0, 4, 0, 0)
        cl.addWidget(self.console, 1)
        cl.addLayout(crow)
        self.tabs = QTabWidget()
        self.tabs.addTab(qw, "")
        self.tabs.addTab(cw, "")

        vs = QSplitter(Qt.Vertical)
        vs.addWidget(panes)
        vs.addWidget(self.tabs)
        vs.setStretchFactor(0, 3)
        vs.setStretchFactor(1, 2)
        vs.setChildrenCollapsible(False)
        browser = QWidget()
        bl = QVBoxLayout(browser)
        bl.setContentsMargins(0, 0, 8, 0)
        bl.addWidget(self.toolbar)
        bl.addWidget(vs, 1)

        self.stack = QStackedWidget()
        self.stack.addWidget(welcome)
        self.stack.addWidget(browser)
        split = QSplitter(Qt.Horizontal)
        split.addWidget(side)
        split.addWidget(self.stack)
        split.setStretchFactor(1, 1)
        split.setChildrenCollapsible(False)
        self.setCentralWidget(split)

        # barra de estado + menús
        self.status_msg = QLabel()
        self.link_label = QLabel()
        self.update_btn = QPushButton()
        self.update_btn.setFlat(True)
        self.update_btn.hide()
        self.update_btn.clicked.connect(self.install_pending_update)
        sb = self.statusBar()
        sb.addWidget(self.status_msg, 1)
        sb.addPermanentWidget(self.update_btn)
        sb.addPermanentWidget(self.link_label)
        self._build_menus()

    def _build_menus(self):
        bar = self.menuBar()
        self.m_file, self.m_view, self.m_tools, self.m_help = (bar.addMenu("") for _ in range(4))
        self.a_new = self.m_file.addAction("", self.new_server)
        self.a_disc = self.m_file.addAction("", self.disconnect_server)
        self.m_file.addSeparator()
        self.a_quit = self.m_file.addAction("", self.close)
        self.a_hidden = self.m_view.addAction("", self.toggle_hidden)
        self.a_hidden.setCheckable(True)
        self.m_lang = self.m_view.addMenu("")
        self.lang_actions = {}
        for code in core.LANGS:
            a = self.m_lang.addAction(core.LANG_NAMES[code], lambda c=code: self.set_language(c))
            a.setCheckable(True)
            self.lang_actions[code] = a
        self.m_theme = self.m_view.addMenu("")
        self.theme_actions = {}
        for mode in ("auto", "light", "dark"):
            a = self.m_theme.addAction("", lambda m=mode: self.set_theme(m))
            a.setCheckable(True)
            self.theme_actions[mode] = a
        self.a_terminal = self.m_tools.addAction("", self.open_terminal)
        self.a_doctor = self.m_tools.addAction("", self.show_doctor)
        self.a_upd_app = self.m_help.addAction("", lambda: self.check_updates(silent=False))
        self.a_upd_tui = self.m_help.addAction("", self.update_tui)
        self.m_help.addSeparator()
        self.a_about = self.m_help.addAction("", self.show_about)

    def apply_texts(self):
        self.setWindowTitle(self._title())
        self.servers_title.setText(tr("g_servers"))
        self.btn_new.setText(tr("g_new"))
        self.btn_edit.setText(tr("g_edit"))
        self.btn_del.setText(tr("g_delete"))
        self._update_connect_btn()
        self.welcome_title.setText(tr("g_welcome_title"))
        self.welcome_btn.setText(tr("g_add_server"))
        self.update_welcome()
        for key, text, tip in (
            ("upload", "g_upload", "g_upload_tip"), ("download", "g_download", "g_download_tip"),
            ("queue", "g_queue_add", "g_queue_add"), ("mkdir", "g_mkdir", "g_mkdir"), ("rename", "g_rename", "g_rename"),
            ("delete", "g_delete", "g_delete"), ("refresh", "g_refresh", "g_refresh"), ("hidden", "g_hidden", "g_hidden"),
            ("terminal", "g_terminal_short", "g_terminal"),
        ):
            self.act[key].setText(tr(text))
            self.act[key].setToolTip(tr(tip))
        for pane in (self.local, self.remote):
            pane.apply_texts()
        self.tabs.setTabText(0, tr("g_tab_transfers"))
        self.tabs.setTabText(1, tr("g_tab_console"))
        self.q_table.setHorizontalHeaderLabels([tr(c) for c in ("col_status", "col_type", "col_name", "col_from", "col_to", "col_progress")])
        self.q_start.setText(tr("g_q_stop") if self.busy else tr("g_q_start"))
        self.q_retry.setText(tr("g_q_retry"))
        self.q_remove.setText(tr("g_q_remove"))
        self.q_clear.setText(tr("g_q_clear"))
        self.cmd_edit.setPlaceholderText(tr("g_cmd_placeholder"))
        self.cmd_cancel.setText(tr("g_cmd_cancel"))
        self.m_file.setTitle(tr("g_menu_file"))
        self.m_view.setTitle(tr("g_menu_view"))
        self.m_tools.setTitle(tr("g_menu_tools"))
        self.m_help.setTitle(tr("g_menu_help"))
        self.a_new.setText(tr("g_add_server"))
        self.a_quit.setText(tr("g_quit"))
        self.a_disc.setText(tr("g_disconnect"))
        self.a_hidden.setText(tr("g_hidden"))
        self.m_lang.setTitle(tr("g_lang"))
        self.m_theme.setTitle(tr("g_theme"))
        for code, a in self.lang_actions.items():
            a.setChecked(code == core.LANG)
        cur_theme = core.load_settings().get("theme", "auto")
        for mode, a in self.theme_actions.items():
            a.setText(tr("g_theme_" + mode))
            a.setChecked(mode == cur_theme)
        self.a_terminal.setText(tr("g_terminal"))
        self.a_doctor.setText(tr("doctor_title", app="SSH Manager App"))
        self.a_upd_app.setText(tr("g_check_updates"))
        self.a_upd_tui.setText(tr("g_update_tui"))
        self.a_about.setText(tr("g_about"))
        self._refresh_queue_table()
        self._set_link_label(getattr(self, "tui_online", False))
        if self.pending_update:
            self.update_btn.setText(tr("g_update_available", v=self.pending_update[0]))
        self.update_selection_status()

    def _title(self) -> str:
        base = f"SSH Manager App v{__version__}"
        return f"{base}  -  {self.srv['name']}" if self.srv else base

    # ---- mensajes y consola ----
    def say(self, text: str, style: str = ""):
        color = LOG_COLORS.get(style)
        stamp = time.strftime("%H:%M:%S")
        line = html.escape(f"{stamp}  {text}")
        style_css = f"white-space:pre-wrap;{'color:' + color + ';' if color else ''}{'font-weight:bold;' if 'bold' in style else ''}"
        self.console.appendHtml(f'<span style="{style_css}">{line}</span>')

    def report(self, text: str, style: str = ""):
        self.say(text, style)
        self.statusBar().showMessage(text, 6000)

    def update_selection_status(self):
        if self.stack.currentIndex() != 1:
            return
        n = len(self.active.selected_names()) if self.active else 0
        self.status_msg.setText(tr("g_selected", n=n) if n else tr("g_drop_hint"))

    def _set_active(self, pane):
        self.active = pane
        self.update_selection_status()

    # ---- servidores ----
    def update_welcome(self):
        self.welcome_text.setText(tr("g_welcome_pick") if self.servers.count() else tr("g_welcome_empty"))

    def reload_servers(self, select: str | None = None):
        cur = select or (self.current_server()["name"] if self.current_server() else None)
        self.server_list = core.load_servers()
        self.servers.clear()
        for s in self.server_list:
            it = QListWidgetItem(f"{s['name']}\n{s['user']}@{s['host']}:{s.get('port', 22)}")
            it.setIcon(self.style().standardIcon(QStyle.SP_DriveNetIcon))
            self.servers.addItem(it)
            if s["name"] == cur:
                self.servers.setCurrentItem(it)
        if self.servers.currentRow() < 0 and self.servers.count():
            self.servers.setCurrentRow(0)
        self.update_welcome()

    def current_server(self):
        row = self.servers.currentRow()
        return self.server_list[row] if 0 <= row < len(getattr(self, "server_list", [])) else None

    def _save_servers(self):
        core.save_servers(self.server_list)
        core.link_notify("tui", {"cmd": "servers_changed"})

    def new_server(self):
        dlg = ServerDialog(self)
        if dlg.exec():
            self.server_list.append(dlg.data())
            self._save_servers()
            self.reload_servers(select=dlg.data()["name"])

    def edit_server(self):
        s = self.current_server()
        if not s:
            return
        dlg = ServerDialog(self, s)
        if dlg.exec():
            self.server_list[self.servers.currentRow()] = dlg.data()
            self._save_servers()
            self.reload_servers(select=dlg.data()["name"])

    def delete_server(self):
        s = self.current_server()
        if not s:
            return
        if QMessageBox.question(self, tr("g_servers"), tr("confirm_rm_server", name=s["name"])) == QMessageBox.Yes:
            del self.server_list[self.servers.currentRow()]
            self._save_servers()
            self.reload_servers()

    def _server_menu(self, pos):
        m = QMenu(self)
        m.addAction(tr("g_connect"), self.connect_selected)
        m.addAction(tr("g_edit"), self.edit_server)
        m.addAction(tr("g_delete"), self.delete_server)
        m.exec(self.servers.viewport().mapToGlobal(pos))

    def _update_connect_btn(self):
        self.btn_connect.setText(tr("g_disconnect") if self.conn is not None else tr("g_connect"))

    def connect_or_disconnect(self):
        self.disconnect_server() if self.conn is not None else self.connect_selected()

    def connect_selected(self):
        s = self.current_server()
        if s:
            self.connect_server(s)

    def open_server_by_name(self, name: str):
        self.reload_servers()
        srv = core.find_server(name)
        if not srv:
            self.report(tr("server_unknown", name=name), "red")
            return
        for i, s in enumerate(self.server_list):
            if s["name"] == srv["name"]:
                self.servers.setCurrentRow(i)
        self.bring_to_front()
        if self.conn is not None and self.srv and self.srv["name"] == srv["name"]:
            return  # ya está abierto: solo se trae la ventana al frente
        self.connect_server(srv)

    def bring_to_front(self):
        self.showNormal() if self.isMinimized() else None
        self.raise_()
        self.activateWindow()

    def connect_server(self, srv: dict, password: str | None = None):
        if self.connecting:
            return
        if self.conn is not None:
            self.disconnect_server()
            if self.conn is not None:  # sigue ocupada
                return
        self.connecting = True
        self.statusBar().showMessage(tr("connecting", name=srv["name"]))
        QApplication.setOverrideCursor(Qt.BusyCursor)

        def ok(conn):
            QApplication.restoreOverrideCursor()
            self.connecting = False
            self.on_connected(conn, srv)

        def err(e):
            QApplication.restoreOverrideCursor()
            self.connecting = False
            need_pw = isinstance(e, paramiko.AuthenticationException) or (
                isinstance(e, paramiko.SSHException) and "No authentication methods" in str(e)
            )
            if need_pw:
                pw, accepted = QInputDialog.getText(self, srv["name"], tr("ask_pass", user=srv["user"], host=srv["host"]), QLineEdit.Password)
                if accepted and pw:
                    self.connect_server(srv, pw)
                return
            msg = f"{srv['name']}: {e}"
            self.report(f"{tr('g_conn_error')}: {msg}", "red")
            QMessageBox.warning(self, tr("g_conn_error"), msg)

        run_bg(lambda: core.Connection(srv, password), ok, err)

    def on_connected(self, conn, srv):
        self.conn, self.srv = conn, srv
        self.qkey = core.server_key(srv)
        self.queue = core.load_queue(self.qkey)
        self.next_id = max((i["id"] for i in self.queue), default=0) + 1
        self.say(tr("log_connected", name=srv["name"], addr=self.qkey), "green")
        self.stack.setCurrentIndex(1)
        self.setWindowTitle(self._title())
        self._update_connect_btn()
        self.local.go(str(Path.home()))
        self.remote.go(None)
        self._refresh_queue_table()
        if self.queue:
            self.report(tr("queue_restored", n=len(self.queue)))
        else:
            self.statusBar().clearMessage()
        self.update_selection_status()

    def disconnect_server(self):
        if self.conn is None:
            return
        if self.busy:
            QMessageBox.information(self, tr("g_disconnect"), tr("busy_leave"))
            return
        pend = sum(1 for i in self.queue if i["status"] in ("pendiente", "error"))
        self.conn.close()
        self.conn = None
        self.say(tr("log_disconnected", name=self.srv["name"]))
        if pend:
            self.report(tr("queue_saved", n=pend))
        self.srv = None
        self.queue = []
        self.stack.setCurrentIndex(0)
        self.setWindowTitle(self._title())
        self._update_connect_btn()
        self.remote.fill("", [], None)

    # ---- acciones sobre archivos ----
    def other(self, pane: FilePane) -> FilePane:
        return self.remote if pane is self.local else self.local

    def refresh_all(self):
        self.local.reload()
        self.remote.reload()

    def toggle_hidden(self):
        self.show_hidden = not self.show_hidden
        self.act["hidden"].setChecked(self.show_hidden)
        self.a_hidden.setChecked(self.show_hidden)
        self.local.render()
        self.remote.render()

    def mkdir_here(self):
        pane = self.active
        if self.conn is None or pane.path == "":
            return
        name, ok = QInputDialog.getText(self, tr("g_mkdir"), tr("mkdir_prompt"))
        if not ok or not name.strip():
            return
        name = name.strip()

        def work():
            core.mkdir_checked(name)
            if pane.kind == "local":
                os.makedirs(os.path.join(pane.path, name), exist_ok=True)
            else:
                self.conn.sftp.mkdir(posixpath.join(pane.path, name))

        where = tr("pc") if pane.kind == "local" else tr("server")
        run_bg(work, lambda _r: (self.say(tr("log_mkdir", where=where, name=name)), pane.reload()),
               lambda e: self.report(f"{tr('error')}: {e}", "red"))

    def rename_selected(self):
        pane = self.active
        names = pane.selected_names()
        if self.conn is None or len(names) != 1:
            return
        old = names[0]
        new, ok = QInputDialog.getText(self, tr("g_rename"), tr("g_rename_prompt", name=old), text=old)
        if not ok or not new.strip() or new.strip() == old:
            return
        new = new.strip()

        def work():
            core.mkdir_checked(new)
            if pane.kind == "local":
                os.rename(os.path.join(pane.path, old), os.path.join(pane.path, new))
            else:
                self.conn.sftp.rename(posixpath.join(pane.path, old), posixpath.join(pane.path, new))

        run_bg(work, lambda _r: (self.say(f"{old} -> {new}"), pane.reload()), lambda e: self.report(f"{tr('error')}: {e}", "red"))

    def delete_selected(self):
        pane = self.active
        names = pane.selected_names()
        if self.conn is None or not names:
            return
        where = tr("where_local") if pane.kind == "local" else tr("where_remote")
        for n in names:
            extra = tr("extra_contents") if pane.entries.get(n) else ""
            if QMessageBox.question(self, tr("g_delete"), tr("confirm_delete", name=n, extra=extra, where=where)) != QMessageBox.Yes:
                return

        def work():
            for n in names:
                if pane.kind == "local":
                    core.delete_local(os.path.join(pane.path, n))
                else:
                    core.delete_remote(self.conn.sftp, posixpath.join(pane.path, n))

        label = tr("pc") if pane.kind == "local" else tr("server")
        run_bg(work, lambda _r: (self.say(tr("log_deleted", where=label, name=", ".join(names))), pane.reload()),
               lambda e: (self.report(f"{tr('error')}: {e}", "red"), pane.reload()))

    # ---- transferencias ----
    def transfer_from(self, src: FilePane):
        """Botones Subir / Bajar: la selección del panel indicado va al otro panel."""
        if not src.selected_names():
            self.statusBar().showMessage(tr("select_first"), 4000)
            return
        self.transfer(src, src.selected_names(), "", run=True)

    def transfer_selected(self, run: bool = True):
        pane = self.active
        if not pane.selected_names():
            self.statusBar().showMessage(tr("select_first"), 4000)
            return
        self.transfer(pane, pane.selected_names(), "", run=run)

    def on_drop(self, target: FilePane, payload: dict, sub: str):
        src = self.local if payload["kind"] == "local" else self.remote
        names = [n for n in payload["names"] if n in src.entries] or payload["names"]
        self.transfer(src, names, sub, run=True, src_dir=payload["dir"])

    def on_drop_files(self, target: FilePane, paths: list, sub: str):
        """Archivos soltados desde el explorador del sistema sobre el panel del servidor."""
        if self.conn is None or not paths:
            return
        dst_dir = self._dest_dir(self.remote, sub)
        items = []
        for p in paths:
            p = os.path.abspath(p)
            items.append(self._item(True, os.path.basename(p.rstrip("\\/")), os.path.isdir(p), os.path.dirname(p), dst_dir))
        self.enqueue(items, run=True)

    def _dest_dir(self, dst: FilePane, sub: str) -> str:
        return dst.join(sub) if sub else dst.path

    def _item(self, up, name, is_dir, src_dir, dst_dir) -> dict:
        return {"id": 0, "up": up, "name": name, "is_dir": bool(is_dir), "src": src_dir, "dst": dst_dir,
                "status": "pendiente", "error": "", "done": 0, "total": 0}

    def transfer(self, src: FilePane, names: list, sub: str, run: bool, src_dir: str | None = None):
        if self.conn is None:
            self.statusBar().showMessage(tr("g_not_connected"), 4000)
            return
        dst = self.other(src)
        src_dir = src_dir if src_dir is not None else src.path
        if src_dir == "" or dst.path == "":
            self.statusBar().showMessage(tr("open_folder"), 4000)
            return
        dst_dir = self._dest_dir(dst, sub)
        items = []
        for n in names:
            if not sub and n in dst.entries:
                if QMessageBox.question(self, tr("g_app"), tr("overwrite", name=n)) != QMessageBox.Yes:
                    continue
            items.append(self._item(src.kind == "local", n, src.entries.get(n, False), src_dir, dst_dir))
        self.enqueue(items, run)

    def describe(self, it: dict) -> str:
        up = it["up"]
        a, b = (tr("pc"), tr("server")) if up else (tr("server"), tr("pc"))
        return f'{core.gl("up") if up else core.gl("down")} {it["name"]}  ({a}: {it["src"]} {core.gl("arrow")} {b}: {it["dst"]})'

    def enqueue(self, items: list, run: bool):
        if not items:
            return
        ids = []
        for it in items:
            it["id"] = self.next_id
            ids.append(self.next_id)
            self.next_id += 1
            self.queue.append(it)
            self.say(tr("log_added", desc=self.describe(it)))
        self.queue_changed()
        if run:
            if self.busy:
                self.report(tr("queued_busy"), "yellow")
            else:
                self.run_ids(ids)
        self.tabs.setCurrentIndex(0)

    def queue_changed(self):
        core.save_queue(self.qkey, self.queue) if self.qkey else None
        if self.qkey:
            core.link_notify("tui", {"cmd": "queue_changed", "key": self.qkey})
        self._refresh_queue_table()

    def queue_reload(self, key):
        """La terminal cambió la fila de este servidor."""
        if self.busy or not self.qkey or key != self.qkey:
            return
        fresh = core.load_queue(self.qkey)
        keep = [i for i in self.queue if i["status"] == "listo"]
        used = {i["id"] for i in keep}
        nid = max(used, default=0) + 1
        for it in fresh:
            if it["id"] in used:
                it["id"], nid = nid, nid + 1
            used.add(it["id"])
        self.queue[:] = keep + fresh
        self.next_id = max(used, default=0) + 1
        self._refresh_queue_table()
        self.say(tr("link_queue"))

    def _refresh_queue_table(self):
        t = self.q_table
        t.setRowCount(len(self.queue))
        self.bars = {}
        counts = {"pendiente": 0, "en curso": 0, "listo": 0, "error": 0}
        for r, it in enumerate(self.queue):
            counts[it["status"]] += 1
            st = QTableWidgetItem(tr(STATUS_KEY[it["status"]]))
            st.setForeground(QColor(STATUS_COLOR[it["status"]]))
            up = it["up"]
            cells = [st, QTableWidgetItem((core.gl("up") + " " + tr("t_up")) if up else (core.gl("down") + " " + tr("t_down"))),
                     QTableWidgetItem(it["name"]),
                     QTableWidgetItem((tr("pc") if up else tr("server")) + ": " + it["src"]),
                     QTableWidgetItem((tr("server") if up else tr("pc")) + ": " + it["dst"])]
            for c, cell in enumerate(cells):
                cell.setData(Qt.UserRole, it["id"])
                t.setItem(r, c, cell)
            bar = QProgressBar()
            bar.setRange(0, 100)
            if it["status"] == "error":
                bar.setFormat(it["error"][:40])
                bar.setValue(0)
            else:
                bar.setValue(int(100 * it["done"] / it["total"]) if it["total"] else (100 if it["status"] == "listo" else 0))
            t.setCellWidget(r, 5, bar)
            self.bars[it["id"]] = bar
        self.q_summary.setText(tr("queue_summary", p=counts["pendiente"], r=counts["en curso"], d=counts["listo"], e=counts["error"])
                               if self.queue else tr("queue_empty").split(".")[0] + ".")
        self.q_start.setText(tr("g_q_stop") if self.busy else tr("g_q_start"))

    def toggle_queue(self):
        if self.busy:
            self.stop.set()
            self.report(tr("stopping"))
            return
        ids = [i["id"] for i in self.queue if i["status"] == "pendiente"]
        if not ids:
            self.statusBar().showMessage(tr("nothing_pending"), 4000)
            return
        self.run_ids(ids)

    def run_ids(self, ids: list):
        if self.busy or self.conn is None:
            return
        self.busy = True
        self.stop.clear()
        self.q_start.setText(tr("g_q_stop"))
        conn, queue = self.conn, self.queue
        threading.Thread(target=lambda: core.run_queue(conn, queue, ids, self.stop, GuiHooks(self)), daemon=True).start()

    def retry_failed(self):
        n = 0
        for it in self.queue:
            if it["status"] == "error":
                it["status"], it["error"] = "pendiente", ""
                n += 1
        self.queue_changed()
        self.statusBar().showMessage(tr("retry_n", n=n) if n else tr("retry_none"), 4000)

    def remove_selected_queue(self):
        ids = {self.q_table.item(r.row(), 0).data(Qt.UserRole) for r in self.q_table.selectionModel().selectedRows()}
        blocked = [i for i in self.queue if i["id"] in ids and i["status"] == "en curso"]
        if blocked:
            self.statusBar().showMessage(tr("rm_running"), 4000)
        self.queue[:] = [i for i in self.queue if i["id"] not in ids or i["status"] == "en curso"]
        self.queue_changed()

    def clear_finished(self):
        self.queue[:] = [i for i in self.queue if i["status"] != "listo"]
        self.queue_changed()

    # hooks del motor (hilo de la interfaz)
    def on_item_update(self, it, status):
        it["status"] = status
        d = self.describe(it)
        if status == "en curso":
            it["error"] = ""
            self.say(tr("log_item_start", d=d))
        elif status == "listo":
            self.say(tr("log_item_ok", d=d), "green")
        elif status == "error":
            self.say(tr("log_item_err", d=d, e=it["error"]), "red")
        elif status == "pendiente":
            self.say(tr("log_item_stop", d=d), "yellow")
        self.queue_changed()

    def on_tick(self, it, label):
        bar = self.bars.get(it["id"])
        frac = min(it["done"] / (it["total"] or 1), 1.0)
        if bar is not None:
            bar.setValue(int(frac * 100))
        arrow = core.gl("up") if it["up"] else core.gl("down")
        self.statusBar().showMessage(f"{arrow} {label}   {frac:.0%}   {core.human(it['done'])} / {core.human(it['total'])}")

    def on_queue_done(self, ok, err, msg):
        self.busy = False
        stopped = self.stop.is_set()
        if msg is None:
            msg = tr("queue_stopped" if stopped else "queue_finished", ok=ok, err=err)
        self.report(("ERROR  " if err or ok == err == 0 and msg else "OK  ") + msg, "red" if err else "green")
        self.refresh_all()
        self._refresh_queue_table()

    # ---- consola ----
    def run_command(self):
        text = self.cmd_edit.text().strip()
        if not text:
            return
        if self.conn is None:
            self.say(tr("g_not_connected"), "yellow")
            return
        if self.cmd_running:
            self.say(tr("cmd_running").replace("F4", tr("g_cmd_cancel")), "yellow")
            return
        self.cmd_edit.clear()
        self.cmd_running = True
        self.cmd = core.RemoteCommand(self.conn, text, self.remote.path)
        self.say(f"$ {text}", "bold green")
        cmd = self.cmd

        def work():
            def emit(lines, style):
                ui(lambda: [self.say(ln, style) for ln in lines])

            cmd.run(emit)
            ui(self._cmd_finished)

        threading.Thread(target=work, daemon=True).start()

    def _cmd_finished(self):
        self.cmd_running = False
        self.remote.reload()

    def cancel_command(self):
        if self.cmd_running and self.cmd is not None:
            self.cmd.cancel()

    # ---- enlace con la terminal ----
    def _link_handler(self, msg: dict):
        cmd = msg.get("cmd")
        if cmd == "info":
            return {"ok": True, "kind": "gui", "version": __version__, "server": self.srv["name"] if self.srv else None}
        if cmd == "show":
            ui(self.bring_to_front)
            return {"ok": True}
        if cmd == "open_server":
            name = str(msg.get("name", ""))
            if not core.find_server(name):
                return {"ok": False, "error": "unknown server"}
            ui(lambda: (self.say(tr("link_open", name=name)), self.open_server_by_name(name)))
            return {"ok": True}
        if cmd == "servers_changed":
            ui(lambda: (self.reload_servers(), self.say(tr("link_servers"))))
            return {"ok": True}
        if cmd == "queue_changed":
            key = msg.get("key")
            ui(lambda: self.queue_reload(key))
            return {"ok": True}
        return {"ok": False, "error": "unknown command"}

    def _poll_tui(self):
        run_bg(lambda: core.link_alive("tui"), self._set_link_label)

    def _set_link_label(self, online: bool):
        self.tui_online = online
        color = "#3fb950" if online else "#8b949e"
        self.link_label.setText(f'<span style="color:{color}">&#9679;</span> {tr("g_link_on") if online else tr("g_link_off")}')

    def open_terminal(self):
        name = self.srv["name"] if self.srv else None

        def done(res):
            ok, msg = res
            self.report(msg, "" if ok else "yellow")

        run_bg(lambda: core.launch_tui(name), done)

    # ---- actualizaciones ----
    def check_updates(self, silent: bool):
        if not silent:
            self.statusBar().showMessage(tr("g_checking"))

        def ok(res):
            remote, src = res
            if src is None:
                if not silent:
                    self.report(tr("g_up_to_date", v=__version__), "green")
                return
            self.pending_update = (remote, src)
            self.update_btn.setText(tr("g_update_available", v=remote))
            self.update_btn.show()
            if not silent:
                self.install_pending_update()

        def err(e):
            if not silent:
                self.report(tr("log_net", e=e), "red")

        run_bg(lambda: core.fetch_update(PROJECT, __version__), ok, err)

    def install_pending_update(self):
        if not self.pending_update:
            return
        remote, src = self.pending_update
        if QMessageBox.question(self, tr("g_app"), tr("confirm_update", v=remote, cur=__version__)) != QMessageBox.Yes:
            return
        try:
            core.apply_update(PROJECT, src)
        except Exception as e:  # noqa: BLE001
            self.report(tr("update_fail", e=e), "red")
            return
        self.pending_update = None
        self.update_btn.hide()
        QMessageBox.information(self, tr("g_app"), tr("g_update_done", v=remote))

    def update_tui(self):
        tui_dir = core.install_paths()[0]
        main = tui_dir / "ssh_manager.py"
        if not main.exists():
            self.report(tr("g_no_tui"), "yellow")
            return
        project = core.Project("sshmanager", "superc839e/sshmanager", ["ssh_manager.py", "sshmanager_core.py"], "ssh_manager.py", tui_dir)
        current = core.parse_version(main.read_text(encoding="utf-8")) or "0"
        self.statusBar().showMessage(tr("g_checking"))

        def ok(res):
            remote, src = res
            if src is None:
                self.report(tr("g_up_to_date", v=current), "green")
            elif QMessageBox.question(self, tr("g_app"), tr("confirm_update", v=remote, cur=current)) == QMessageBox.Yes:
                try:
                    core.apply_update(project, src)
                    self.report(f"OK  sshmanager v{remote}", "green")
                except Exception as e:  # noqa: BLE001
                    self.report(tr("update_fail", e=e), "red")

        run_bg(lambda: core.fetch_update(project, current), ok, lambda e: self.report(tr("log_net", e=e), "red"))

    def show_doctor(self):
        import contextlib
        import io

        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            core.doctor("SSH Manager App", REQS, "tui", say=lambda s: print(s))
        box = QMessageBox(self)
        box.setWindowTitle(tr("doctor_title", app="SSH Manager App"))
        box.setText(buf.getvalue())
        box.exec()

    def show_about(self):
        QMessageBox.about(self, tr("g_about"), tr("g_about_text", v=__version__, core=core.__version__, repo=REPO_URL).replace("\\n", "\n"))

    # ---- idioma y tema ----
    def set_language(self, code: str):
        core.apply_settings(code, core.CHARS)
        self.apply_texts()
        self.reload_servers()

    def set_theme(self, mode: str):
        data = core.load_settings()
        data["theme"] = mode
        core.save_settings(data)
        apply_theme(QApplication.instance(), mode)
        for m, a in self.theme_actions.items():
            a.setChecked(m == mode)

    def closeEvent(self, ev):
        if self.busy:
            self.stop.set()
        try:
            self.link.stop()
        except Exception:  # noqa: BLE001
            pass
        if self.conn is not None:
            self.conn.close()
        super().closeEvent(ev)


DEFAULT_PALETTE = None


def apply_theme(app: QApplication, mode: str) -> None:
    global DEFAULT_PALETTE
    if DEFAULT_PALETTE is None:
        DEFAULT_PALETTE = app.palette()
    app.setPalette(dark_palette() if mode == "dark" else light_palette() if mode == "light" else DEFAULT_PALETTE)
    app.setStyleSheet("")  # sin esto los widgets ya dibujados conservan los colores anteriores
    app.setStyleSheet(STYLE)


def main():
    global BRIDGE
    args = sys.argv[1:]
    connect = args[1] if len(args) > 1 and args[0] == "--connect" else None
    app = QApplication(sys.argv[:1])
    app.setApplicationName("SSH Manager App")
    app.setDesktopFileName("sshmanagerapp")
    app.setStyle("Fusion")
    app.setStyleSheet(STYLE)
    BRIDGE = Bridge()
    apply_theme(app, core.load_settings().get("theme", "auto"))
    win = MainWindow(connect=connect)
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
