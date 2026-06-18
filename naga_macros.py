#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ============================================================
#  MACROS Razer Naga V2 Hyperspeed  -  version Linux (Wayland/X11)
#
#  Equivalente al script de AutoHotkey, pero para Linux.
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
#    Boton 4  (F16) LIBRE
#    Boton 5  (F17) Abrir la guia de atajos
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
import sys
import signal
import subprocess
from select import select
from time import monotonic

from evdev import InputDevice, UInput, ecodes as e, list_devices

# ---------------- CONFIGURACION ----------------

# Solo se "capturan" los dispositivos cuyo nombre contenga esto:
DEVICE_NAME_CONTAINS = "naga"

# Ruta de la imagen-guia de atajos (junto al script, igual que en AHK):
IMAGE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "NagaV2_atajos.png")

# Tiempo (segundos) que el selector Alt+Tab sigue abierto sin pulsar:
ALTTAB_TIMEOUT = 0.8

# Anti-repeticion del tilt (copiar/pegar/pista). Segundos:
TILT_DEBOUNCE = 0.40

# Cuanto sube/baja el volumen por cada paso de rueda:
WHEEL_STEPS = 2

# Cuanto aumenta/reduce el zoom por cada paso de rueda:
ZOOM_STEPS = 1

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


class NagaMacros:
    def __init__(self):
        self.hyper1 = False          # Boton 10 mantenido
        self.hyper2 = False          # Boton 11 mantenido
        self.alttab_open = False
        self.alttab_deadline = 0.0
        self.last_tilt = {}          # nombre -> tiempo, para el debounce

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

        # Si no encuentra por nombre, busca el dispositivo que emita F13
        if not named:
            for path in list_devices():
                try:
                    d = InputDevice(path)
                except Exception:
                    continue
                keys = d.capabilities().get(e.EV_KEY, [])
                if e.KEY_F13 in keys:
                    named.append(d)

        if not named:
            sys.exit("No encontre el raton Naga. Ajusta DEVICE_NAME_CONTAINS "
                     "o ejecuta con sudo.")

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

    def once(self, name, func):
        """Ejecuta func solo la primera vez del tilt (anti-repeticion)."""
        now = monotonic()
        prev = self.last_tilt.get(name, 0.0)
        self.last_tilt[name] = now
        if now - prev < TILT_DEBOUNCE:
            return
        func()

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
        elif n == 5:                     # abrir guia de atajos
            subprocess.Popen(["xdg-open", IMAGE_PATH],
                             close_fds=True, start_new_session=True)
        elif n == 7:                     # pantalla completa
            self.tap(e.KEY_F11)
        elif n == 12:                    # overview (tecla Super)
            self.tap(e.KEY_LEFTMETA)
        # 4, 6, 8, 9 -> LIBRES (sin accion)

    # ---------- bucle principal ----------
    def run(self):
        fds = {d.fd: d for d in self.read_devs}
        fd_list = list(fds)   # inmutable durante el bucle
        while True:
            timeout = None
            if self.alttab_open:
                timeout = max(0.0, self.alttab_deadline - monotonic())
            r, _, _ = select(fd_list, [], [], timeout)

            if self.alttab_open and monotonic() >= self.alttab_deadline:
                self.alttab_close()

            for fd in r:
                d = fds[fd]
                grabbed = d in self.grab_devs
                try:
                    for ev in d.read():
                        self.process(ev, grabbed)
                except BlockingIOError:
                    pass

    def process(self, ev, grabbed):
        # ---- teclas F13..F24 (botones laterales) ----
        if ev.type == e.EV_KEY and ev.code in FKEYS:
            n = FKEYS[ev.code]
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
        for d in self.grab_devs:
            try:
                d.ungrab()
            except Exception:
                pass
        try:
            self.ui.close()
        except Exception:
            pass


def main():
    # SCHED_FIFO prioridad 10: el kernel no interrumpe este proceso mientras
    # procesa eventos de entrada, reduciendo la latencia de respuesta.
    # Requiere root (o CAP_SYS_NICE), que ya se necesita para evdev/uinput.
    try:
        os.sched_setscheduler(0, os.SCHED_FIFO, os.sched_param(10))
        print("Scheduling: SCHED_FIFO prio=10")
    except Exception as ex:
        print(f"Aviso: no se pudo establecer prioridad en tiempo real: {ex}")

    app = NagaMacros()

    def stop(*_):
        app.cleanup()
        sys.exit(0)

    signal.signal(signal.SIGINT, stop)
    signal.signal(signal.SIGTERM, stop)
    try:
        app.run()
    finally:
        app.cleanup()


if __name__ == "__main__":
    main()
