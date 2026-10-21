# Changelog

Fuente única de la versión de las macros: los scripts (Windows y Linux) y la
guía de atajos leen el número de la **primera** entrada `## [X.Y.Z]` de
este archivo.

Para publicar una versión: añade una entrada nueva **arriba del todo**,
regenera la guía (`python generar_guia_atajos.py`), haz commit y etiqueta
(`git tag vX.Y.Z`). Criterio: PARCHE = arreglo sin cambiar atajos; MENOR =
macro nueva o cambiada; MAYOR = cambio que obliga a reconfigurar algo
(Synapse, rutas, autoarranque).

## [2.2.1] - 2026-10-21

### Corregido
- Linux: la guía del Botón 5 salía vacía si Pillow estaba instalado sin
  `PIL.ImageTk` (en Debian/Ubuntu viene aparte, `python3-pil.imagetk`). Ahora
  usa el `PhotoImage` de Tk en ese caso, y `instalar.sh` avisa si falta.

### Cambiado
- Linux: la guía del Botón 5 es un 25 % más grande. `generar_guia_atajos.py`
  la dibuja directamente a ese tamaño (`DESTINOS`: escala por carpeta), así el
  texto sale nítido; la de Windows queda igual.

## [2.2.0] - 2026-10-19

### Añadido
- Icono nuevo de la app (círculo verde con una «N»), generado con
  `generar_icono.py`. Se usa en el `.exe`, los accesos directos, el lanzador de
  Linux y la bandeja (en Linux, naranja mientras espera al ratón).
- Instalador de Windows (`windows/instalar.bat`): accesos con icono en el menú
  Inicio y el escritorio, más el arranque automático.
- Instalador de Linux (`linux/instalar.sh`): servicio systemd, icono y lanzador
  "Naga V2 Macros" en el menú de aplicaciones; abrirlo (re)arranca las macros.
- Windows: abrir la app con otra instancia en marcha ofrece reiniciarla (útil
  si dejó de responder).

### Cambiado
- El acceso directo del autoarranque de Windows usa el icono de la app.

## [2.1.0] - 2026-10-16

### Añadido
- Linux: la guía de atajos se muestra como overlay **mientras se mantiene** el
  Botón 5, igual que en Windows (sin robar el foco y centrada en el monitor del
  puntero).

### Cambiado
- La guía indica que el Botón 5 se mantiene pulsado para verla.

## [2.0.0] - 2026-10-16

### Cambiado
- La carpeta de Windows pasa a llamarse `windows/`. Si ya tenías el
  autoarranque activado, vuelve a ejecutar `windows/autoarranque.ps1` (el
  acceso directo guarda la ruta antigua) y recompila el `.exe` con
  `windows/compilar_exe.ps1`.

## [1.1.0] - 2026-10-16

### Añadido
- `CHANGELOG.md` como fuente única de la versión y del historial de cambios.
- La guía de atajos muestra el número de versión.

## [1.0.0] - 2026-10-16

Primera versión numerada. Recoge todo lo hecho hasta ahora.

### Añadido
- Número de versión visible en el icono de la bandeja (tooltip y primera línea
  del menú) en Windows y Linux.
- Botón 4: siguiente pestaña (`Ctrl+Tab`).
- Windows: proceso Python normal (compatible con los anticheat de juegos), con
  ejecutable `.exe`, icono propio, instancia única, overlay de la guía con el
  Botón 5 y "Reiniciar" en la bandeja.
- Linux: icono en la bandeja (verde = activo, naranja = esperando ratón),
  reconexión automática y servicio systemd de usuario para el autoarranque.
- Tilt reasignado en Synapse a `Shift+F13/F14`: scroll lateral continuo sin
  hypershift, pista siguiente/anterior (HS1) y copiar/pegar (HS2).

### Corregido
- Linux: el scroll lateral del tilt no se movía (faltaba el evento hi-res).
- Windows: zoom por aplicación y teclas inyectadas que llegaban mal.
