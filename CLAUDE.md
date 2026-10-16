# CLAUDE.md — contexto para mantener este repo

Macros para el ratón **Razer Naga V2 Hyperspeed**. Los 12 botones laterales
están configurados (en Razer Synapse, guardado en memoria onboard) para enviar
**F13–F24**; los scripts capturan esas teclas y ejecutan la macro real.

Hay **tres implementaciones equivalentes** que deben mantenerse sincronizadas,
cada una en su carpeta:

```
├── windows-python/   naga_macros_win.py · NagaV2_Macros_Win.vbs · autoarranque.ps1 · NagaV2_atajos.png
├── windows-ahk/      NagaV2_Macros.ahk · NagaV2_atajos.png
├── linux/            naga_macros.py · naga-macros.service · NagaV2_atajos.png
└── generar_guia_atajos.py   (genera la imagen en las 3 carpetas)
```

| Archivo | Sistema | Cómo recargar / probar |
|---------|---------|------------------------|
| `windows-python/naga_macros_win.py` | Windows (Python + ctypes, **sin AHK**) | Cerrar desde la bandeja y volver a lanzar el `.vbs` |
| `windows-ahk/NagaV2_Macros.ahk` | Windows (AutoHotkey v2) | Clic derecho en icono "H" → **Reload Script** |
| `linux/naga_macros.py` | Linux Wayland/X11 (Python `evdev`/`uinput`) | `systemctl --user restart naga-macros` (o `sudo -E python3 linux/naga_macros.py`) |
| `windows-python/NagaV2_Macros_Win.vbs` | Windows — lanzador sin consola (`pythonw`) | Doble clic |
| `windows-python/autoarranque.ps1` | Windows — crea/borra el acceso directo en `shell:startup` | `-Estado` para consultar, `-Quitar` para desactivar |
| `linux/naga-macros.service` | Linux — unidad systemd de usuario (autoarranque) | `cp` a `~/.config/systemd/user/`, ajustar `ExecStart`, `enable --now` |
| `NagaV2_atajos.png` (×3) | Guía de atajos visual (la abre el Botón 5) | Se **regenera** con `generar_guia_atajos.py` |
| `generar_guia_atajos.py` | Generador de la imagen (Pillow, multiplataforma) | `python generar_guia_atajos.py` |
| `README.md` | Documentación de usuario | — |

> **La imagen está duplicada a propósito** en las tres carpetas: cada script la
> abre con una ruta relativa a sí mismo, así cada versión es autocontenida. El
> generador escribe las tres de una pasada — **no editar una copia a mano**.

> **¿Por qué dos versiones de Windows?** El `.ahk` y `naga_macros_win.py` hacen
> lo mismo; el clon en Python existe porque algunos **anticheat** de juegos
> exigen cerrar AutoHotkey para arrancar. Se mantiene el `.ahk` como referencia
> histórica, pero **al cambiar una macro hay que tocar ambos** (ver la sección
> de los sitios a tocar).

## Mapa de botones (fuente de verdad)

Botón → tecla: **Botón N = F(12+N)** → Botón 1=F13 … Botón 12=F24.

| Botón | Tecla | Acción actual |
|:----:|:----:|---------------|
| 1 | F13 | Alt+Tab rápido (un toque) |
| 2 | F14 | Selector Alt+Tab persistente — anterior |
| 3 | F15 | Selector Alt+Tab persistente — siguiente |
| 4 | F16 | Siguiente pestaña (Ctrl+Tab) |
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

## ⚠️ Al AGREGAR o CAMBIAR una macro — tocar SIEMPRE estos 5 sitios

1. **Windows / Python** → `windows-python/naga_macros_win.py`
   - Botón simple: método `boton_simple()` (usa el número de botón).
   - Combo de Hypershift: método `on_mouse()` (ramas `self.hyper1` / `self.hyper2`).
   - Tilt: método `tilt()`. Acción que NO debe repetirse: envolver con `self.once(...)`.
   - Acciones disparadas por el tilt: usar `tap_limpio()`, no `tap()` (ver recetas).
