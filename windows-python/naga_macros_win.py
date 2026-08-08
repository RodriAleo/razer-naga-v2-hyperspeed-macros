#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ============================================================
#  MACROS Razer Naga V2 Hyperspeed  -  version WINDOWS (Python)
#
#  Clon funcional de NagaV2_Macros.ahk, sin AutoHotkey. Existe
#  porque algunos anticheat de juegos exigen cerrar AHK para
#  arrancar; este demonio es un proceso Python normal.
#
#  Usa solo ctypes (API de Windows): NO requiere pip install.
#  Opcionalmente usa pystray+Pillow para el icono de bandeja.
#
#  Los 12 botones laterales mandan F13..F24 (guardado en la
#  memoria interna del raton via Synapse).
#
#  --- REQUISITOS ---
#    Python 3.8+ (nada mas para el nucleo)
#    Opcional (icono de bandeja):  pip install pystray pillow
#
#  --- EJECUTAR ---
#    pythonw naga_macros_win.py     (sin ventana de consola)
#    python  naga_macros_win.py     (con consola, para ver logs)
#
#  --- DISPOSICION (igual que la guia de atajos) ---
#    Boton 1  (F13) Alt+Tab rapido
#    Boton 2  (F14) Selector Alt+Tab  <- anterior
#    Boton 3  (F15) Selector Alt+Tab  -> siguiente
#    Boton 4  (F16) LIBRE
#    Boton 5  (F17) Abrir la guia de atajos
#    Boton 6  (F18) LIBRE
#    Boton 7  (F19) Pantalla completa (F11)
#    Boton 8  (F20) LIBRE
#    Boton 9  (F21) LIBRE
#    Boton 10 (F22) HYPERSHIFT 1 (manten pulsado)
#    Boton 11 (F23) HYPERSHIFT 2 (manten pulsado)
#    Boton 12 (F24) Vista de tareas (Win+Tab)
#
#    HYPERSHIFT 1 (Boton 10):
#      rueda arriba/abajo  -> subir/bajar volumen
#      clic de rueda       -> play/pausa
#      tilt der/izq        -> pista siguiente/anterior  (una vez)
#    HYPERSHIFT 2 (Boton 11):
#      rueda arriba/abajo  -> zoom Ctrl+ / Ctrl-
#      clic de rueda       -> Ctrl+Q (software de capturas)
#      clic derecho        -> portapapeles (Win+V)
#      tilt izq/der        -> copiar/pegar  (una vez)
#    TILT SIN HYPERSHIFT:
#      desplazamiento lateral continuo (scroll horizontal)
# ============================================================

import os
import sys
import ctypes
import threading
import subprocess
from ctypes import wintypes
from time import monotonic

try:
    import pystray
    from PIL import Image, ImageDraw
    _HAS_TRAY = True
except ImportError:
    _HAS_TRAY = False

# ---------------- CONFIGURACION ----------------

# Ruta de la imagen-guia de atajos (junto al script, igual que en AHK):
IMAGE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "NagaV2_atajos.png")

# Tiempo (segundos) que el selector Alt+Tab sigue abierto sin pulsar:
ALTTAB_TIMEOUT = 0.8

# Anti-repeticion del tilt (copiar/pegar/pista). Segundos:
TILT_DEBOUNCE = 0.40

# Cuanto sube/baja el volumen por cada paso de rueda:
WHEEL_STEPS = 2

# Cuanto aumenta/reduce el zoom por cada paso de rueda:
ZOOM_STEPS = 1

# Desplazamiento lateral continuo (tilt SIN hypershift). El tilt se reasigna en
# Synapse a Shift+F13 (derecha) / Shift+F14 (izquierda) y aqui se traduce a
# scroll horizontal repetido mientras se mantiene inclinado.
TILT_SCROLL_INTERVAL = 0.06   # segundos entre cada paso (mayor = mas lento)
TILT_SCROLL_STEPS = 1         # muescas por paso (mismo valor ambos lados)

# Watchdog del scroll lateral: si en este tiempo no llega ni el soltado ni una
# auto-repeticion de la F-key, se corta igual (evita un scroll trabado). Debe
# ser MAYOR que el retardo inicial de auto-repeticion de Windows (~0,5 s).
TILT_WATCHDOG = 0.9

# --- COMPORTAMIENTO POR APLICACION -------------------------------------
# El zoom (Hypershift 2 + rueda) se manda por defecto como Ctrl + numpad +/-,
# que es lo mas fiable en navegadores y editores. Pero algunas apps NO lo
# soportan y solo hacen zoom con Ctrl + rueda; se listan aqui por el nombre de
# su ejecutable (en minusculas).
#
# Para saber el nombre de una app: ponla en primer plano y ejecuta
#   python -c "import naga_macros_win as m, time; time.sleep(3); print(m.app_en_foco())"
# (tienes 3 segundos para hacer clic en su ventana).
ZOOM_CON_RUEDA = {
    "onenote.exe",        # OneNote de Office (escritorio)
    "onenoteim.exe",      # OneNote para Windows 10/11 (Store)
}

# Cuanto se cachea la app en primer plano (segundos). Ver app_en_foco().
APP_CACHE_TTL = 0.3

# Cuanto zoom por muesca en las apps de ZOOM_CON_RUEDA. Se manda como un unico
# evento de rueda con el delta completo. Subelo si quieres pasos mas grandes.
ZOOM_RUEDA_STEPS = 1

