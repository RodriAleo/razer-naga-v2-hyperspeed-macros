# Changelog

Fuente única de la versión de las macros: los scripts (Windows Python y Linux)
y la guía de atajos leen el número de la **primera** entrada `## [X.Y.Z]` de
este archivo.

Para publicar una versión: añade una entrada nueva **arriba del todo**,
regenera la guía (`python generar_guia_atajos.py`), haz commit y etiqueta
(`git tag vX.Y.Z`). Criterio: PARCHE = arreglo sin cambiar atajos; MENOR =
macro nueva o cambiada; MAYOR = cambio que obliga a reconfigurar algo
(Synapse, rutas, autoarranque).

## [1.1.0] - 2026-10-16

### Añadido
- `CHANGELOG.md` como fuente única de la versión y del historial de cambios.
- La guía de atajos muestra el número de versión.

### Deprecado
- Versión AutoHotkey (`windows-ahk/`): en Windows solo se usa la versión
  Python. Queda congelada en esta versión como referencia y ya no se actualiza.

## [1.0.0] - 2026-10-16

Primera versión numerada. Recoge todo lo hecho hasta ahora.

### Añadido
- Número de versión visible en el icono de la bandeja (tooltip y primera línea
  del menú) en Windows Python, Windows AHK y Linux.
- Botón 4: siguiente pestaña (`Ctrl+Tab`).
- Windows: versión en Python sin AutoHotkey (por los anticheat), con
  ejecutable `.exe`, icono propio, instancia única, overlay de la guía con el
  Botón 5 y "Reiniciar" en la bandeja.
- Linux: icono en la bandeja (verde = activo, naranja = esperando ratón),
  reconexión automática y servicio systemd de usuario para el autoarranque.
- Tilt reasignado en Synapse a `Shift+F13/F14`: scroll lateral continuo sin
  hypershift, pista siguiente/anterior (HS1) y copiar/pegar (HS2).

### Corregido
- Linux: el scroll lateral del tilt no se movía (faltaba el evento hi-res).
- Windows: zoom por aplicación y teclas inyectadas que llegaban mal.