2. **Windows / AHK** → `windows-ahk/NagaV2_Macros.ahk`
   - Botón simple: edita el bloque `Fxx::` correspondiente.
   - Combo de Hypershift: edita/añade líneas `F22 & ...` (HS1) o `F23 & ...` (HS2).
3. **Linux** → `linux/naga_macros.py`
   - Botón simple: método `boton_simple()` (usa el número de botón).
   - Combo de Hypershift: método `process()` (ramas `self.hyper1` / `self.hyper2`).
   - Acción de tilt que NO debe repetirse: envolver con `self.once("nombre", ...)`.
4. **Imagen** → editar las listas `CELDAS` y/o `SECCIONES` de
   `generar_guia_atajos.py` y **re-ejecutarlo** (`python generar_guia_atajos.py`):
   regenera las tres copias de `NagaV2_atajos.png` de una pasada.
5. **README** → actualizar las tablas de atajos en `README.md`.

Luego, si procede: `git add . && git commit`.

> Mantener los 4 en coherencia es lo importante. Un cambio que solo toca uno de
> ellos deja el proyecto inconsistente (p. ej. Windows y Linux divergen, o la
> guía de atajos miente).

---

## Versionado

Las tres implementaciones llevan **el mismo número de versión** (SemVer,
`MAYOR.MENOR.PARCHE`), visible en el icono de la bandeja: en el tooltip y como
primera línea (deshabilitada) del menú. Al publicar un cambio, subirlo en los
**tres** sitios a la vez:

| Archivo | Dónde |
|---------|-------|
| `windows-python/naga_macros_win.py` | `VERSION = "x.y.z"` (sección CONFIGURACION) |
| `windows-ahk/NagaV2_Macros.ahk` | `NAGA_VERSION := "x.y.z"` y la directiva `;@Ahk2Exe-SetVersion` |
| `linux/naga_macros.py` | `VERSION = "x.y.z"` (sección CONFIGURACION) |

Criterio: **PARCHE** = arreglo sin cambiar atajos; **MENOR** = macro nueva o
cambiada; **MAYOR** = cambio que obliga a reconfigurar algo (Synapse, rutas,
autoarranque). Tras el commit, etiquetar: `git tag vX.Y.Z`. El `.exe` de
Windows hay que **recompilarlo** (`compilar_exe.ps1`) para que muestre la
versión nueva.

---

## Equivalencias de sintaxis AHK ↔ Windows/Python ↔ Linux/evdev

| Acción | AHK (`NagaV2_Macros.ahk`) | Win/Python (`naga_macros_win.py`) | Linux (`naga_macros.py`) |
|--------|---------------------------|-----------------------------------|--------------------------|
| Combo de teclas | `Send("^c")` | `tap(VK["CONTROL"], VK["C"])` | `self.tap(e.KEY_LEFTCTRL, e.KEY_C)` |
| Tecla suelta | `Send("{F11}")` | `tap(VK["F11"])` | `self.tap(e.KEY_F11)` |
| Tecla multimedia | `Send("{Media_Next}")` | `tap(VK["MEDIA_NEXT"])` | `self.tap(e.KEY_NEXTSONG)` |
| Volumen | `Send("{Volume_Up}")` | `tap(VK["VOLUME_UP"])` | `self.tap(e.KEY_VOLUMEUP)` |
| Scroll lateral | `SendEvent("{WheelRight}")` | `wheel(horizontal=True, notches=1)` | `self.hscroll(1)` |
| Abrir archivo/app | `Run(...)` | `os.startfile(ruta)` | `subprocess.Popen(["xdg-open", ruta], close_fds=True, start_new_session=True)` |
| Modificadores | `^`=Ctrl `!`=Alt `+`=Shift `#`=Win | `VK["CONTROL"/"MENU"/"SHIFT"/"LWIN"]` | `KEY_LEFTCTRL/LEFTALT/LEFTSHIFT/LEFTMETA` |

---

## Recetas técnicas y gotchas (no romper)

### Windows/Python (`naga_macros_win.py`) — específicos de esta implementación

- **Motivo de existir:** los anticheat que exigen cerrar AutoHotkey. Es un
  proceso Python normal. Usa **solo `ctypes`** (nada de `pip` para el núcleo):
  menos dependencias y menor superficie de detección. `pystray`/`Pillow` son
  **opcionales** (solo el icono de bandeja); si faltan, el script corre igual.