# Que teclas usa el zoom por teclado (todas las apps salvo ZOOM_CON_RUEDA).
#   False -> "+/-" de la FILA PRINCIPAL (VK_OEM_PLUS/MINUS). Es lo que hacia el
#            .ahk con Send("^-") y lo que esperan los navegadores; en Google Docs
#            dentro de Edge da el zoom del documento.
#   True  -> "+/-" del NUMPAD (VK_ADD/VK_SUBTRACT). Independiente del layout,
#            pero algunas apps web lo tratan distinto.
ZOOM_CON_NUMPAD = False
# -----------------------------------------------


# ============================================================
#  API de Windows (ctypes)
# ============================================================
user32 = ctypes.WinDLL("user32", use_last_error=True)
kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)

WH_KEYBOARD_LL = 13
WH_MOUSE_LL = 14
WM_KEYDOWN, WM_KEYUP = 0x0100, 0x0101
WM_SYSKEYDOWN, WM_SYSKEYUP = 0x0104, 0x0105
WM_MOUSEWHEEL, WM_MOUSEHWHEEL = 0x020A, 0x020E
WM_MBUTTONDOWN, WM_RBUTTONDOWN = 0x0207, 0x0204
WM_MBUTTONUP, WM_RBUTTONUP = 0x0208, 0x0205
# Al consumir un boton hay que suprimir TAMBIEN su evento de soltado: si el
# "up" se escapa, llega a la ventana que la macro acaba de abrir (p. ej. el
# panel del portapapeles) y la cierra por clic-fuera.
BOTON_UP = {WM_MBUTTONDOWN: WM_MBUTTONUP, WM_RBUTTONDOWN: WM_RBUTTONUP}

# Ruta rapida del hook de raton: el ratón emite WM_MOUSEMOVE a ~1000 Hz y el
# 99% de los eventos no nos interesan. Comprobar el mensaje ANTES de leer la
# estructura evita ese trabajo en cada movimiento.
MOUSE_INTERESANTES = frozenset((WM_MOUSEWHEEL, WM_MBUTTONDOWN, WM_RBUTTONDOWN,
                                WM_MBUTTONUP, WM_RBUTTONUP))
WM_QUIT = 0x0012
LLKHF_INJECTED = 0x00000010
LLMHF_INJECTED = 0x00000001

# Virtual-key codes
VK = {
    "F13": 0x7C, "F14": 0x7D, "F15": 0x7E, "F16": 0x7F, "F17": 0x80,
    "F18": 0x81, "F19": 0x82, "F20": 0x83, "F21": 0x84, "F22": 0x85,
    "F23": 0x86, "F24": 0x87,
    "F11": 0x7A, "TAB": 0x09, "SHIFT": 0x10, "CONTROL": 0x11, "MENU": 0x12,
    "LSHIFT": 0xA0, "RSHIFT": 0xA1,
    "OEM_PLUS": 0xBB, "OEM_MINUS": 0xBD,   # fila principal (= y -)
    "LWIN": 0x5B, "C": 0x43, "V": 0x56, "Q": 0x51,
    "VOLUME_UP": 0xAF, "VOLUME_DOWN": 0xAE,
    "MEDIA_PLAY_PAUSE": 0xB3, "MEDIA_NEXT": 0xB0, "MEDIA_PREV": 0xB1,
    "OEM_PLUS": 0xBB, "OEM_MINUS": 0xBD,
    "ADD": 0x6B, "SUBTRACT": 0x6D,   # numpad +/-: independientes del layout
}

# Boton lateral N -> VK de F(12+N)
FKEY_TO_BUTTON = {VK["F13"] + i: i + 1 for i in range(12)}

INPUT_MOUSE, INPUT_KEYBOARD = 0, 1
KEYEVENTF_KEYUP = 0x0002
KEYEVENTF_EXTENDEDKEY = 0x0001
MOUSEEVENTF_WHEEL = 0x0800
MOUSEEVENTF_HWHEEL = 0x01000
WHEEL_DELTA = 120

ULONG_PTR = ctypes.c_ulonglong if ctypes.sizeof(ctypes.c_void_p) == 8 else ctypes.c_ulong


class KBDLLHOOKSTRUCT(ctypes.Structure):
    _fields_ = [("vkCode", wintypes.DWORD), ("scanCode", wintypes.DWORD),
                ("flags", wintypes.DWORD), ("time", wintypes.DWORD),
                ("dwExtraInfo", ULONG_PTR)]


class MSLLHOOKSTRUCT(ctypes.Structure):
    _fields_ = [("pt", wintypes.POINT), ("mouseData", wintypes.DWORD),
                ("flags", wintypes.DWORD), ("time", wintypes.DWORD),
                ("dwExtraInfo", ULONG_PTR)]


class MOUSEINPUT(ctypes.Structure):
    _fields_ = [("dx", wintypes.LONG), ("dy", wintypes.LONG),
                ("mouseData", wintypes.DWORD), ("dwFlags", wintypes.DWORD),
                ("time", wintypes.DWORD), ("dwExtraInfo", ULONG_PTR)]


class KEYBDINPUT(ctypes.Structure):
    _fields_ = [("wVk", wintypes.WORD), ("wScan", wintypes.WORD),
                ("dwFlags", wintypes.DWORD), ("time", wintypes.DWORD),
                ("dwExtraInfo", ULONG_PTR)]


class _INPUTunion(ctypes.Union):
    _fields_ = [("mi", MOUSEINPUT), ("ki", KEYBDINPUT)]


