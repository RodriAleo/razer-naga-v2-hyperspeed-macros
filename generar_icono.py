#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Genera el icono de la aplicacion (circulo verde con una "N" y tres puntos).

Escribe:

    windows/NagaV2_Macros.ico          ejecutable y accesos directos (16-256 px)
    windows/NagaV2_Macros.png          icono de la bandeja
    linux/NagaV2_Macros.png            lanzador del menu de aplicaciones y bandeja (activo)
    linux/NagaV2_Macros_espera.png     bandeja mientras se espera al raton (naranja)

    python generar_icono.py

La "N" se dibuja como poligono, no con una fuente: asi el icono sale identico
en Windows y en Linux sin depender de las fuentes instaladas.

Requiere Pillow:   pip install pillow
"""

import os
import sys

try:
    from PIL import Image, ImageDraw
except ImportError:
    sys.exit("Falta Pillow.  Instalalo con:  pip install pillow")

VERDE   = (68, 214, 44, 255)     # el mismo verde que la guia de atajos
NARANJA = (230, 140, 0, 255)     # estado "esperando raton" (Linux)
NEGRO   = (10, 10, 12, 255)

S = 1024                         # se dibuja grande y se reduce (antialias)
NOMBRE = "NagaV2_Macros"
TAMANOS_ICO = [16, 20, 24, 32, 40, 48, 64, 128, 256]


def dibujar(fondo):
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse([40, 40, S - 40, S - 40], fill=fondo)

    # "N" negrita: dos astas + diagonal (la union de los tres poligonos)
    arriba, abajo = 230, 720
    izq, der, grosor = 318, 706, 118
    d.rectangle([izq, arriba, izq + grosor, abajo], fill=NEGRO)
    d.rectangle([der - grosor, arriba, der, abajo], fill=NEGRO)
    d.polygon([(izq, arriba), (izq + grosor + 18, arriba),
               (der, abajo), (der - grosor - 18, abajo)], fill=NEGRO)

    # tres puntos: los botones laterales
    r, y = 34, 812
    for cx in (412, 512, 612):
        d.ellipse([cx - r, y - r, cx + r, y + r], fill=NEGRO)
    return im


def main():
    raiz = os.path.dirname(os.path.abspath(__file__))
    activo = dibujar(VERDE)
    espera = dibujar(NARANJA)
    png = activo.resize((256, 256), Image.LANCZOS)

    salidas = []
    win = os.path.join(raiz, "windows")
    if os.path.isdir(win):
        ico = os.path.join(win, NOMBRE + ".ico")
        activo.save(ico, sizes=[(t, t) for t in TAMANOS_ICO])
        png.save(os.path.join(win, NOMBRE + ".png"))
        salidas += [ico, os.path.join(win, NOMBRE + ".png")]
    lin = os.path.join(raiz, "linux")
    if os.path.isdir(lin):
        png.save(os.path.join(lin, NOMBRE + ".png"))
        espera.resize((256, 256), Image.LANCZOS).save(
            os.path.join(lin, NOMBRE + "_espera.png"))
        salidas += [os.path.join(lin, NOMBRE + ".png"),
                    os.path.join(lin, NOMBRE + "_espera.png")]

    if not salidas:
        sys.exit("No se escribio nada: faltan las carpetas windows/ y linux/.")
    print("Icono generado en:")
    for s in salidas:
        print(f"  - {os.path.relpath(s, raiz)}")


if __name__ == "__main__":
    main()