- **Hooks low-level + bomba de mensajes:** `WH_KEYBOARD_LL`/`WH_MOUSE_LL` **solo
  funcionan si el hilo que los instala bombea mensajes** (`GetMessageW`). Por eso
  `HookLoop.run()` bloquea. Con bandeja, los hooks van en un hilo daemon y
  `pystray` se queda con el hilo principal (lo exige en Windows).
- **⚠️ Referencias vivas de los callbacks:** `self._kb_proc`/`self._ms_proc`
  guardan los `HOOKPROC`. Si se pasan inline a `SetWindowsHookExW`, el GC de
  Python los libera y **Windows crashea** al invocar el callback. No inline-ar.
- **⚠️ Anti-realimentación:** todo lo que inyectamos lleva `dwExtraInfo =
  INJECTED_TAG` ("NAGA") y el hook **ignora** los eventos con esa marca. Sin eso,
  la rueda sintética del scroll lateral se volvería a procesar → bucle infinito.
- **⚠️ Modificadores al LEER del hook — usar los VK laterales:** el hook
  low-level reporta **`VK_LSHIFT` (0xA0) / `VK_RSHIFT` (0xA1)**, *nunca* el
  genérico `VK_SHIFT` (0x10). Comparar solo con el genérico hacía que el tilt no
  se detectara y `Shift+F13`/`Shift+F14` cayeran al manejo de botón normal (bug
  real: el tilt derecho hacía Alt+Tab y el izquierdo abría el selector, incluso
  en hypershift). Al **enviar** con `SendInput`, en cambio, el genérico sí sirve.
  Como red extra se consulta `is_physically_down(VK["SHIFT"])`, que cubre el caso
  de que Synapse mande la F-key antes que el modificador.
- **Suprimir una tecla:** el callback devuelve `1` (en vez de `CallNextHookEx`).
  Las F13–F24 **siempre** se suprimen, para que ninguna app las vea.
- **⚠️ Al consumir un clic, suprimir TAMBIÉN su evento de soltado:** si se
  suprime `WM_RBUTTONDOWN` pero no `WM_RBUTTONUP`, el "up" se escapa y llega a
  la ventana que la macro acaba de abrir — el panel del portapapeles (`Win+V`)
  se abría y se cerraba solo por clic-fuera. `BOTON_UP` mapea down→up y
  `self._botones_consumidos` guarda los pendientes. Ese chequeo va **antes** del
  de hypershift: si se suelta el hypershift entre el down y el up, el up debe
  suprimirse igual (si no, se escapa un clic suelto a la app).
- **Anti-repetición del tilt:** Windows manda auto-repeticiones al mantener la
  tecla. Se ignoran comparando `self.scroll_side != side` antes de re-disparar.
- **⚠️ Acciones del tilt → usar `tap_limpio()`, NO `tap()`:** Synapse mantiene
  pulsado el `Shift` del combo `Shift+F13/F14`, así que un `tap(CTRL, C)` normal
  llega a la app como **`Ctrl+Shift+C`** — que no es copiar (en navegadores abre
  el inspector). `tap_limpio()` suelta `LSHIFT`/`RSHIFT` **en la misma llamada a
  `SendInput`** (atómico, para que Synapse no re-afirme el Shift en el medio).
  El AHK no sufría esto porque `Send("^c")` ya neutraliza los modificadores del
  hotkey. Ojo con el diagnóstico: el fallo **se disimula en pegar**, porque
  `Ctrl+Shift+V` es "pegar sin formato" y aparenta funcionar — el síntoma visible
  fue "copia no, pega sí".
- **⚠️ El scroll lateral corre en un HILO DEDICADO con `Event`, no con timers.**
  Dos razones, ambas por bugs reales:
  1. `threading.Timer` reprogramado por paso creaba un hilo nuevo cada 60 ms
     (jitter perceptible).
  2. Más grave: si cada tick exige `is_physically_down()` para **continuar**, el
     scroll se corta. `GetAsyncKeyState` **no es fiable con teclas que nosotros
     mismos suprimimos**, así que el bucle moría tras el primer paso y solo
     revivía con la auto-repetición de Windows → *"se mueve un poco, frena,
     continúa"*, con un retardo inicial igual al typematic delay.
  Regla: **el sondeo nunca decide si continuar**, solo el soltado.