class INPUT(ctypes.Structure):
    _fields_ = [("type", wintypes.DWORD), ("union", _INPUTunion)]


LRESULT = ctypes.c_ssize_t
HOOKPROC = ctypes.WINFUNCTYPE(LRESULT, ctypes.c_int, wintypes.WPARAM, wintypes.LPARAM)

user32.SetWindowsHookExW.restype = wintypes.HHOOK
user32.SetWindowsHookExW.argtypes = (ctypes.c_int, HOOKPROC, wintypes.HINSTANCE, wintypes.DWORD)
user32.CallNextHookEx.restype = LRESULT
user32.CallNextHookEx.argtypes = (wintypes.HHOOK, ctypes.c_int, wintypes.WPARAM, wintypes.LPARAM)
user32.SendInput.restype = wintypes.UINT
user32.SendInput.argtypes = (wintypes.UINT, ctypes.POINTER(INPUT), ctypes.c_int)
user32.GetAsyncKeyState.restype = ctypes.c_short
# Deteccion de la app en primer plano (comportamiento por aplicacion)
user32.GetForegroundWindow.restype = wintypes.HWND
user32.GetWindowThreadProcessId.restype = wintypes.DWORD
user32.GetWindowThreadProcessId.argtypes = (wintypes.HWND,
                                            ctypes.POINTER(wintypes.DWORD))
kernel32.OpenProcess.restype = wintypes.HANDLE
kernel32.OpenProcess.argtypes = (wintypes.DWORD, wintypes.BOOL, wintypes.DWORD)
kernel32.QueryFullProcessImageNameW.restype = wintypes.BOOL
kernel32.QueryFullProcessImageNameW.argtypes = (
    wintypes.HANDLE, wintypes.DWORD, wintypes.LPWSTR,
    ctypes.POINTER(wintypes.DWORD))
kernel32.CloseHandle.argtypes = (wintypes.HANDLE,)

# Marca propia: los eventos que inyectamos llevan esta firma en dwExtraInfo, para
# que nuestro propio hook los ignore y no se realimente (bucle infinito).
INJECTED_TAG = 0x4E414741   # "NAGA"


# ============================================================
#  Inyeccion de teclas y rueda
# ============================================================
def _send(*inputs):
    arr = (INPUT * len(inputs))(*inputs)
    user32.SendInput(len(inputs), arr, ctypes.sizeof(INPUT))


def _key_input(vk, up=False):
    flags = KEYEVENTF_KEYUP if up else 0
    if vk in (VK["LWIN"], VK["MEDIA_NEXT"], VK["MEDIA_PREV"],
              VK["MEDIA_PLAY_PAUSE"], VK["VOLUME_UP"], VK["VOLUME_DOWN"]):
        flags |= KEYEVENTF_EXTENDEDKEY
    # ⚠️ Rellenar wScan (no dejarlo en 0): las apps Chromium (Edge, Chrome,
    # Electron) derivan el "code" del evento DOM del SCAN CODE, no del virtual
    # key. Con wScan=0 pueden identificar mal la tecla; en Google Docs el zoom
    # con Ctrl +/- no se comportaba como el del teclado fisico.
    return INPUT(type=INPUT_KEYBOARD,
                 union=_INPUTunion(ki=KEYBDINPUT(wVk=vk,
                                                 wScan=user32.MapVirtualKeyW(vk, 0),
                                                 dwFlags=flags,
                                                 time=0, dwExtraInfo=INJECTED_TAG)))


def key_down(vk):
    _send(_key_input(vk, up=False))


def key_up(vk):
    _send(_key_input(vk, up=True))


def tap(*vks):
    """Pulsa y suelta: tap(CTRL, C) = Ctrl+C (suelta en orden inverso)."""
    seq = [_key_input(v) for v in vks]
    seq += [_key_input(v, up=True) for v in reversed(vks)]
    _send(*seq)


def tap_limpio(*vks):
    """Como tap(), pero soltando antes el Shift en el MISMO envio.

    Necesario para las acciones del tilt: Synapse mantiene el Shift del combo
    (Shift+F13/F14) pulsado, asi que un tap(CTRL, C) normal llegaria a la app
    como Ctrl+SHIFT+C -- que no es copiar (en navegadores abre el inspector).
    Con pegar el fallo se disimulaba: Ctrl+Shift+V es "pegar sin formato" y
    parecia funcionar. Todo va en una sola llamada a SendInput para que Synapse
    no alcance a re-afirmar el Shift en el medio.
    """
    seq = [_key_input(VK["LSHIFT"], up=True), _key_input(VK["RSHIFT"], up=True)]
    seq += [_key_input(v) for v in vks]
    seq += [_key_input(v, up=True) for v in reversed(vks)]
    _send(*seq)


def _wheel_input(horizontal, notches):
    flag = MOUSEEVENTF_HWHEEL if horizontal else MOUSEEVENTF_WHEEL
    data = ctypes.c_int32(notches * WHEEL_DELTA).value & 0xFFFFFFFF
    return INPUT(type=INPUT_MOUSE,
                 union=_INPUTunion(mi=MOUSEINPUT(dx=0, dy=0, mouseData=data,
                                                 dwFlags=flag, time=0,
                                                 dwExtraInfo=INJECTED_TAG)))


def wheel(horizontal, notches):
    """Rueda sintetica. horizontal=True -> scroll lateral (WM_MOUSEHWHEEL).
    En horizontal, positivo = derecha; en vertical, positivo = arriba."""
    _send(_wheel_input(horizontal, notches))


