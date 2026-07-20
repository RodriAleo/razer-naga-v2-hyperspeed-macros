# CLAUDE.md — contexto para mantener este repo

Macros para el ratón **Razer Naga V2 Hyperspeed**. Los 12 botones laterales
están configurados (en Razer Synapse, guardado en memoria onboard) para enviar
**F13–F24**; los scripts capturan esas teclas y ejecutan la macro real.

Hay **dos implementaciones equivalentes** que deben mantenerse sincronizadas:

| Archivo | Sistema | Cómo recargar / probar |
|---------|---------|------------------------|
| `NagaV2_Macros.ahk` | Windows (AutoHotkey v2) | Clic derecho en icono "H" → **Reload Script** |
| `naga_macros.py` | Linux Wayland/X11 (Python `evdev`/`uinput`) | `systemctl --user restart naga-macros` (o `sudo -E python3 naga_macros.py`) |
| `naga-macros.service` | Linux — unidad systemd de usuario (autoarranque) | `cp` a `~/.config/systemd/user/`, ajustar `ExecStart`, `enable --now` |
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
**Tilt sin hypershift:** desplazamiento lateral continuo (scroll horizontal) mientras se mantiene.

> **El tilt se reasigna en Synapse a teclado:** tilt derecha=`Shift+F13`,
> tilt izquierda=`Shift+F14`. El firmware reporta el tilt como un evento de
> rueda que en Linux no se distingue del scroll; por eso ambos scripts capturan
> ese combo y lo traducen al gesto de tilt (scroll lateral / sig-ant / copiar-pegar
> según el hypershift). Sin esta reasignación el tilt derecho se pierde en Linux.
> **El combo NO lleva Ctrl a propósito:** en Windows `Ctrl`+rueda = zoom y no se
> puede evitar de forma fiable si Synapse mantiene `Ctrl` pulsado; con solo
> `Shift`, la rueda vertical se vuelve scroll horizontal nativo (ver receta abajo).

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
  - Windows: se listan **dos hotkeys explícitos** por botón — `F14::` (1ª
    pulsación, sin modificadores) y `!F14::` (pulsaciones con Alt sostenido por
    el selector) — más modo `{Blind}` + `SendMode("Event")`. Sin cubrir el caso
    `Alt` solo cuenta la 1ª pulsación (Alt queda pulsado y la tecla pasa a ser
    `Alt+Fxx`); sin `{Blind}` el selector se cierra/reabre en cada pulsación.
    **NO usar el comodín `*F14::`**: capturaría también `Shift+F14`, que es el
    tilt izquierdo, y abriría el selector por error (ver receta del tilt).
  - Linux: se mantiene `KEY_LEFTALT` pulsado y se suelta tras `ALTTAB_TIMEOUT`.
- **Hypershift:**
  - Windows: combinaciones personalizadas `F22 & WheelUp::` (F22/F23 como
    tecla prefijo).
  - Linux: `naga_macros.py` **captura (grab)** la interfaz de ratón para poder
    suprimir el scroll normal; reinyecta movimiento y clic izquierdo. El estado
    se lleva con `self.hyper1`/`self.hyper2`.
- **Tilt reasignado a teclado (Shift+F13/F14):** el tilt ya NO llega como
  evento de rueda sino como combo de teclado (ver el mapa de botones). **Sin
  Ctrl a propósito** (con Ctrl la rueda haría zoom en Windows). Cada script lo
  traduce según el hypershift:
  - Windows (AHK): hotkeys `+F13::` / `+F14::` → función `TiltLateral(lado)`,
    que mira `GetKeyState("F22"/"F23","P")` para decidir HS1/HS2/sin-HS. Las viejas
    líneas `F22/F23 & WheelLeft/Right` se eliminaron.
  - Linux (Python): en `process()`, F13/F14 con `shift_held` se desvían a
    `tilt_combo(code, value)`; se rastrea el estado de `KEY_LEFTSHIFT` (y
    `RIGHTSHIFT`; `Ctrl` también, por si el binding aún lo trae). Ojo: depende de
    que Synapse mande el modificador ANTES que la F-key (orden estándar).