- **Stop del scroll — primario + watchdog:** el keyup de la F-key es el stop real
  (el hook **siempre** lo ve, aunque la tecla se suprima) y activa `stop_evt`.
  El watchdog (`TILT_WATCHDOG`) solo corta si dejan de llegar *tanto* el keyup
  *como* las auto-repeticiones; debe ser **mayor que el retardo inicial de
  auto-repetición de Windows** (~0,5 s) o cortaría el scroll a mitad.
  Las auto-repeticiones no reinician el scroll: llaman a `scroll_refresh()`.
- **⚠️ Rellenar `wScan` en las teclas inyectadas** (`MapVirtualKeyW(vk, 0)`), no
  dejarlo en 0. Las apps **Chromium** (Edge, Chrome, Electron) derivan el `code`
  del evento DOM del **scan code**, no del virtual key: con `wScan=0` identifican
  mal la tecla. Bug real: en Google Docs dentro de Edge el zoom con `Ctrl +/−`
  no se comportaba como el del teclado físico.
- **Zoom por teclado — fila principal, NO numpad (en Windows):** `ZOOM_CON_NUMPAD`
  (por defecto `False`) usa `VK_OEM_PLUS`/`VK_OEM_MINUS`, que es lo que hacía el
  `.ahk` con `Send("^-")` y lo que esperan los navegadores. **Ojo con "unificar"
  esto con Linux:** allá se usa el numpad a propósito (`KEY_KPPLUS`/`KEY_KPMINUS`)
  porque los OEM pasan por el keymap del compositor y en layouts no-US producen
  caracteres raros. En Windows ese problema no existe y el numpad, en cambio,
  algunas apps web lo tratan distinto. Son decisiones opuestas por buenas razones.
- **Comportamiento por aplicación (solo esta implementación):** `app_en_foco()`
  devuelve el `.exe` de la ventana activa
  (`GetForegroundWindow` → `GetWindowThreadProcessId` → `OpenProcess` con
  `PROCESS_QUERY_LIMITED_INFORMATION` → `QueryFullProcessImageNameW`). Se usa
  para el zoom: las apps de `ZOOM_CON_RUEDA` (OneNote) reciben `Ctrl+rueda` vía
  `wheel_ctrl()` en vez de `Ctrl + numpad +/−`, porque no responden al atajo de
  teclado. **El resultado se cachea `APP_CACHE_TTL` (0,3 s)**: al girar la rueda
  esto se consultaría decenas de veces por segundo. `wheel_ctrl()` manda
  `Ctrl↓ + rueda + Ctrl↑` en **un solo `SendInput`** (misma lección que
  `tap_limpio`: si se separa, el modificador se pierde o lo pisa Synapse).
  ⚠️ **Rompe a propósito la paridad de las 3 implementaciones**: es una función
  exclusiva de Windows/Python (el AHK y Linux siempre usan `Ctrl + +/−`). Si se
  agregan más comportamientos por app, documentarlo en el README.
- **⚠️ Zoom con Ctrl+rueda → los 3 eventos en UN `SendInput`** (`wheel_ctrl()`).
  El estado del teclado que ve la app está sincronizado con el **orden de los
  mensajes**, no con el reloj: al procesar la rueda verá el `Ctrl` pulsado
  aunque en tiempo real ya se haya soltado. **No separar el `Ctrl↑`.**
  Se intentó "sostener" el Ctrl entre muescas (soltándolo con un temporizador o
  al soltar el hypershift) y salió peor: el `Ctrl↑` llegaba **antes** de que
  OneNote procesara la rueda, así que la leía sin Ctrl y **hacía scroll en vez
  de zoom** — el síntoma era "al soltar el HS2 la página baja". Además obligaba
  a mantener el hypershift hasta que la app reaccionara.
  Corolario: cada muesca es un gesto completo e independiente, y `ZOOM_RUEDA_STEPS`
  manda el delta en **un** evento de rueda (`notches * 120`) en lugar de varios
  eventos de una muesca: menos mensajes que procesar.

