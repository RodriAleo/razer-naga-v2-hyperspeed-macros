#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ============================================================
#  MACROS Razer Naga V2 Hyperspeed  -  version Linux (Wayland/X11)
#
#  Equivalente a la version de Windows (windows/naga_macros_win.py).
#  Lee los eventos del raton con evdev e inyecta las
#  combinaciones de teclas con uinput (a nivel de kernel,
#  por eso funciona igual en Wayland y en X11).
#
#  Los 12 botones laterales mandan F13..F24 (guardado en la
#  memoria interna del raton via Synapse).
#
#  --- REQUISITOS ---
#    sudo apt install python3-evdev      (o:  pip install evdev)
#
#  --- EJECUTAR ---
#    sudo python3 naga_macros.py
#  (mas abajo, en las NOTAS, como evitar el sudo y como
#   arrancarlo automaticamente al iniciar sesion)
#
#  --- DISPOSICION (igual que la guia de atajos) ---
#    Boton 1  (F13) Alt+Tab rapido
#    Boton 2  (F14) Selector Alt+Tab  <- anterior
#    Boton 3  (F15) Selector Alt+Tab  -> siguiente
#    Boton 4  (F16) Ctrl+Tab (siguiente pestaña)
#    Boton 5  (F17) Guia de atajos (visible mientras se mantiene)
#    Boton 6  (F18) LIBRE
#    Boton 7  (F19) Pantalla completa (F11)
#    Boton 8  (F20) LIBRE
#    Boton 9  (F21) LIBRE
#    Boton 10 (F22) HYPERSHIFT 1 (manten pulsado)
#    Boton 11 (F23) HYPERSHIFT 2 (manten pulsado)
#    Boton 12 (F24) Overview / vista de tareas (tecla Super)
#
#    HYPERSHIFT 1 (Boton 10):
#      rueda arriba/abajo  -> subir/bajar volumen
#      clic de rueda       -> play/pausa
#      tilt der/izq        -> pista siguiente/anterior  (una vez)
#    HYPERSHIFT 2 (Boton 11):
#      rueda arriba/abajo  -> zoom Ctrl+ / Ctrl-
#      clic de rueda       -> Ctrl+Q (software de capturas)
#      clic derecho        -> Super+V (portapapeles*)
#      tilt izq/der        -> copiar/pegar  (una vez)
# ============================================================

import os
import re
import sys
import signal
import subprocess
import threading
from select import select
from time import monotonic, sleep

try:
    import pystray
    from PIL import Image, ImageDraw
    _HAS_TRAY = True
except ImportError:
    _HAS_TRAY = False

from evdev import InputDevice, UInput, ecodes as e, list_devices

def _leer_version():
    """Version de las macros: primera entrada '## [X.Y.Z]' del CHANGELOG.md
    de la raiz del repo (fuente unica para los tres scripts y la guia).
    Si no se encuentra, devuelve '?' en vez de impedir el arranque."""
    ruta = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        os.pardir, "CHANGELOG.md")
    try:
        with open(ruta, encoding="utf-8") as f:
            for linea in f:
                m = re.match(r"##\s*\[(\d+\.\d+\.\d+)\]", linea)
                if m:
                    return m.group(1)
    except OSError:
        pass
    return "?"


# Se muestra en el icono de la bandeja. Se edita en CHANGELOG.md, no aqui.
VERSION = _leer_version()

# ---------------- CONFIGURACION ----------------

# Solo se "capturan" los dispositivos cuyo nombre contenga esto:
DEVICE_NAME_CONTAINS = "naga"

# Ruta de la imagen-guia de atajos (junto al script):
IMAGE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "NagaV2_atajos.png")

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
TILT_SCROLL_INTERVAL = 0.1    # segundos entre cada paso (mayor = mas lento)
TILT_SCROLL_STEPS = 1         # cuanto desplaza cada paso (mismo valor ambos lados)
HI_RES_PER_STEP = 120         # unidades hi-res por muesca (constante del kernel)