- **Desplazamiento lateral continuo (tilt sin hypershift):** se repite mientras
  se mantiene el tilt.
  - Windows (AHK): timer `ScrollTick` que manda rueda **horizontal nativa**
    `SendEvent("{WheelRight/Left}")`. Clave del **anti-zoom**: el binding es
    `Shift+Fxx` **sin Ctrl** (con Ctrl la rueda haría zoom y no se puede soltar
    Ctrl de forma fiable, Synapse lo mantiene). El `Shift` solo distingue el tilt
    del botón; NO se usa para el scroll (Synapse lo suelta enseguida, así que
    depender de `Shift`+rueda vertical daba scroll vertical). **Stop doble:**
    hotkey `*Fxx up::DetenerScroll()` (event-driven) + respaldo por sondeo
    `GetKeyState(tecla,"P")` en `ScrollTick`. Usar **`SendEvent`, NO `Send`**:
    `Send`=`SendInput` (por `SendMode("Input")`) congela el hook y se comía el
    soltado, dejando el scroll trabado. `scrollLado` lleva el estado; un `#HotIf
    (scrollLado=...)` ignora las auto-repeticiones de la F-key (botones 1/2).
  - Linux (Python): bucle `run()` con un deadline `self.next_scroll` (intervalo
    `TILT_SCROLL_INTERVAL`), llamando a `self.hscroll(...)`; se frena al recibir
    el soltado (`value == 0`) de `scroll_key`. Sin problema de zoom: los
    modificadores del combo se capturan (grab) y nunca llegan al compositor.
- **⚠️ Scroll sintético en Linux — SIEMPRE emitir el evento de alta resolución:**
  el `UInput` declara `REL_WHEEL_HI_RES`/`REL_HWHEEL_HI_RES`, y **libinput, en
  cuanto un dispositivo anuncia hi-res, usa SOLO ese eje y DESCARTA los
  `REL_WHEEL`/`REL_HWHEEL` clásicos** (los considera derivados). Emitir solo el
  evento clásico hace que el scroll **no se mueva en absoluto** (bug real: el
  desplazamiento lateral del tilt no funcionaba). El helper `hscroll(steps)`
  manda los dos en el mismo frame — `REL_HWHEEL_HI_RES = steps * HI_RES_PER_STEP`
  (120 = 1 muesca, constante del kernel) y `REL_HWHEEL = steps` — igual que un
  ratón real; no duplica el scroll porque libinput ignora el clásico si hay
  hi-res. El scroll vertical normal no sufría esto porque se **reenvía tal cual**
  llega del ratón (ya trae sus propios eventos hi-res). Si algún día se añade
  scroll vertical sintético, hay que hacer lo mismo con `REL_WHEEL_HI_RES`.
- **Anti-repetición del tilt (en hypershift):** mantener el tilt genera muchos
  eventos. Copiar, pegar y cambio de pista se ejecutan UNA vez por inclinación
  (AHK: función `TiltUnaVez`; Python: `self.once(...)`). El zoom y el volumen
  SÍ se repiten al girar la rueda (no llevan anti-repetición). El scroll lateral
  sin hypershift SÍ es continuo (no usa anti-repetición).
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
  kernel desaloje el proceso mientras procesa un evento de entrada. **Corriendo
  como servicio de usuario (sin root) esto falla y solo imprime un aviso** — es
  inofensivo, solo se pierde la optimización de latencia.