def wheel_ctrl(notches):
    """Ctrl + rueda vertical: el gesto de zoom que esperan algunas apps
    (OneNote, mapas, editores de imagen) y que NO responden a Ctrl+numpad+/-.

    ⚠️ Los tres eventos van en UN solo SendInput a proposito. El estado del
    teclado que ve la app esta sincronizado con el ORDEN de los mensajes, asi
    que al procesar la rueda vera el Ctrl pulsado aunque para entonces ya se
    haya soltado en tiempo real. Si el Ctrl↑ se manda por separado (p. ej. con
    un temporizador o al soltar el hypershift) puede llegar ANTES de que la app
    procese la rueda: entonces la lee sin Ctrl y en vez de zoom hace scroll.

    Se manda UN evento de rueda con el delta completo (notches * 120) en vez de
    varios de una muesca: menos mensajes que procesar = respuesta mas directa.
    """
    _send(_key_input(VK["CONTROL"]),
          _wheel_input(False, notches),
          _key_input(VK["CONTROL"], up=True))


def is_physically_down(vk):
    """Estado fisico de la tecla (bit alto de GetAsyncKeyState)."""
    return bool(user32.GetAsyncKeyState(vk) & 0x8000)


# ---------- aplicacion en primer plano ----------
PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
_app_cache = {"t": 0.0, "exe": ""}


def app_en_foco():
    """Nombre del ejecutable de la ventana activa, en minusculas
    (p. ej. "onenote.exe"). Cadena vacia si no se puede averiguar.

    El resultado se cachea unos milisegundos: al girar la rueda esto se
    consultaria decenas de veces por segundo y la app en foco no cambia
    mientras tanto."""
    ahora = monotonic()
    if ahora - _app_cache["t"] < APP_CACHE_TTL:
        return _app_cache["exe"]

    exe = ""
    try:
        hwnd = user32.GetForegroundWindow()
        if hwnd:
            pid = wintypes.DWORD()
            user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
            h = kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION,
                                     False, pid.value)
            if h:
                try:
                    buf = ctypes.create_unicode_buffer(512)
                    tam = wintypes.DWORD(len(buf))
                    if kernel32.QueryFullProcessImageNameW(h, 0, buf,
                                                           ctypes.byref(tam)):
                        exe = os.path.basename(buf.value).lower()
                finally:
                    kernel32.CloseHandle(h)
    except Exception:
        exe = ""

    _app_cache.update(t=ahora, exe=exe)
    return exe


