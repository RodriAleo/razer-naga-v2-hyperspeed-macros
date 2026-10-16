#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Genera la guia visual de atajos (NagaV2_atajos.png).

La imagen se escribe en las carpetas de las implementaciones activas, porque
cada una la abre desde su propio directorio (Boton 5):

    windows/NagaV2_atajos.png
    linux/NagaV2_atajos.png

Al cambiar una macro: edita CELDAS y/o SECCIONES aqui abajo y re-ejecuta.
El numero de version se lee de CHANGELOG.md: re-ejecutar tambien al subirla.

    python generar_guia_atajos.py

Requiere Pillow:   pip install pillow
(Sustituye al antiguo generar_guia_atajos.ps1, que solo corria en Windows
 y dejaba la imagen en una sola carpeta.)
"""

import os
import re
import sys

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    sys.exit("Falta Pillow.  Instalalo con:  pip install pillow")

# ---------------- CONTENIDO (editar aqui) ----------------

# (numero, texto, tipo) -- tipo: 0=normal, 1=hypershift, 2=libre
CELDAS = [
    (1,  "Alt+Tab rapido",             0),
    (2,  "Alt+Tab: ventana anterior",  0),
    (3,  "Alt+Tab: ventana siguiente", 0),
    (4,  "Ctrl+Tab: pestaña siguiente", 0),
    (5,  "Abrir esta ayuda",           0),
    (6,  "(libre)",                    2),
    (7,  "Pantalla completa (F11)",    0),
    (8,  "(libre)",                    2),
    (9,  "(libre)",                    2),
    (10, "HYPERSHIFT 1  (ver abajo)",  1),
    (11, "HYPERSHIFT 2  (ver abajo)",  1),
    (12, "Win+Tab: vista de tareas",   0),
]

SECCIONES = [
    ("HYPERSHIFT 1  -  Boton 10  (manten pulsado)", [
        ("Rueda arriba / abajo",     "Subir / bajar volumen"),
        ("Clic de rueda",            "Play / Pausa multimedia"),
        ("Tilt derecha / izquierda", "Pista siguiente / anterior"),
    ]),
    ("HYPERSHIFT 2  -  Boton 11  (manten pulsado)", [
        ("Rueda arriba / abajo",     "Acercar / alejar zoom  (Ctrl + / -)"),
        ("Clic de rueda",            "Abrir software de capturas  (Ctrl+Q)"),
        ("Clic derecho",             "Portapapeles  (Win+V)"),
        ("Tilt izquierda / derecha", "Copiar / Pegar  (Ctrl+C / Ctrl+V)"),
    ]),
    ("TILT DE LA RUEDA  -  sin hypershift", [
        ("Tilt izquierda / derecha",
         "Desplazamiento lateral continuo (scroll horizontal)"),
    ]),
]

PIE = "Pulsa el Boton 5 para volver a abrir esta ayuda."


def _leer_version():
    """Primera entrada '## [X.Y.Z]' del CHANGELOG.md (fuente unica)."""
    ruta = os.path.join(os.path.dirname(os.path.abspath(__file__)), "CHANGELOG.md")
    with open(ruta, encoding="utf-8") as f:
        for linea in f:
            m = re.match(r"##\s*\[(\d+\.\d+\.\d+)\]", linea)
            if m:
                return m.group(1)
    sys.exit("CHANGELOG.md no tiene ninguna entrada '## [X.Y.Z]'.")
TITULO = "RAZER NAGA V2 HYPERSPEED  -  Atajos"

# Carpetas donde se deja la imagen (relativas a este archivo)
DESTINOS = ["windows", "linux"]
NOMBRE_IMAGEN = "NagaV2_atajos.png"

# ---------------- ESTILO ----------------
W, H = 920, 900
BG          = (28, 28, 30)
PANEL       = (44, 44, 48)
PANEL_VACIO = (34, 34, 37)
VERDE       = (68, 214, 44)
BLANCO      = (238, 238, 238)
GRIS        = (160, 160, 165)
APAGADO     = (95, 95, 100)
NEGRO       = (0, 0, 0)

M_IZQ, HUECO, TOP = 20, 16, 80
CELDA_W = (W - 2 * M_IZQ - 2 * HUECO) // 3
CELDA_H, V_HUECO = 92, 14


def _fuente(tam_pt, negrita=False):
    """Segoe UI si existe (Windows); si no, una sans-serif del sistema.
    Los tamanos vienen en puntos, como en el generador original: se pasan a
    pixeles a 96 ppp (1 pt = 4/3 px)."""
    px = int(round(tam_pt * 4 / 3))
    candidatas = (
        ["C:/Windows/Fonts/segoeuib.ttf", "C:/Windows/Fonts/arialbd.ttf",
         "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
         "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"]
        if negrita else
        ["C:/Windows/Fonts/segoeui.ttf", "C:/Windows/Fonts/arial.ttf",
         "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
         "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"]
    )
    for ruta in candidatas:
        if os.path.exists(ruta):
            return ImageFont.truetype(ruta, px)
    return ImageFont.load_default()


def _ancho(d, texto, fuente):
    return d.textbbox((0, 0), texto, font=fuente)[2]


def _partir(d, texto, fuente, ancho_max):
    """Parte el texto en lineas que quepan en ancho_max."""
    palabras, lineas, actual = texto.split(), [], ""
    for p in palabras:
        prueba = f"{actual} {p}".strip()
        if _ancho(d, prueba, fuente) <= ancho_max or not actual:
            actual = prueba
        else:
            lineas.append(actual)
            actual = p
    if actual:
        lineas.append(actual)
    return lineas


def generar():
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    f_titulo = _fuente(22, negrita=True)
    f_cabeza = _fuente(13, negrita=True)
    f_num    = _fuente(12, negrita=True)
    f_celda  = _fuente(12)
    f_fila   = _fuente(14)
    f_chica  = _fuente(11)

    # --- cabecera ---
    d.rectangle([0, 0, W, 62], fill=VERDE)
    d.text((24, 31), TITULO, font=f_titulo, fill=NEGRO, anchor="lm")

    # --- rejilla de 12 botones ---
    for i, (num, texto, tipo) in enumerate(CELDAS):
        col, fila = i % 3, i // 3
        cx = M_IZQ + col * (CELDA_W + HUECO)
        cy = TOP + fila * (CELDA_H + V_HUECO)

        fondo  = PANEL_VACIO if tipo == 2 else PANEL
        acento = APAGADO if tipo == 2 else VERDE
        d.rectangle([cx, cy, cx + CELDA_W, cy + CELDA_H], fill=fondo)
        d.rectangle([cx, cy, cx + 5, cy + CELDA_H], fill=acento)      # barra
        d.ellipse([cx + 16, cy + 12, cx + 46, cy + 42], fill=acento)  # circulo
        d.text((cx + 31, cy + 27), str(num), font=f_num,
               fill=BLANCO if tipo == 2 else NEGRO, anchor="mm")

        color = VERDE if tipo == 1 else (APAGADO if tipo == 2 else BLANCO)
        lineas = _partir(d, texto, f_celda, CELDA_W - 66)
        alto = len(lineas) * 20
        ty = cy + (CELDA_H - alto) // 2 + 10
        for ln in lineas:
            d.text((cx + 56, ty), ln, font=f_celda, fill=color, anchor="lm")
            ty += 20

    # --- secciones (hypershift y tilt) ---
    y = TOP + 4 * CELDA_H + 3 * V_HUECO + 22
    for titulo, pares in SECCIONES:
        d.text((24, y), titulo, font=f_cabeza, fill=VERDE, anchor="lt")
        y += 30
        for izq, der in pares:
            d.text((56, y), izq, font=f_fila, fill=GRIS, anchor="lt")
            d.text((360, y), der, font=f_fila, fill=BLANCO, anchor="lt")
            y += 28
        y += 8

    d.text((24, H - 30), PIE, font=f_chica, fill=GRIS, anchor="lt")
    # Version en la cabecera: si la guia esta desactualizada respecto a los
    # scripts (no se regenero al subir la version), se nota a simple vista.
    d.text((W - 24, 31), "v" + _leer_version(), font=f_cabeza, fill=NEGRO,
           anchor="rm")

    # --- guardar en las carpetas destino ---
    raiz = os.path.dirname(os.path.abspath(__file__))
    escritas = []
    for carpeta in DESTINOS:
        destino = os.path.join(raiz, carpeta)
        if not os.path.isdir(destino):
            print(f"Aviso: no existe la carpeta {carpeta}/ -- se omite")
            continue
        ruta = os.path.join(destino, NOMBRE_IMAGEN)
        img.save(ruta, "PNG")
        escritas.append(ruta)

    if not escritas:
        sys.exit("No se escribio ninguna imagen: faltan las carpetas destino.")
    print("Imagen generada en:")
    for r in escritas:
        print(f"  - {os.path.relpath(r, raiz)}")


if __name__ == "__main__":
    generar()