# Comando para abrir el historial del portapapeles (HS2 + clic derecho).
# Requiere un gestor instalado. Ejemplos:
#   ["copyq", "toggle"]
#   ["gpaste-client", "show-history"]
# Dejar vacío [] para deshabilitar (evita que Super+V abra el panel de GNOME):
PORTAPAPELES_CMD = []
# -----------------------------------------------


# Teclas F13..F24 -> numero de boton 1..12
FKEYS = {
    e.KEY_F13: 1, e.KEY_F14: 2, e.KEY_F15: 3, e.KEY_F16: 4,
    e.KEY_F17: 5, e.KEY_F18: 6, e.KEY_F19: 7, e.KEY_F20: 8,
    e.KEY_F21: 9, e.KEY_F22: 10, e.KEY_F23: 11, e.KEY_F24: 12,
}

# Codigos de rueda de alta resolucion (pueden no existir en kernels viejos)
REL_WHEEL_HI = getattr(e, "REL_WHEEL_HI_RES", None)
REL_HWHEEL_HI = getattr(e, "REL_HWHEEL_HI_RES", None)

if _HAS_TRAY:
    def _make_tray_icon(color):
        img = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
        ImageDraw.Draw(img).ellipse([4, 4, 60, 60], fill=color)
        return img

    _ICON_ACTIVE  = _make_tray_icon((50, 200, 50, 255))   # verde: activo
    _ICON_WAITING = _make_tray_icon((220, 130, 0, 255))   # naranja: esperando


# ============================================================
#  Overlay de la guia de atajos (Boton 5 mantenido)
# ============================================================
def _monitores():
    """Lista de (x, y, ancho, alto) de cada monitor segun `xrandr`. Vacia si
    no se puede averiguar (sin xrandr, Wayland puro...): entonces se usa la
    pantalla completa."""
    try:
        out = subprocess.run(["xrandr", "--listmonitors"], capture_output=True,
                             text=True, timeout=2).stdout
    except Exception:
        return []
    # " 0: +*HDMI-1 1920/528x1080/297+0+0  HDMI-1"
    return [tuple(int(v) for v in (m[2], m[3], m[0], m[1]))
            for m in re.findall(r"(\d+)/\d+x(\d+)/\d+\+(-?\d+)\+(-?\d+)", out)]


