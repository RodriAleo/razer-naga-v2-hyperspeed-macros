# CLAUDE.md — contexto para mantener este repo

Macros para el ratón **Razer Naga V2 Hyperspeed**. Los 12 botones laterales
están configurados (en Razer Synapse, guardado en memoria onboard) para enviar
**F13–F24**; los scripts capturan esas teclas y ejecutan la macro real.

Hay **dos implementaciones equivalentes** que deben mantenerse sincronizadas:

| Archivo | Sistema | Cómo recargar / probar |
|---------|---------|------------------------|
| `NagaV2_Macros.ahk` | Windows (AutoHotkey v2) | Clic derecho en icono "H" → **Reload Script** |
| `naga_macros.py` | Linux Wayland/X11 (Python `evdev`/`uinput`) | `sudo python3 naga_macros.py` |
| `NagaV2_atajos.png` | Guía de atajos visual (la abre el Botón 5) | Se **regenera** con `generar_guia_atajos.ps1` |
| `generar_guia_atajos.ps1` | Generador de la imagen | `powershell -ExecutionPolicy Bypass -File generar_guia_atajos.ps1` |
| `README.md` | Documentación de usuario | — |

## Mapa de botones (fuente de verdad)

Botón → tecla: **Botón N = F(12+N)** → Botón 1=F13 … Botón 12=F24.

| Botón | Tecla | Acción actual |
|:----:|:----:|---------------|
| 1 | F13 | Alt+Tab rápido (un toque) |
| 2 | F14 | Selector Alt+Tab persistente — anterior |
| 3 | F15 | Selector Alt+Tab persistente — siguiente |
| 4 | F16 | **LIBRE** |
| 5 | F17 | Abrir la guía de atajos (`NagaV2_atajos.png`) |
| 6 | F18 | **LIBRE** |
| 7 | F19 | Pantalla completa (F11) |
| 8 | F20 | **LIBRE** |
| 9 | F21 | **LIBRE** |
| 10 | F22 | **Hypershift 1** (mantener) |
| 11 | F23 | **Hypershift 2** (mantener) |
| 12 | F24 | Vista de tareas (Win+Tab / Super) |

**Hypershift 1 (Botón 10):** rueda=volumen, clic rueda=play/pausa, tilt=pista sig/ant.
**Hypershift 2 (Botón 11):** rueda=zoom, clic rueda=Ctrl+Q, clic derecho=portapapeles, tilt=copiar/pegar.

---

## ⚠️ Al AGREGAR o CAMBIAR una macro — tocar SIEMPRE estos 4 sitios

1. **Windows** → `NagaV2_Macros.ahk`
   - Botón simple: edita el bloque `Fxx::` correspondiente.
   - Combo de Hypershift: edita/añade líneas `F22 & ...` (HS1) o `F23 & ...` (HS2).
2. **Linux** → `naga_macros.py`
   - Botón simple: método `boton_simple()` (usa el número de botón).
   - Combo de Hypershift: método `process()` (ramas `self.hyper1` / `self.hyper2`).
   - Acción de tilt que NO debe repetirse: envolver con `self.once("nombre", ...)`.
3. **Imagen** → editar los arrays de `generar_guia_atajos.ps1` (`$cells` y/o las
   `Section` de Hypershift) y **re-ejecutarlo** para regenerar `NagaV2_atajos.png`.
4. **README** → actualizar las tablas de atajos en `README.md`.

Luego, si procede: `git add . && git commit`.

> Mantener los 4 en coherencia es lo importante. Un cambio que solo toca uno de
> ellos deja el proyecto inconsistente (p. ej. Windows y Linux divergen, o la
> guía de atajos miente).

---

## Equivalencias de sintaxis Windows (AHK v2) ↔ Linux (evdev)

| Acción | AHK (`NagaV2_Macros.ahk`) | Python (`naga_macros.py`) |
|--------|---------------------------|---------------------------|
| Combo de teclas | `Send("^c")` | `self.tap(e.KEY_LEFTCTRL, e.KEY_C)` |
| Tecla suelta | `Send("{F11}")` | `self.tap(e.KEY_F11)` |
| Tecla multimedia | `Send("{Media_Next}")` | `self.tap(e.KEY_NEXTSONG)` |
| Volumen | `Send("{Volume_Up}")` | `self.tap(e.KEY_VOLUMEUP)` |
| Abrir archivo/app | `Run(...)` | `subprocess.Popen(["xdg-open", ruta], close_fds=True, start_new_session=True)` |
| Modificadores | `^`=Ctrl `!`=Alt `+`=Shift `#`=Win | `KEY_LEFTCTRL/LEFTALT/LEFTSHIFT/LEFTMETA` |

---

## Recetas técnicas y gotchas (no romper)