# ============================================================
#  Overlay de la guia de atajos (Boton 5 mantenido)
# ============================================================
class GuiaOverlay:
    """Muestra NagaV2_atajos.png como ventana flotante mientras se mantiene el
    Boton 5, y la oculta al soltarlo.

    Tk NO es thread-safe y quiere su propio hilo con su mainloop, asi que vive
    en un hilo dedicado y el hook solo levanta/baja un Event; el hilo de Tk lo
    sondea. Nada de llamar a Tk desde el hook.

    ⚠️ La ventana se marca WS_EX_NOACTIVATE: si robara el foco, la app activa
    cambiaria a este proceso y (entre otras cosas) app_en_foco() devolveria
    python.exe, rompiendo el zoom por aplicacion.
    """

    def __init__(self, ruta):
        self.ruta = ruta
        self.error = None
        self._pedir = threading.Event()     # True = deberia estar visible
        self._listo = threading.Event()     # el hilo de Tk ya arranco
        self.visible = False                # estado real (lo fija el hilo Tk)
        self._t = threading.Thread(target=self._loop, daemon=True)
        self._t.start()
        self._listo.wait(timeout=5)

    # --- API para el hook (no toca Tk) ---
    def mostrar(self):
        self._pedir.set()

    def ocultar(self):
        self._pedir.clear()

    @property
    def disponible(self):
        return self.error is None

    # --- hilo propio de Tk ---
    def _loop(self):
        try:
            import tkinter as tk
        except ImportError:
            self.error = "tkinter no esta disponible"
            self._listo.set()
            return
        try:
            root = tk.Tk()
            root.withdraw()
            root.overrideredirect(True)         # sin barra de titulo
            root.attributes("-topmost", True)
            root.title("Naga V2 - Guia de atajos")
            root.configure(bg="black")

            img = self._cargar(tk, root)
            ancho, alto = img.width(), img.height()
            lbl = tk.Label(root, image=img, bd=0, highlightthickness=0, bg="black")
            lbl.image = img                     # referencia viva (si no, se borra)
            lbl.pack()

            x = (root.winfo_screenwidth() - ancho) // 2
            y = (root.winfo_screenheight() - alto) // 2
            root.geometry(f"{ancho}x{alto}+{x}+{y}")
            root.attributes("-alpha", 0.96)
            self._sin_foco(root)
        except Exception as ex:
            self.error = str(ex)
            self._listo.set()
            return

        self._listo.set()

        def tick():
            quiere = self._pedir.is_set()
            if quiere and not self.visible:
                root.deiconify()
                root.lift()
                root.attributes("-topmost", True)
                self.visible = True
            elif not quiere and self.visible:
                root.withdraw()
                self.visible = False
            root.after(30, tick)

        root.after(30, tick)
        root.mainloop()

    def _cargar(self, tk, root):
        """PhotoImage lee PNG en Tk 8.6+. Si la imagen no entra en la pantalla
        (o Tk no puede con el PNG) se recurre a Pillow para escalarla."""
        pantalla_h = root.winfo_screenheight()
        maximo = int(pantalla_h * 0.9)
        try:
            img = tk.PhotoImage(file=self.ruta)
            if img.height() <= maximo:
                return img
            factor = max(2, -(-img.height() // maximo))   # division hacia arriba
            return img.subsample(factor, factor)          # entero: sin Pillow
        except Exception:
            from PIL import Image as _Im, ImageTk
            im = _Im.open(self.ruta)
            if im.height > maximo:
                escala = maximo / im.height
                im = im.resize((int(im.width * escala), maximo), _Im.LANCZOS)
            return ImageTk.PhotoImage(im)

    @staticmethod
    def _sin_foco(root):
        """WS_EX_NOACTIVATE + TOOLWINDOW: la ventana no roba el foco ni sale en
        Alt+Tab (importante: el Boton 1 es justamente Alt+Tab)."""
        try:
            GWL_EXSTYLE = -20
            WS_EX_NOACTIVATE, WS_EX_TOOLWINDOW = 0x08000000, 0x00000080
            hwnd = int(root.winfo_id())
            get_ = getattr(user32, "GetWindowLongPtrW", user32.GetWindowLongW)
            set_ = getattr(user32, "SetWindowLongPtrW", user32.SetWindowLongW)
            set_(hwnd, GWL_EXSTYLE,
                 get_(hwnd, GWL_EXSTYLE) | WS_EX_NOACTIVATE | WS_EX_TOOLWINDOW)
        except Exception:
            pass


# ============================================================
#  Logica de macros (equivalente al .ahk)
# ============================================================
class NagaMacros:
    def __init__(self):
        self.hyper1 = False          # Boton 10 (F22) mantenido
        self.hyper2 = False          # Boton 11 (F23) mantenido
        self.shift_held = False      # Shift del combo de tilt
        self.last_tilt = {}          # nombre -> tiempo (anti-repeticion)

        self.alttab_open = False
        self.alttab_timer = None

        self.scroll_side = None      # None | "der" | "izq"
        self.scroll_stop_evt = None  # Event para frenar el hilo del scroll
        self.scroll_thread = None
        self.scroll_seen = 0.0       # ultima confirmacion de que el tilt sigue

        # Eventos de "boton soltado" pendientes de suprimir (ver BOTON_UP)
        self._botones_consumidos = set()

        # ¿La app en foco necesita Ctrl+rueda para el zoom? (ZOOM_CON_RUEDA)
        # Se resuelve al activar el Hypershift 2, no en cada muesca.
        self.zoom_con_rueda = False

        # Overlay de la guia de atajos (Boton 5). Se crea perezosamente en
        # main() para no pagar el arranque de Tk si no se usa.
        self.overlay = None

        self._lock = threading.RLock()

    # ---------- helpers ----------
    def once(self, name, func):
        """Ejecuta func solo la primera vez del tilt (anti-repeticion)."""
        now = monotonic()
        prev = self.last_tilt.get(name, 0.0)
        self.last_tilt[name] = now
        if now - prev < TILT_DEBOUNCE:
            return
        func()

    # ---------- Alt+Tab persistente (botones 2 y 3) ----------
    def alttab(self, forward):
        """El selector queda ABIERTO (Alt sostenido) y se cierra tras
        ALTTAB_TIMEOUT sin pulsar, confirmando la ventana elegida."""
        with self._lock:
            if not self.alttab_open:
                key_down(VK["MENU"])          # Alt abajo -> abre el selector
                self.alttab_open = True
            if forward:
                tap(VK["TAB"])
            else:
                tap(VK["SHIFT"], VK["TAB"])   # Alt+Shift+Tab -> retrocede
            if self.alttab_timer:
                self.alttab_timer.cancel()
            self.alttab_timer = threading.Timer(ALTTAB_TIMEOUT, self.alttab_close)
            self.alttab_timer.daemon = True
            self.alttab_timer.start()

    def alttab_close(self):
        with self._lock:
            if self.alttab_open:
                key_up(VK["MENU"])            # suelta Alt -> confirma
                self.alttab_open = False
            self.alttab_timer = None

    # ---------- botones simples ----------
    def boton_simple(self, n):
        if n == 1:                            # Alt+Tab rapido
            tap(VK["MENU"], VK["TAB"])
        elif n == 2:                          # selector <-
            self.alttab(forward=False)
        elif n == 3:                          # selector ->
            self.alttab(forward=True)
        elif n == 5:                          # guia de atajos (ver guia_*)
            self.guia_mostrar()
        elif n == 7:                          # pantalla completa
            tap(VK["F11"])
        elif n == 12:                         # vista de tareas (Win+Tab)
            tap(VK["LWIN"], VK["TAB"])
        # 4, 6, 8, 9 -> LIBRES (sin accion)

    # ---------- guia de atajos (Boton 5) ----------
    def guia_mostrar(self):
        """Overlay mientras se mantiene el boton. Si el overlay no esta
        disponible (sin tkinter), abre la imagen con el visor del sistema."""
        if self.overlay is not None and self.overlay.disponible:
            self.overlay.mostrar()
            return
        try:
            os.startfile(IMAGE_PATH)
        except OSError as ex:
            print(f"No pude abrir la guia: {ex}")

    def guia_ocultar(self):
        if self.overlay is not None:
            self.overlay.ocultar()

    # ---------- tilt (Shift+F13/F14) ----------
    def tilt(self, side):
        """Traduce el combo de tilt al gesto original segun el hypershift.
        El tilt se reasigna en Synapse porque el firmware lo reporta como
        rueda; ver README. El combo NO lleva Ctrl (haria zoom)."""
        # Estas acciones usan tap_limpio: el Shift del combo de tilt sigue
        # pulsado por Synapse y convertiria Ctrl+C en Ctrl+Shift+C (ver
        # tap_limpio). Las multimedia no lo necesitarian, pero se usa igual por
        # coherencia y por si alguna app mira los modificadores.
        right = (side == "der")
        if self.hyper1:                       # HS1 -> pista sig/ant (una vez)
            if right:
                self.once("next", lambda: tap_limpio(VK["MEDIA_NEXT"]))
            else:
                self.once("prev", lambda: tap_limpio(VK["MEDIA_PREV"]))
            return
        if self.hyper2:                       # HS2 -> pegar/copiar (una vez)
            if right:
                self.once("paste", lambda: tap_limpio(VK["CONTROL"], VK["V"]))
            else:
                self.once("copy", lambda: tap_limpio(VK["CONTROL"], VK["C"]))
            return
        self.scroll_start(side)               # sin HS -> scroll lateral continuo

    # ---------- scroll lateral continuo ----------
    #
    # Un HILO DEDICADO con un Event para frenar. Antes se reprogramaba un
    # threading.Timer por paso: creaba un hilo nuevo cada 60 ms (jitter) y, peor,
    # cada tick exigia is_physically_down() para continuar. Como
    # GetAsyncKeyState no es fiable con teclas que nosotros suprimimos, el bucle
    # moria tras el primer paso y solo revivia con la auto-repeticion de Windows
    # -> "se mueve un poco, frena, continua", con el retardo inicial del
    # typematic delay. Ahora el sondeo NO decide si continuar; solo el soltado.
    def scroll_start(self, side):
        with self._lock:
            if self.scroll_side is not None:  # ya hay uno en curso
                return
            self.scroll_side = side
            self.scroll_seen = monotonic()
            self.scroll_stop_evt = threading.Event()
            t = threading.Thread(target=self._scroll_loop,
                                 args=(side, self.scroll_stop_evt), daemon=True)
            self.scroll_thread = t
        t.start()

    def scroll_refresh(self):
        """Cada auto-repeticion de la F-key confirma que el tilt sigue puesto
        (alimenta el watchdog)."""
        self.scroll_seen = monotonic()

    def scroll_stop(self):
        with self._lock:
            self.scroll_side = None
            if self.scroll_stop_evt:
                self.scroll_stop_evt.set()
                self.scroll_stop_evt = None

    def _scroll_loop(self, side, stop_evt):
        """Emite rueda horizontal a ritmo constante hasta que se suelta el tilt.
        Stop primario: el keyup de la F-key (el hook SIEMPRE lo ve, aunque la
        tecla se suprima) -> stop_evt. Watchdog: si dejaran de llegar tanto el
        keyup como las auto-repeticiones, corta igual para no quedar trabado."""
        notches = TILT_SCROLL_STEPS if side == "der" else -TILT_SCROLL_STEPS
        vk = VK["F13"] if side == "der" else VK["F14"]
        while not stop_evt.is_set():
            wheel(horizontal=True, notches=notches)
            if stop_evt.wait(TILT_SCROLL_INTERVAL):
                break                         # soltado -> fin inmediato
            if (monotonic() - self.scroll_seen > TILT_WATCHDOG
                    and not is_physically_down(vk)):
                break                         # respaldo: nadie confirma el tilt
        with self._lock:
            if self.scroll_side == side:
                self.scroll_side = None
                self.scroll_stop_evt = None

    # ---------- hook de teclado ----------
    def on_key(self, vk, is_down):
        """Devuelve True para SUPRIMIR la tecla (no llega a las apps)."""
        # --- modificador del combo de tilt ---
        # OJO: el hook low-level reporta VK_LSHIFT/VK_RSHIFT (0xA0/0xA1), NUNCA
        # el generico VK_SHIFT (0x10). Comparar solo con el generico hacia que
        # el tilt no se detectara y cayera al manejo de boton normal.
        if vk in (VK["LSHIFT"], VK["RSHIFT"], VK["SHIFT"]):
            self.shift_held = is_down
            return False                      # el Shift real sigue siendo util

        if vk not in FKEY_TO_BUTTON:
            return False
        n = FKEY_TO_BUTTON[vk]

        # --- tilt: Shift+F13 (der) / Shift+F14 (izq) ---
        # Se acepta el estado rastreado O el fisico (por si Synapse manda la
        # F-key antes que el modificador). El "or scroll activo" garantiza ver
        # el soltado aunque el Shift se libere antes que la propia F-key.
        if vk in (VK["F13"], VK["F14"]):
            side = "der" if vk == VK["F13"] else "izq"
            if (self.shift_held or self.scroll_side == side
                    or is_physically_down(VK["SHIFT"])):
                if is_down:
                    if self.scroll_side == side:
                        self.scroll_refresh()  # auto-repeticion: alimenta el
                    else:                      # watchdog, no reinicia el scroll
                        self.tilt(side)
                else:
                    if self.scroll_side == side:
                        self.scroll_stop()
                return True                   # las F-keys nunca pasan

        # --- hypershift (botones 10 y 11): mantener ---
        if n == 10:
            self.hyper1 = is_down
            return True
        if n == 11:
            self.hyper2 = is_down
            if is_down:
                # Se resuelve AQUI, no en cada muesca de rueda: al pulsar el
                # hypershift hay tiempo de sobra, y el camino de la rueda queda
                # sin llamadas a la API (menos latencia). La app en foco no
                # cambia mientras se mantiene el hypershift.
                self.zoom_con_rueda = app_en_foco() in ZOOM_CON_RUEDA
            return True

        # --- boton 5: la guia se muestra MIENTRAS se mantiene ---
        if n == 5:
            if is_down:
                self.guia_mostrar()   # idempotente (aguanta auto-repeticiones)
            else:
                self.guia_ocultar()
            return True

        # --- botones simples ---
        if is_down:
            self.boton_simple(n)
        return True                           # las F-keys nunca pasan

    # ---------- hook de raton ----------
    def on_mouse(self, msg, mouse_data):
        """Devuelve True para SUPRIMIR el evento. Solo actua en hypershift."""
        # Soltado de un boton cuyo "pulsado" ya consumimos: suprimirlo tambien.
        # Se comprueba ANTES del chequeo de hypershift, por si se solto el
        # hypershift entre el down y el up (si no, el up se escaparia igual).
        if msg in self._botones_consumidos:
            self._botones_consumidos.discard(msg)
            return True

        if not (self.hyper1 or self.hyper2):
            return False                      # sin HS -> rueda/clics normales

        if msg == WM_MOUSEWHEEL:
            delta = ctypes.c_short(mouse_data >> 16).value
            up = delta > 0
            if self.hyper1:                   # HS1 -> volumen
                for _ in range(WHEEL_STEPS):
                    tap(VK["VOLUME_UP"] if up else VK["VOLUME_DOWN"])
            elif self.zoom_con_rueda:
                # HS2 en apps que solo hacen zoom con Ctrl+rueda (ej. OneNote).
                # UNA sola llamada con el delta completo: el Ctrl viaja en el
                # mismo lote que la rueda, asi soltar el hypershift despues no
                # puede convertir el zoom en scroll (ver wheel_ctrl).
                wheel_ctrl(ZOOM_RUEDA_STEPS if up else -ZOOM_RUEDA_STEPS)
            else:                             # HS2 -> zoom por teclado
                if ZOOM_CON_NUMPAD:
                    mas, menos = VK["ADD"], VK["SUBTRACT"]
                else:
                    mas, menos = VK["OEM_PLUS"], VK["OEM_MINUS"]
                for _ in range(ZOOM_STEPS):
                    tap(VK["CONTROL"], mas if up else menos)
            return True                       # suprime el scroll normal

        if msg == WM_MBUTTONDOWN:
            self._botones_consumidos.add(BOTON_UP[msg])
            if self.hyper1:
                tap(VK["MEDIA_PLAY_PAUSE"])
            else:
                tap(VK["CONTROL"], VK["Q"])   # HS2 -> software de capturas
            return True

        if msg == WM_RBUTTONDOWN and self.hyper2:
            self._botones_consumidos.add(BOTON_UP[msg])
            tap(VK["LWIN"], VK["V"])          # portapapeles
            return True

        return False


# ============================================================
#  Bucle de hooks (low-level, hilo con bomba de mensajes)
# ============================================================
class HookLoop:
    def __init__(self, macros):
        self.macros = macros
        self.thread_id = None
        self._kb_proc = HOOKPROC(self._kb_cb)     # referencias vivas: si el GC
        self._ms_proc = HOOKPROC(self._ms_cb)     # las libera, Windows crashea

    def _kb_cb(self, nCode, wParam, lParam):
        if nCode == 0:
            kb = ctypes.cast(lParam, ctypes.POINTER(KBDLLHOOKSTRUCT)).contents
            # ignora lo que inyectamos nosotros (evita realimentacion)
            if kb.dwExtraInfo != INJECTED_TAG:
                is_down = wParam in (WM_KEYDOWN, WM_SYSKEYDOWN)
                try:
                    if self.macros.on_key(kb.vkCode, is_down):
                        return 1              # suprime la tecla
                except Exception as ex:
                    print(f"Error en macro de teclado: {ex}")
        return user32.CallNextHookEx(None, nCode, wParam, lParam)

    def _ms_cb(self, nCode, wParam, lParam):
        # Ruta rapida: descarta WM_MOUSEMOVE (y demas) sin leer la estructura.
        # Este callback corre por CADA evento del raton (1000 Hz), asi que todo
        # lo que se haga aqui se paga en latencia de puntero.
        if nCode == 0 and wParam in MOUSE_INTERESANTES:
            ms = ctypes.cast(lParam, ctypes.POINTER(MSLLHOOKSTRUCT)).contents
            if ms.dwExtraInfo != INJECTED_TAG:
                try:
                    if self.macros.on_mouse(wParam, ms.mouseData):
                        return 1              # suprime el evento
                except Exception as ex:
                    print(f"Error en macro de raton: {ex}")
        return user32.CallNextHookEx(None, nCode, wParam, lParam)

    def run(self):
        """Instala los hooks y bombea mensajes. BLOQUEA el hilo llamante:
        los hooks low-level solo funcionan con un message loop vivo."""
        self.thread_id = kernel32.GetCurrentThreadId()
        # Prioridad alta para el hilo de los hooks: Windows da un plazo limitado
        # al callback (LowLevelHooksTimeout) y, si se agota, deja de llamarlo.
        try:
            THREAD_PRIORITY_HIGHEST = 2
            kernel32.SetThreadPriority(kernel32.GetCurrentThread(),
                                       THREAD_PRIORITY_HIGHEST)
        except Exception:
            pass
        kb = user32.SetWindowsHookExW(WH_KEYBOARD_LL, self._kb_proc, None, 0)
        ms = user32.SetWindowsHookExW(WH_MOUSE_LL, self._ms_proc, None, 0)
        if not kb or not ms:
            raise OSError(f"No pude instalar los hooks "
                          f"(error {ctypes.get_last_error()})")
        print("Macros activas. Ctrl+C o el menu de la bandeja para salir.")
        msg = wintypes.MSG()
        while user32.GetMessageW(ctypes.byref(msg), None, 0, 0) > 0:
            user32.TranslateMessage(ctypes.byref(msg))
            user32.DispatchMessageW(ctypes.byref(msg))
        user32.UnhookWindowsHookEx(kb)
        user32.UnhookWindowsHookEx(ms)

    def stop(self):
        if self.thread_id:
            user32.PostThreadMessageW(self.thread_id, WM_QUIT, 0, 0)


# ============================================================
#  Icono de bandeja (opcional: pystray + Pillow)
# ============================================================
def _tray_image(color):
    img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.ellipse((6, 6, 58, 58), fill=color)
    return img


def relanzar():
    """Arranca una instancia nueva del script y devuelve True si lo consiguio.

    ⚠️ Llamar SOLO despues de haber soltado los hooks: si las dos instancias
    coexisten, ambas los instalan y gana la que Windows tenga primero en la
    cadena (con la vieja ganando, los cambios recien hechos no se ven).
    Se usa pythonw.exe si existe, para que no aparezca una consola."""
    exe = sys.executable
    sin_consola = os.path.join(os.path.dirname(exe), "pythonw.exe")
    if os.path.exists(sin_consola):
        exe = sin_consola
    try:
        DETACHED_PROCESS = 0x00000008
        subprocess.Popen([exe, os.path.abspath(__file__)],
                         close_fds=True, creationflags=DETACHED_PROCESS)
        return True
    except Exception as ex:
        print(f"No pude relanzar el script: {ex}")
        return False


def run_tray(hooks, macros):
    """Icono verde en la bandeja con menu Reiniciar / Salir. Si pystray no esta
    instalado, el programa funciona igual pero sin icono."""
    def on_guia(_i=None, _it=None):
        # Desde el menu no hay tecla que mantener: se abre con el visor del
        # sistema, que se cierra normalmente.
        try:
            os.startfile(IMAGE_PATH)
        except OSError as ex:
            print(f"No pude abrir la guia: {ex}")

    def on_restart(icon, _it=None):
        # El orden importa: primero se cierra TODO (icono, hooks, modificadores
        # colgados) y solo despues se lanza la instancia nueva, para no tener
        # dos juegos de hooks compitiendo ni un Alt/Ctrl pulsado sin dueño.
        icon.stop()
        hooks.stop()
        macros.alttab_close()
        macros.scroll_stop()
        relanzar()
        os._exit(0)          # salida inmediata: el relevo ya esta en marcha

    def on_quit(icon, _it=None):
        icon.stop()
        hooks.stop()

    icon = pystray.Icon(
        "naga_macros", _tray_image((68, 214, 44, 255)), "Naga V2 — Macros",
        menu=pystray.Menu(
            pystray.MenuItem("Abrir guia de atajos", on_guia, default=True),
            pystray.MenuItem("Reiniciar", on_restart),
            pystray.MenuItem("Salir", on_quit),
        ))
    icon.run()


def main():
    if sys.platform != "win32":
        sys.exit("Este script es la version de Windows. En Linux usa naga_macros.py")

    # Prioridad alta: reduce la latencia de respuesta de las macros.
    try:
        kernel32.SetPriorityClass(kernel32.GetCurrentProcess(), 0x00000080)
    except Exception:
        pass

    # El intervalo de conmutacion del GIL es 5 ms por defecto: si otro hilo
    # (bandeja, scroll lateral) lo tiene tomado, el callback del hook puede
    # esperar hasta ese tiempo antes de ejecutarse. Bajarlo a 1 ms recorta esa
    # espera; el coste en CPU es despreciable para lo poco que hace el proceso.
    sys.setswitchinterval(0.001)

    macros = NagaMacros()

    # Overlay de la guia (Boton 5 mantenido). Si tkinter no esta o la imagen no
    # se puede cargar, se avisa y el Boton 5 cae al visor del sistema.
    if os.path.exists(IMAGE_PATH):
        macros.overlay = GuiaOverlay(IMAGE_PATH)
        if not macros.overlay.disponible:
            print(f"(sin overlay: {macros.overlay.error}; "
                  f"el Boton 5 abrira la imagen en el visor)")
    else:
        print(f"(no encuentro {IMAGE_PATH}; el Boton 5 no hara nada)")

    hooks = HookLoop(macros)

    if _HAS_TRAY:
        # Los hooks van en un hilo aparte; pystray necesita el hilo principal.
        t = threading.Thread(target=hooks.run, daemon=True)
        t.start()
        try:
            run_tray(hooks, macros)
        except KeyboardInterrupt:
            hooks.stop()
    else:
        print("(pystray/Pillow no instalados: sin icono de bandeja)")
        try:
            hooks.run()
        except KeyboardInterrupt:
            hooks.stop()

    # No dejar modificadores pulsados si se sale a mitad de un gesto
    macros.alttab_close()
    macros.scroll_stop()


if __name__ == "__main__":
    main()