class GuiaOverlay:
    """Muestra NagaV2_atajos.png como ventana flotante mientras se mantiene el
    Boton 5 y la oculta al soltarlo (igual que en Windows).

    Tk NO es thread-safe y quiere su propio mainloop, asi que vive en un hilo
    dedicado; process() solo levanta/baja un Event y el hilo de Tk lo sondea.
    Nada de llamar a Tk desde el bucle de eventos.

    La ventana es override-redirect: el gestor de ventanas no la decora, no le
    da el foco y no sale en Alt+Tab (importa: el Boton 1 es Alt+Tab). Se centra
    en el monitor donde esta el puntero; con varios monitores, centrarla en
    "la pantalla" de Tk la dejaria partida entre dos.

    Es una sola instancia para todo el proceso (se crea en main()): las
    NagaMacros se recrean al reconectar el raton, el hilo de Tk no.
    """

    def __init__(self, ruta):
        self.ruta = ruta
        self.error = None
        self._pedir = threading.Event()     # True = deberia estar visible
        self._listo = threading.Event()     # el hilo de Tk ya arranco
        self.visible = False                # estado real (lo fija el hilo Tk)
        self._t = threading.Thread(target=self._loop, daemon=True,
                                   name="naga-guia")
        self._t.start()
        self._listo.wait(timeout=5)
        if not self._listo.is_set():
            self.error = "Tk no arranco a tiempo"

    # --- API para process() (no toca Tk) ---
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
            if not os.environ.get("DISPLAY"):
                raise RuntimeError("no hay DISPLAY (sesion grafica X11)")
            root = tk.Tk()
            root.withdraw()
            root.overrideredirect(True)          # sin decoracion ni foco
            root.attributes("-topmost", True)
            root.title("Naga V2 - Guia de atajos")
            root.configure(bg="black")
            lbl = tk.Label(root, bd=0, highlightthickness=0, bg="black")
            lbl.pack()
            try:
                root.attributes("-alpha", 0.96)  # requiere compositor
            except tk.TclError:
                pass
            original = self._abrir(tk)
        except Exception as ex:
            self.error = str(ex)
            self._listo.set()
            return

        cache = {}           # alto maximo -> PhotoImage (una por tamano de monitor)
        monitores = _monitores()
        # Precarga: escalar la imagen al primer uso costaba ~250 ms de retardo
        # al pulsar el Boton 5. Se prepara ya una por cada alto de monitor.
        try:
            for alto_mon in {m[3] for m in monitores}:
                cache.setdefault(int(alto_mon * 0.9),
                                 self._escalar(tk, original, int(alto_mon * 0.9)))
        except Exception:
            pass
        self._listo.set()

        def colocar():
            nonlocal monitores
            px, py = root.winfo_pointerxy()
            dentro = [m for m in monitores
                      if m[0] <= px < m[0] + m[2] and m[1] <= py < m[1] + m[3]]
            if not dentro:                       # cambio de monitores: releer
                monitores = _monitores()
                dentro = [m for m in monitores
                          if m[0] <= px < m[0] + m[2] and m[1] <= py < m[1] + m[3]]
            mx, my, mw, mh = dentro[0] if dentro else (
                0, 0, root.winfo_screenwidth(), root.winfo_screenheight())
            maximo = int(mh * 0.9)
            if maximo not in cache:
                cache[maximo] = self._escalar(tk, original, maximo)
            img = cache[maximo]
            lbl.configure(image=img)
            ancho, alto = img.width(), img.height()
            root.geometry(f"{ancho}x{alto}+{mx + (mw - ancho) // 2}"
                          f"+{my + (mh - alto) // 2}")

        def tick():
            quiere = self._pedir.is_set()
            if quiere and not self.visible:
                try:
                    colocar()
                except Exception as ex:
                    print(f"Guia: no pude colocar el overlay: {ex}")
                root.deiconify()
                root.lift()
                self.visible = True
            elif not quiere and self.visible:
                root.withdraw()
                self.visible = False
            root.after(30, tick)

        root.after(30, tick)
        root.mainloop()

    def _abrir(self, tk):
        """Imagen original: con Pillow si esta (escala con calidad); si no, el
        PhotoImage de Tk (lee PNG en Tk 8.6+)."""
        if _HAS_TRAY:                            # Pillow ya importado
            return Image.open(self.ruta).convert("RGB")
        return tk.PhotoImage(file=self.ruta)

    @staticmethod
    def _escalar(tk, original, maximo):
        if _HAS_TRAY:
            from PIL import ImageTk
            im = original
            if im.height > maximo:
                im = im.resize((int(im.width * maximo / im.height), maximo),
                               Image.LANCZOS)
            return ImageTk.PhotoImage(im)
        if original.height() <= maximo:
            return original
        factor = -(-original.height() // maximo)   # sin Pillow: solo enteros
        return original.subsample(factor, factor)


class NagaMacros:
    def __init__(self, stop_event=None, guia=None):
        self._stop = stop_event if stop_event is not None else threading.Event()
        self.guia = guia             # GuiaOverlay compartido (o None)
        self.hyper1 = False          # Boton 10 mantenido
        self.hyper2 = False          # Boton 11 mantenido
        self.alttab_open = False
        self.alttab_deadline = 0.0
        self.last_tilt = {}          # nombre -> tiempo, para el debounce

        # Combo de tilt (Shift+F13/F14) y scroll lateral continuo
        self.ctrl_held = False       # Ctrl (por si el binding aun lo incluye)
        self.shift_held = False      # Shift del combo de tilt
        self.scroll_dir = 0          # scroll lateral activo: +pasos der, -pasos izq
        self.scroll_key = None       # tecla (F13/F14) que mantiene el scroll
        self.next_scroll = 0.0       # proximo paso de scroll (monotonic)

        self.read_devs = []          # se leen (botones F13..F24)
        self.grab_devs = []          # se capturan (raton: rueda/tilt/clics)
        self._open_devices()

        # Dispositivo virtual por el que inyectamos todo
        macro_keys = [
            e.KEY_LEFTALT, e.KEY_LEFTCTRL, e.KEY_LEFTSHIFT, e.KEY_LEFTMETA,
            e.KEY_TAB, e.KEY_F11, e.KEY_Q, e.KEY_C, e.KEY_V,
            e.KEY_EQUAL, e.KEY_MINUS,
            e.KEY_KPPLUS, e.KEY_KPMINUS,
            e.KEY_VOLUMEUP, e.KEY_VOLUMEDOWN,
            e.KEY_PLAYPAUSE, e.KEY_NEXTSONG, e.KEY_PREVIOUSSONG,
            e.BTN_LEFT, e.BTN_RIGHT, e.BTN_MIDDLE,
        ]
        rels = [e.REL_X, e.REL_Y, e.REL_WHEEL, e.REL_HWHEEL]
        if REL_WHEEL_HI is not None:
            rels.append(REL_WHEEL_HI)
        if REL_HWHEEL_HI is not None:
            rels.append(REL_HWHEEL_HI)
        self.ui = UInput({e.EV_KEY: macro_keys, e.EV_REL: rels},
                         name="naga-macros-virtual")

    # ---------- deteccion de dispositivos ----------
    def _open_devices(self):
        flt = DEVICE_NAME_CONTAINS.lower()
        named = []
        for path in list_devices():
            try:
                d = InputDevice(path)
            except Exception:
                continue
            if flt in d.name.lower():
                named.append(d)

        # Fallback: busca dispositivo con F13 pero sin KEY_A (excluye teclados
        # reales como Logitech que también declaran KEY_F13)
        if not named:
            for path in list_devices():
                try:
                    d = InputDevice(path)
                except Exception:
                    continue
                keys = d.capabilities().get(e.EV_KEY, [])
                if e.KEY_F13 in keys and e.KEY_A not in keys:
                    named.append(d)

        if not named:
            raise OSError(19, "No encontre el raton Naga. Ajusta "
                          "DEVICE_NAME_CONTAINS o ejecuta con sudo.")

        for d in named:
            self.read_devs.append(d)
            caps = d.capabilities()
            rel  = caps.get(e.EV_REL, [])
            keys = caps.get(e.EV_KEY, [])
            # grabar tanto la interfaz de raton (REL_X) como la de teclado macro
            # (F13); sin grab las F-keys pasan al sistema y GNOME las interpreta
            if e.REL_X in rel or e.KEY_F13 in keys:
                self.grab_devs.append(d)

        for d in self.grab_devs:
            try:
                d.grab()
            except Exception as ex:
                print(f"Aviso: no pude capturar {d.name}: {ex}")

        print("Dispositivos en uso:")
        for d in self.read_devs:
            marca = " (capturado)" if d in self.grab_devs else ""
            print(f"  - {d.name}{marca}")

    # ---------- helpers de inyeccion ----------
    def tap(self, *codes):
        for c in codes:
            self.ui.write(e.EV_KEY, c, 1)
        self.ui.syn()
        for c in reversed(codes):
            self.ui.write(e.EV_KEY, c, 0)
        self.ui.syn()

    def key(self, code, value):
        self.ui.write(e.EV_KEY, code, value)
        self.ui.syn()

    def hscroll(self, steps):
        """Scroll horizontal de `steps` muescas.

        CRITICO: hay que emitir el evento de ALTA RESOLUCION ademas del legacy.
        Nuestro uinput declara REL_HWHEEL_HI_RES, y libinput, en cuanto un
        dispositivo anuncia hi-res, usa SOLO ese eje y DESCARTA los REL_HWHEEL
        legacy (los considera derivados). Mandando solo el legacy no se movia
        nada. Los mouses reales mandan los dos en el mismo frame, igual que aqui;
        no duplica el scroll porque libinput ignora el legacy si hay hi-res.
        """
        if REL_HWHEEL_HI is not None:
            self.ui.write(e.EV_REL, REL_HWHEEL_HI, steps * HI_RES_PER_STEP)
        self.ui.write(e.EV_REL, e.REL_HWHEEL, steps)
        self.ui.syn()

    def once(self, name, func):
        """Ejecuta func solo la primera vez del tilt (anti-repeticion)."""
        now = monotonic()
        prev = self.last_tilt.get(name, 0.0)
        self.last_tilt[name] = now
        if now - prev < TILT_DEBOUNCE:
            return
        func()

    # ---------- traduccion del tilt (Shift+F13/F14) ----------
    def tilt_combo(self, code, value):
        """En Linux el firmware no distingue el tilt del scroll, asi que el
        tilt se reasigna en Synapse a Shift+F13 (der) / Shift+F14 (izq) y aqui
        se reinterpreta como el gesto de tilt original."""
        right = (code == e.KEY_F13)
        if value == 1:                   # tilt inclinado
            if self.hyper1:              # HS1 -> pista sig/ant (una vez)
                if right:
                    self.once("next", lambda: self.tap(e.KEY_NEXTSONG))
                else:
                    self.once("prev", lambda: self.tap(e.KEY_PREVIOUSSONG))
            elif self.hyper2:            # HS2 -> pegar/copiar (una vez)
                if right:
                    self.once("paste", lambda: self.tap(e.KEY_LEFTCTRL, e.KEY_V))
                else:
                    self.once("copy", lambda: self.tap(e.KEY_LEFTCTRL, e.KEY_C))
            else:                        # sin HS -> scroll lateral continuo
                self.scroll_dir = TILT_SCROLL_STEPS if right else -TILT_SCROLL_STEPS
                self.scroll_key = code
                self.next_scroll = monotonic()   # primer paso ya mismo
        elif value == 0:                 # tilt soltado -> frena el scroll
            if self.scroll_key == code:
                self.scroll_dir = 0
                self.scroll_key = None
        # value == 2 (autorepeat del kernel) -> ignorar

    # ---------- Alt+Tab persistente ----------
    def alttab(self, forward):
        if not self.alttab_open:
            self.key(e.KEY_LEFTALT, 1)
            self.alttab_open = True
        if forward:
            self.tap(e.KEY_TAB)
        else:
            self.tap(e.KEY_LEFTSHIFT, e.KEY_TAB)
        self.alttab_deadline = monotonic() + ALTTAB_TIMEOUT

    def alttab_close(self):
        if self.alttab_open:
            self.key(e.KEY_LEFTALT, 0)
            self.alttab_open = False

    # ---------- macros de botones simples ----------
    def boton_simple(self, n):
        if n == 1:                       # Alt+Tab rapido
            self.tap(e.KEY_LEFTALT, e.KEY_TAB)
        elif n == 2:                     # selector <-
            self.alttab(forward=False)
        elif n == 3:                     # selector ->
            self.alttab(forward=True)
        elif n == 4:                     # siguiente pestaña
            self.tap(e.KEY_LEFTCTRL, e.KEY_TAB)
        elif n == 7:                     # pantalla completa
            self.tap(e.KEY_F11)
        elif n == 12:                    # overview (tecla Super)
            self.tap(e.KEY_LEFTMETA)
        # 6, 8, 9 -> LIBRES (sin accion). El 5 va aparte (guia_*): actua al
        # pulsar Y al soltar.

    # ---------- guia de atajos (Boton 5) ----------
    def guia_mostrar(self):
        """Overlay mientras se mantiene el boton. Si el overlay no esta
        disponible (sin tkinter/DISPLAY), abre la imagen con el visor."""
        if self.guia is not None and self.guia.disponible:
            self.guia.mostrar()
            return
        subprocess.Popen(["xdg-open", IMAGE_PATH],
                         close_fds=True, start_new_session=True)

    def guia_ocultar(self):
        if self.guia is not None:
            self.guia.ocultar()

    # ---------- bucle principal ----------
    def run(self):
        fds = {d.fd: d for d in self.read_devs}
        fd_list = list(fds)   # inmutable durante el bucle
        while not self._stop.is_set():
            deadlines = []
            if self.alttab_open:
                deadlines.append(self.alttab_deadline)
            if self.scroll_dir:
                deadlines.append(self.next_scroll)
            # cap 0.25 s para comprobar self._stop pronto (permite reiniciar)
            cap = 0.25
            timeout = min(cap, max(0.0, min(deadlines) - monotonic()) if deadlines else cap)
            r, _, _ = select(fd_list, [], [], timeout)
            now = monotonic()

            if self.alttab_open and now >= self.alttab_deadline:
                self.alttab_close()

            # scroll lateral continuo mientras se mantiene el tilt
            if self.scroll_dir and now >= self.next_scroll:
                self.hscroll(self.scroll_dir)
                self.next_scroll = now + TILT_SCROLL_INTERVAL

            for fd in r:
                d = fds[fd]
                grabbed = d in self.grab_devs
                try:
                    for ev in d.read():
                        self.process(ev, grabbed)
                except BlockingIOError:
                    pass

    def process(self, ev, grabbed):
        # ---- modificadores del combo de tilt (Shift+F13/F14) ----
        # La interfaz de teclado del Naga solo emite Shift (y Ctrl si el binding
        # aun lo trae) como parte de ese combo; basta registrar su estado y no
        # reenviarlos.
        if ev.type == e.EV_KEY and ev.code in (e.KEY_LEFTCTRL, e.KEY_RIGHTCTRL):
            self.ctrl_held = ev.value != 0
            return
        if ev.type == e.EV_KEY and ev.code in (e.KEY_LEFTSHIFT, e.KEY_RIGHTSHIFT):
            self.shift_held = ev.value != 0
            return

        # ---- teclas F13..F24 (botones laterales) ----
        if ev.type == e.EV_KEY and ev.code in FKEYS:
            n = FKEYS[ev.code]
            # F13/F14 con Shift = tilt der/izq (ver tilt_combo). El binding en
            # Synapse es Shift+F13/F14 (sin Ctrl: con Ctrl, en Windows la rueda
            # haria zoom). El "or scroll_key == code" garantiza recibir el
            # soltado aunque Synapse libere Shift antes que la propia F-key.
            if ev.code in (e.KEY_F13, e.KEY_F14) and \
               (self.shift_held or self.scroll_key == ev.code):
                self.tilt_combo(ev.code, ev.value)
                return
            if n == 5:                   # guia: visible MIENTRAS se mantiene
                if ev.value == 1:
                    self.guia_mostrar()
                elif ev.value == 0:
                    self.guia_ocultar()
                return                   # (value 2 = auto-repeticion: nada)
            if ev.value == 1:            # pulsado
                if n == 10:
                    self.hyper1 = True
                elif n == 11:
                    self.hyper2 = True
                else:
                    self.boton_simple(n)
            elif ev.value == 0:          # soltado
                if n == 10:
                    self.hyper1 = False
                elif n == 11:
                    self.hyper2 = False
            return                       # nunca se reenvian las F-keys

        # ---- clics fisicos (solo del raton capturado) ----
        if ev.type == e.EV_KEY and ev.code in (e.BTN_RIGHT, e.BTN_MIDDLE):
            if ev.value == 1:
                if ev.code == e.BTN_MIDDLE and self.hyper1:
                    self.tap(e.KEY_PLAYPAUSE); return
                if ev.code == e.BTN_MIDDLE and self.hyper2:
                    self.tap(e.KEY_LEFTCTRL, e.KEY_Q); return
                if ev.code == e.BTN_RIGHT and self.hyper2:
                    if PORTAPAPELES_CMD:
                        subprocess.Popen(PORTAPAPELES_CMD,
                                         close_fds=True, start_new_session=True)
                    return
            # sin hypershift: clic normal -> reenviar
            if grabbed:
                self.ui.write(ev.type, ev.code, ev.value)
            return

        # ---- rueda vertical ----
        if ev.type == e.EV_REL and ev.code in (e.REL_WHEEL, REL_WHEEL_HI):
            if self.hyper1 or self.hyper2:
                if ev.code == e.REL_WHEEL:   # solo el de baja-res dispara
                    up = ev.value > 0
                    if self.hyper1:
                        for _ in range(WHEEL_STEPS):
                            self.tap(e.KEY_VOLUMEUP if up else e.KEY_VOLUMEDOWN)
                    else:  # hyper2 -> zoom (KP+/KP- son layout-independientes)
                        key = e.KEY_KPPLUS if up else e.KEY_KPMINUS
                        for _ in range(ZOOM_STEPS):
                            self.tap(e.KEY_LEFTCTRL, key)
                return                        # suprime el scroll normal
            if grabbed:                       # scroll normal -> reenviar
                self.ui.write(ev.type, ev.code, ev.value)
            return

        # ---- tilt / rueda horizontal ----
        if ev.type == e.EV_REL and ev.code in (e.REL_HWHEEL, REL_HWHEEL_HI):
            if self.hyper1 or self.hyper2:
                if ev.code == e.REL_HWHEEL:
                    right = ev.value > 0
                    if self.hyper1:
                        if right:
                            self.once("next", lambda: self.tap(e.KEY_NEXTSONG))
                        else:
                            self.once("prev", lambda: self.tap(e.KEY_PREVIOUSSONG))
                    else:  # hyper2 -> copiar/pegar
                        if right:
                            self.once("paste", lambda: self.tap(e.KEY_LEFTCTRL, e.KEY_V))
                        else:
                            self.once("copy", lambda: self.tap(e.KEY_LEFTCTRL, e.KEY_C))
                return
            if grabbed:
                self.ui.write(ev.type, ev.code, ev.value)
            return

        # ---- todo lo demas (movimiento, clic izq, SYN...) ----
        if grabbed:
            if ev.type == e.EV_SYN:
                self.ui.syn()
            elif ev.type == e.EV_REL or (ev.type == e.EV_KEY and ev.code == e.BTN_LEFT):
                self.ui.write(ev.type, ev.code, ev.value)

    def cleanup(self):
        self.alttab_close()
        self.guia_ocultar()          # por si se desconecta con el Boton 5 pulsado
        for d in self.grab_devs:
            try:
                d.ungrab()
            except Exception:
                pass
        try:
            self.ui.close()
        except Exception:
            pass


def _wait_for_naga(poll=2.0, settle=3.0):
    """Bloquea hasta que el Naga aparezca y esté estable en /dev/input/.
    Tras detectarlo espera `settle` segundos y confirma que sigue presente,
    para asegurarse de que el kernel registró todas las interfaces.
    """
    flt = DEVICE_NAME_CONTAINS.lower()

    def present():
        for path in list_devices():
            try:
                if flt in InputDevice(path).name.lower():
                    return True
            except Exception:
                pass
        return False

    while True:
        if present():
            sleep(settle)
            if present():   # confirmar estabilidad tras el asentamiento
                return
        sleep(poll)


def main():
    # SCHED_FIFO prioridad 10: el kernel no interrumpe este proceso mientras
    # procesa eventos de entrada, reduciendo la latencia de respuesta.
    # Requiere root (o CAP_SYS_NICE), que ya se necesita para evdev/uinput.
    try:
        os.sched_setscheduler(0, os.SCHED_FIFO, os.sched_param(10))
        print("Scheduling: SCHED_FIFO prio=10")
    except Exception as ex:
        print(f"Aviso: no se pudo establecer prioridad en tiempo real: {ex}")

    # Overlay de la guia (Boton 5 mantenido): uno para todo el proceso. Si Tk
    # o la imagen fallan, se avisa y el Boton 5 cae al visor de imagenes.
    guia = None
    if os.path.exists(IMAGE_PATH):
        guia = GuiaOverlay(IMAGE_PATH)
        if not guia.disponible:
            print(f"(sin overlay: {guia.error}; el Boton 5 abrira la imagen "
                  f"en el visor)")
    else:
        print(f"(no encuentro {IMAGE_PATH}; el Boton 5 no hara nada)")

    # Estado compartido entre el hilo worker y el hilo del tray
    _app   = [None]               # instancia NagaMacros actual
    _stop  = [threading.Event()]  # evento de parada; se limpia en cada iteracion
    _alive = [True]               # False cuando el usuario elige Salir
    _icon  = [None]               # icono de bandeja (solo si _HAS_TRAY)

    def _set_active(active):
        if _HAS_TRAY and _icon[0] is not None:
            _icon[0].icon  = _ICON_ACTIVE if active else _ICON_WAITING
            _icon[0].title = (f"Naga Macros v{VERSION} - activo"
                              if active else
                              f"Naga Macros v{VERSION} - esperando raton")

    def _worker():
        while _alive[0]:
            _stop[0].clear()
            _set_active(False)
            try:
                _app[0] = NagaMacros(stop_event=_stop[0], guia=guia)
            except OSError as ex:
                _app[0] = None
                if ex.errno == 19:
                    print("Dispositivo no encontrado. Esperando...")
                    _wait_for_naga()
                    print("Dispositivo encontrado, iniciando...")
                    continue
                raise
            _set_active(True)
            _disconnect = False
            try:
                _app[0].run()
            except OSError as ex:
                if ex.errno != 19:
                    raise
                _disconnect = True
            finally:
                if _app[0] is not None:
                    try:
                        _app[0].cleanup()
                    except Exception:
                        pass
                    _app[0] = None
            if _disconnect:
                _set_active(False)
                print("\nDispositivo desconectado. Esperando reconexion...")
                _wait_for_naga()
                print("Dispositivo encontrado, reiniciando...")

    def _on_restart(icon, item):
        """Reinicia el script sin salir: detiene run() y el worker crea una nueva instancia."""
        _stop[0].set()

    def _on_quit(icon, item):
        _alive[0] = False
        _stop[0].set()
        icon.stop()

    def _stop_signal(*_):
        _alive[0] = False
        _stop[0].set()
        if _HAS_TRAY and _icon[0]:
            _icon[0].stop()
        sys.exit(0)

    signal.signal(signal.SIGINT,  _stop_signal)
    signal.signal(signal.SIGTERM, _stop_signal)

    if _HAS_TRAY:
        t = threading.Thread(target=_worker, daemon=True, name="naga-worker")
        t.start()
        icon = pystray.Icon(
            "naga-macros",
            _ICON_WAITING,
            f"Naga Macros v{VERSION} - esperando raton",
            menu=pystray.Menu(
                # Solo informativo (deshabilitado): la version a la vista al
                # hacer clic en el icono.
                pystray.MenuItem(f"Naga V2 Macros v{VERSION}",
                                 lambda *_: None, enabled=False),
                pystray.Menu.SEPARATOR,
                pystray.MenuItem("Reiniciar", _on_restart),
                pystray.MenuItem("Salir",     _on_quit),
            ),
        )
        _icon[0] = icon
        icon.run()        # bloquea el hilo principal (requerido por pystray)
        t.join(timeout=2.0)
    else:
        _worker()


if __name__ == "__main__":
    main()