- **Bandeja del sistema y reconexión (Linux):** `main()` levanta un hilo
  `_worker` con el bucle de macros y deja el hilo principal para `pystray`
  (lo exige la librería). Puntos a respetar:
  - `pystray`/`Pillow` son **opcionales**: si no están, `_HAS_TRAY` es `False` y
    `_worker()` corre en primer plano. No romper ese camino.
  - Ícono **verde** = ratón detectado y activo; **naranja** = esperando ratón.
  - Si el Naga no está o se desconecta, `_open_devices()`/`run()` lanzan
    `OSError(errno 19)` y `_worker` espera con `_wait_for_naga()` (que además
    exige que el dispositivo siga presente tras `settle` segundos, porque el
    kernel registra las 5 interfaces de forma escalonada).
  - "Reiniciar" del menú solo hace `_stop.set()`: `run()` sale y el worker crea
    una instancia nueva. Por eso el `select()` de `run()` lleva un tope de 0.25 s,
    para mirar `_stop` con frecuencia.
  - El menú **Salir** termina con código 0 → la unidad systemd usa
    `Restart=on-failure` (no `always`) para que quedarse cerrado sea posible.
- **Fallback de detección de dispositivo:** si ningún dispositivo tiene "naga" en
  el nombre, se busca uno con `KEY_F13` **y sin `KEY_A`**. El `sin KEY_A` excluye
  teclados reales (p. ej. Logitech) que también declaran F13 y que si no serían
  capturados por error, dejando el teclado inservible.

## Diferencias de plataforma a recordar

- **Portapapeles (HS2 + clic derecho):** en Windows es `Win+V` nativo; en Linux
  `Super+V` en GNOME 44+ abre el panel de notificaciones (no el portapapeles).
  Usar la constante `PORTAPAPELES_CMD` en `naga_macros.py` para configurar el
  gestor instalado (ej. `["copyq", "toggle"]`).
- **Botón 12:** Windows `Win+Tab` (Task View); Linux tecla **Super** (overview GNOME).
- **Ctrl+Q (capturas):** asume el mismo atajo en la app de capturas de cada SO.
- **Tilt — RESUELTO vía reasignación en Synapse (antes era limitación Linux):**
  El firmware reporta el tilt como evento de rueda (`REL_WHEEL`/`REL_HWHEEL`) que
  en Linux no se distingue del scroll normal (el tilt derecho se perdía). Solución
  adoptada: el tilt se reasigna en Synapse a `Shift+F13` (derecha) /
  `Shift+F14` (izquierda) y los scripts lo traducen (ver receta "Tilt
  reasignado a teclado" arriba). Así funciona igual en Windows y Linux. Requiere
  que esa reasignación esté guardada en la memoria onboard del ratón.

## Autoarranque

- **Windows:** acceso directo del `.ahk` en `shell:startup`
  (`%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup`). Si se mueve el
  repo, rehacer el acceso directo (apunta por ruta absoluta).
- **Linux:** servicio systemd **de usuario**, versionado en el repo como
  `naga-macros.service` (instrucciones de instalación en `README.md`). Es de
  usuario y no de sistema a propósito: el ícono de bandeja y la inyección de
  teclas necesitan la sesión gráfica. Tres ajustes que no hay que cambiar sin
  entender por qué:
  - `WantedBy=/After=/PartOf=graphical-session.target` (**no** `default.target`):
    con `default.target` arranca antes de que exista la sesión gráfica y el
    ícono de bandeja no aparece.
  - `Environment=PYTHONUNBUFFERED=1`: sin esto Python bufferiza `stdout` al no
    haber tty y los `print()` solo llegan al journal cuando el proceso muere
    (despista mucho al depurar: parece que el script no imprime nada).
  - `Restart=on-failure` (**no** `always`): el menú "Salir" sale con código 0 y
    debe quedarse cerrado.
  - `ExecStart` debe apuntar al intérprete que tenga `evdev`/`pystray`/`Pillow`
    (si es conda o venv, a ESE python). La copia instalada vive en
    `~/.config/systemd/user/` y **no** se actualiza sola al cambiar la del repo.
  - Tras editar `naga_macros.py`: `systemctl --user restart naga-macros`.
    Ver log en vivo: `journalctl --user -u naga-macros -f`.