- **Selector Alt+Tab persistente (botones 2/3):**
  - Windows: requiere prefijo `*` en el hotkey (`*F14::`, `*F15::`) **y** modo
    `{Blind}` + `SendMode("Event")`. Sin el `*` solo cuenta la 1ª pulsación
    (porque Alt queda pulsado y la tecla pasa a ser `Alt+Fxx`). Sin `{Blind}`
    el selector se cierra y reabre en cada pulsación.
  - Linux: se mantiene `KEY_LEFTALT` pulsado y se suelta tras `ALTTAB_TIMEOUT`.
- **Hypershift:**
  - Windows: combinaciones personalizadas `F22 & WheelUp::` (F22/F23 como
    tecla prefijo).
  - Linux: `naga_macros.py` **captura (grab)** la interfaz de ratón para poder
    suprimir el scroll normal; reinyecta movimiento y clic izquierdo. El estado
    se lleva con `self.hyper1`/`self.hyper2`.
- **Anti-repetición del tilt:** mantener el tilt genera muchos eventos. Copiar,
  pegar y cambio de pista se ejecutan UNA vez por inclinación
  (AHK: función `TiltUnaVez`; Python: `self.once(...)`). El zoom y el volumen
  SÍ se repiten al girar la rueda (no llevan anti-repetición).
- **Botón 5 / ruta de la imagen:**
  - Windows: `Run(A_ScriptDir . "\NagaV2_atajos.png")` — la imagen debe estar
    junto al `.ahk`. Si se renombra la imagen, actualizar esta línea.
  - Linux: `IMAGE_PATH` se calcula con `os.path.dirname(os.path.abspath(__file__))`
    para ser siempre relativa al directorio del script, sin importar desde dónde
    se arranque.
- **Grab de dispositivos en Linux (crítico):**
  El Naga V2 HS aparece como **5 interfaces** separadas en `/dev/input/`:
  `Mouse`, `Keyboard`, `Naga V2 HS`, `System Control`, `Consumer Control`.
  El script graba (grab) las que tienen `REL_X` (interfaz Mouse) **y** las que
  tienen `KEY_F13` (interfaz Keyboard). Sin grab del Keyboard, las teclas F13–F24
  pasan al sistema y GNOME puede reaccionar a ellas (p. ej. abrir configuración
  de Bluetooth). Las otras 3 interfaces no se graban.
- **Zoom en Linux — usar teclas de numpad:**
  `Ctrl+KEY_EQUAL` y `Ctrl+KEY_MINUS` pasan por el keymap del compositor. En
  layouts no-US producen caracteres inesperados (ej. `^[` = ESC en layout
  español). Usar `Ctrl+KEY_KPPLUS` / `Ctrl+KEY_KPMINUS`: las teclas de numpad
  son layout-independientes y funcionan en Firefox, GNOME Terminal y apps GTK.
  Recordar declarar `KEY_KPPLUS` y `KEY_KPMINUS` en el `UInput(...)`.
- **Prioridad de scheduling en Linux:**
  El script llama `os.sched_setscheduler(0, os.SCHED_FIFO, os.sched_param(10))`
  al arrancar (requiere root). Reduce la latencia de respuesta evitando que el
  kernel desaloje el proceso mientras procesa un evento de entrada.

## Diferencias de plataforma a recordar

- **Portapapeles (HS2 + clic derecho):** en Windows es `Win+V` nativo; en Linux
  `Super+V` en GNOME 44+ abre el panel de notificaciones (no el portapapeles).
  Usar la constante `PORTAPAPELES_CMD` en `naga_macros.py` para configurar el
  gestor instalado (ej. `["copyq", "toggle"]`).
- **Botón 12:** Windows `Win+Tab` (Task View); Linux tecla **Super** (overview GNOME).
- **Ctrl+Q (capturas):** asume el mismo atajo en la app de capturas de cada SO.
- **Tilt derecha (HS1 = pista siguiente / HS2 = pegar) — LIMITACIÓN LINUX:**
  El firmware del Naga V2 HS reporta tilt derecha como `REL_WHEEL +1` (rueda
  vertical arriba), idéntico a scroll arriba. No se puede distinguir en software.
  En Linux, tilt derecha actúa igual que scroll arriba (volumen / zoom in).
  Las funciones "pista siguiente" y "pegar vía tilt" están **perdidas en Linux**
  a menos que se reconfigure el tilt en Razer Synapse (Windows) para que mande
  una tecla personalizada en vez de scroll.

## Autoarranque

- **Windows:** acceso directo del `.ahk` en `shell:startup`
  (`%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup`). Si se mueve el
  repo, rehacer el acceso directo (apunta por ruta absoluta).
- **Linux:** servicio systemd de usuario (ver `README.md`).