### Latencia — lo que se midió y lo que sí importa

Ante una queja de "va con retardo", medir antes de tocar. Descartados por
benchmark (no son el problema): `app_en_foco()` sin caché = **0,03 ms**, el
`cast` de `MSLLHOOKSTRUCT` = **0,0008 ms**. Lo que sí cuenta:

- **Gestos partidos en trozos** (el caso real del zoom, ver arriba): no es
  latencia del script sino de cómo la app interpreta la secuencia.
- **`sys.setswitchinterval(0.001)`** en `main()`: el intervalo del GIL es 5 ms
  por defecto, así que si otro hilo (bandeja, scroll lateral) lo tiene tomado,
  el callback del hook espera hasta ese tiempo. Bajarlo a 1 ms recorta esa cola.
- **Ruta rápida del hook de ratón** (`MOUSE_INTERESANTES`): el ratón emite
  `WM_MOUSEMOVE` a ~1000 Hz; comprobar el mensaje **antes** de leer la
  estructura evita ese trabajo en cada movimiento del puntero.
- **Sacar las llamadas a la API del camino crítico**: `app_en_foco()` se
  resuelve al **activar el Hypershift 2**, no en cada muesca (la app en foco no
  cambia mientras se mantiene pulsado).
- **`SetThreadPriority(THREAD_PRIORITY_HIGHEST)`** en el hilo de los hooks:
  Windows da un plazo limitado al callback (`LowLevelHooksTimeout`) y, si se
  agota repetidamente, **deja de llamarlo** (las macros dejarían de responder).
- **⚠️ Instancia única (mutex `Local\NagaV2MacrosHyperspeed`):** el mismo
  nombre para el `.py` y el `.exe`, así **no pueden convivir**. Dos instancias
  instalan dos juegos de hooks: cada tecla se procesa dos veces o gana la vieja
  y tapa los cambios (pasó de verdad). `tomar_instancia()` **reintenta ~3 s**
  porque el "Reiniciar" de la bandeja arranca el relevo antes de que la vieja
  termine de salir; `relanzar()` llama a `soltar_instancia()` antes del `Popen`.
- **Compilación a `.exe` (`compilar_exe.ps1`, PyInstaller onefile):** el `.exe`
  **no se versiona** (`.gitignore`), es un artefacto. Lo que cambia al estar
  "congelado" y hay que respetar:
  - `__file__` apunta a la carpeta temporal de extracción, **no** a donde vive
    el `.exe`. Por eso `BASE_DIR` usa `sys.executable` si `sys.frozen`, y
    `_recurso()` busca primero junto al `.exe` y luego en `sys._MEIPASS`.
  - `relanzar()` debe ejecutar `sys.executable` **sin argumentos** (el `.exe` ya
    es el programa); pasarle el `.py` no funcionaría.
  - Al probar el `.exe`, **esperar ~10 s**: en onefile el primer arranque
    descomprime a disco. Probarlo antes hace creer que no funciona (pasó).
  - Con `--noconsole` no hay stdout: los `print()` de diagnóstico no se ven. Para
    depurar, compilar sin `--noconsole`.
- **Lanzador sin consola:** `NagaV2_Macros_Win.vbs` ejecuta `pythonw.exe`. Para
  el autoarranque va un acceso directo del `.vbs` en `shell:startup`.
- **Overlay de la guía (Botón 5 mantenido) — `GuiaOverlay`:** Tk **no es
  thread-safe** y quiere su propio `mainloop`, así que vive en un hilo dedicado;
  el hook solo levanta/baja un `Event` y el hilo de Tk lo sondea cada 30 ms.
  **Nunca llamar a Tk desde el hook.**
  ⚠️ La ventana lleva **`WS_EX_NOACTIVATE | WS_EX_TOOLWINDOW`**: si robara el
  foco, la app activa pasaría a ser este proceso y `app_en_foco()` devolvería
  `python.exe`, rompiendo el zoom por aplicación; además saldría en el Alt+Tab
  del Botón 1. Si falta tkinter o la imagen no carga, `guia_mostrar()` cae al
  visor del sistema (`os.startfile`) y se avisa por consola.
- **Reiniciar desde la bandeja (`relanzar()`):** el orden es **cerrar primero**
  (icono, hooks, modificadores colgados) y **lanzar la instancia nueva después**.
  Si se solapan, ambas instalan hooks y gana la que Windows tenga primera en la
  cadena — con la vieja ganando, los cambios recién hechos no se ven (pasó de
  verdad con dos instancias abiertas a la vez). Termina con `os._exit(0)` para
  no volver por el flujo normal de `main()`.

### Comunes a las tres implementaciones

- **Selector Alt+Tab persistente (botones 2/3):**
  - Windows: se listan **dos hotkeys explícitos** por botón — `F14::` (1ª
    pulsación, sin modificadores) y `!F14::` (pulsaciones con Alt sostenido por
    el selector) — más modo `{Blind}` + `SendMode("Event")`. Sin cubrir el caso
    `Alt` solo cuenta la 1ª pulsación (Alt queda pulsado y la tecla pasa a ser
    `Alt+Fxx`); sin `{Blind}` el selector se cierra/reabre en cada pulsación.
    **NO usar el comodín `*F14::`**: capturaría también `Shift+F14`, que es el
    tilt izquierdo, y abriría el selector por error (ver receta del tilt).
  - Win/Python y Linux: se mantiene Alt pulsado (`key_down(VK["MENU"])` /
    `KEY_LEFTALT`) y se suelta tras `ALTTAB_TIMEOUT` con un timer. No hay
    problema de comodines: la desambiguación tilt-vs-botón es explícita.
- **Hypershift:**
  - Windows (AHK): combinaciones personalizadas `F22 & WheelUp::` (F22/F23 como
    tecla prefijo).
  - Win/Python: `on_key()` mantiene `self.hyper1`/`hyper2`; `on_mouse()` actúa
    solo si alguno está activo y devuelve `1` para **suprimir** el scroll/clic
    normal. Sin hypershift no toca nada (deja pasar todo).
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
  - Win/Python: en `on_key()`, F13/F14 con `self.shift_held` se desvían a
    `tilt(side)`. El `or self.scroll_side == side` garantiza ver el soltado
    aunque Synapse libere el Shift antes que la F-key.
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
  - Win/Python: `_scroll_tick()` se reprograma con `threading.Timer` cada
    `TILT_SCROLL_INTERVAL` y manda `wheel(horizontal=True, ...)`
    (`MOUSEEVENTF_HWHEEL`). Mismo **stop doble** que el AHK: keyup event-driven +
    respaldo con `is_physically_down()`. Aquí `SendInput` no da el problema del
    AHK porque el hook y el envío están en hilos distintos y los eventos propios
    se filtran por `INJECTED_TAG`.
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
- **Generador de la guía (`generar_guia_atajos.py`):** sustituyó al antiguo
  `generar_guia_atajos.ps1` (solo Windows, una sola carpeta). Ahora es Python +
  Pillow, corre también en Linux y escribe **las tres copias** de la imagen de
  una pasada (lista `DESTINOS`). Los tamaños de fuente están en **puntos**, como
  en el original de PowerShell, y se convierten a píxeles a 96 ppp (`pt * 4/3`);
  si se cambian a píxeles directamente, la imagen deja de coincidir con la
  versión histórica. Busca *Segoe UI* y cae a Arial/DejaVu/Liberation si no está.
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

- **Windows / Python (recomendado):** `windows-python/autoarranque.ps1` crea un
  acceso directo en `shell:startup`
  (`%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\Naga V2 Macros.lnk`).
  No toca el registro ni pide administrador. Apunta a `wscript.exe` con el
  `.vbs` como argumento (así funciona aunque el `.vbs` no tenga asociación de
  archivos). Flags: `-Estado` consulta, `-Quitar` desactiva. **Guarda una ruta
  absoluta:** si se mueve el repo, hay que re-ejecutarlo.
- **Windows / AHK:** acceso directo del `.ahk` en esa misma carpeta. **No tener
  las dos versiones en autoarranque a la vez** (cada tecla se procesaría dos
  veces).
- **Linux:** servicio systemd **de usuario**, versionado en el repo como
  `linux/naga-macros.service` (instrucciones en `README.md`). Es de
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
