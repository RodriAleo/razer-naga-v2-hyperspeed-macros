# Razer Naga V2 Hyperspeed — Macros (Windows + Linux)

Macros para los **12 botones laterales** del ratón Razer Naga V2 Hyperspeed,
con dos modos **Hypershift**, un selector **Alt+Tab persistente** y soporte
para el **tilt** de la rueda.

El mismo conjunto de atajos está implementado en tres versiones equivalentes,
cada una en su carpeta:

| Sistema | Carpeta | Tecnología |
|---------|---------|------------|
| **Windows** (recomendada) | [`windows-python/`](windows-python/) | Python + `ctypes` — **sin AutoHotkey** |
| **Windows** (original) | [`windows-ahk/`](windows-ahk/) | AutoHotkey v2 |
| **Linux** (Wayland/X11) | [`linux/`](linux/) | Python + `evdev`/`uinput` |

```
├── windows-python/          ← versión recomendada para Windows
│   ├── naga_macros_win.py       el demonio de macros
│   ├── NagaV2_Macros_Win.vbs    lanzador (doble clic, sin consola)
│   ├── autoarranque.ps1         activa/desactiva el inicio con Windows
│   └── NagaV2_atajos.png        guía de atajos (la abre el Botón 5)
├── windows-ahk/
│   ├── NagaV2_Macros.ahk
│   └── NagaV2_atajos.png
├── linux/
│   ├── naga_macros.py
│   ├── naga-macros.service      unidad systemd (autoarranque)
│   └── NagaV2_atajos.png
└── generar_guia_atajos.py   ← regenera la imagen en las 3 carpetas
```

> La imagen está repetida a propósito en cada carpeta: el **Botón 5** la abre
> con una ruta relativa al script, así cada versión es autocontenida.

> **¿Por qué dos versiones para Windows?** Algunos **anticheat** de juegos no
> arrancan si detectan AutoHotkey, obligando a cerrarlo y reabrirlo cada vez.
> La versión en Python es un proceso normal y hace exactamente lo mismo, así que
> no hace falta estar activando y desactivando nada. El `.ahk` se mantiene para
> quien lo prefiera; **usa una sola de las dos a la vez** (si no, cada tecla se
> procesaría dos veces).

---

## Cómo está montado el ratón

Los 12 botones laterales **no** ejecutan las macros por sí mismos: en
**Razer Synapse** se configuraron para enviar las teclas **F13 → F24**, y
estos scripts "capturan" esas teclas y ejecutan la acción correspondiente.

> La asignación F13–F24 conviene **guardarla en la memoria interna del ratón**
> (perfil *onboard*). Así también funciona en Linux, donde Synapse no existe.

Correspondencia botón → tecla:

| Botón | Tecla | | Botón | Tecla |
|:----:|:----:|:--:|:----:|:----:|
| 1 | F13 | | 7  | F19 |
| 2 | F14 | | 8  | F20 |
| 3 | F15 | | 9  | F21 |
| 4 | F16 | | 10 | F22 |
| 5 | F17 | | 11 | F23 |
| 6 | F18 | | 12 | F24 |

---

## Mapa de atajos

![Atajos del Razer Naga V2 Hyperspeed](NagaV2_atajos.png)

### Botones simples

| Botón | Acción |
|:----:|--------|
| **1** | Alt+Tab rápido (un toque) |
| **2** | Selector Alt+Tab persistente — ventana **anterior** |
| **3** | Selector Alt+Tab persistente — ventana **siguiente** |
| **4** | *(libre)* |
| **5** | Abrir esta guía de atajos (imagen) |
| **6** | *(libre)* |
| **7** | Pantalla completa (`F11`) |
| **8** | *(libre)* |
| **9** | *(libre)* |
| **12** | Vista de tareas — `Win+Tab` (Windows) / Actividades-Super (Linux) |

### Hypershift 1 — Botón 10 (mantener pulsado)

| Combinación | Acción |
|-------------|--------|
| Rueda arriba / abajo | Subir / bajar volumen |
| Clic de rueda | Play / Pausa multimedia |
| Tilt derecha / izquierda | Pista siguiente / anterior |

### Hypershift 2 — Botón 11 (mantener pulsado)

| Combinación | Acción |
|-------------|--------|
| Rueda arriba / abajo | Acercar / alejar zoom (`Ctrl +` / `Ctrl -`) |
| Clic de rueda | `Ctrl+Q` (abrir software de capturas) |
| Clic derecho | Portapapeles (`Win+V` en Windows) |
| Tilt izquierda / derecha | Copiar / Pegar (`Ctrl+C` / `Ctrl+V`) |

### Tilt de la rueda — sin hypershift

| Combinación | Acción |
|-------------|--------|
| Tilt izquierda / derecha | Desplazamiento lateral continuo (scroll horizontal) mientras se mantiene |

> **Importante — configuración del tilt en Razer Synapse.** El firmware reporta
> el tilt como un evento de rueda que en Linux **no se distingue** del scroll
> normal. Por eso el tilt se reasigna en Synapse a una combinación de teclado, y
> los scripts la traducen al gesto original:
>
> | Gesto físico | Tecla a asignar en Synapse |
> |--------------|----------------------------|
> | Tilt derecha | `Shift + F13` |
> | Tilt izquierda | `Shift + F14` |
>
> **No agregues `Ctrl` al combo:** en Windows `Ctrl`+rueda = zoom y no se puede
> evitar de forma fiable si Synapse mantiene `Ctrl` pulsado durante el tilt. Con
> solo `Shift` no hay zoom; el `Shift` sirve únicamente para distinguir el tilt
> del botón (los scripts mandan rueda horizontal nativa, que no depende de
> modificadores). En Linux da igual (los modificadores se capturan), pero se usa
> `Shift` en las tres versiones para tener un único binding.
>
> Con esto el tilt funciona **igual en Windows y Linux** (antes el tilt derecho
> se perdía en Linux). La velocidad del scroll lateral se ajusta con
> `SCROLL_INTERVALO` (AHK) y `TILT_SCROLL_INTERVAL` (ambos Python).

---

## Windows — versión Python (recomendada, sin AutoHotkey)

Pensada para no tener que cerrar nada al jugar: es un proceso Python normal,
así que los anticheat que bloquean AutoHotkey no la afectan.

### Requisitos
- **Python 3.8+** ([python.org](https://www.python.org/downloads/) — marca
  *"Add Python to PATH"* al instalar).
- Nada más: el núcleo usa solo `ctypes` (incluido en Python).
- *Opcional*, para el icono en la bandeja del sistema:
  ```bash
  pip install pystray pillow
  ```

### Uso
Doble clic en **`windows-python/NagaV2_Macros_Win.vbs`** (arranca sin ventana
de consola).

Si instalaste `pystray`, aparece un icono verde en la bandeja con el menú
*Abrir guía de atajos* / *Salir*. Sin él funciona igual, pero para cerrarlo
tendrás que finalizar `pythonw.exe` en el Administrador de tareas.

Para ver los mensajes (diagnóstico), ejecútalo desde una terminal:

```bash
python windows-python/naga_macros_win.py
```

### Arranque automático con Windows

Desde la carpeta `windows-python/`:

```bash
powershell -ExecutionPolicy Bypass -File autoarranque.ps1
```

Eso crea un acceso directo en la carpeta de Inicio del usuario
(`shell:startup`); las macros arrancarán solas al iniciar sesión. No requiere
permisos de administrador ni toca el registro.

| Acción | Comando |
|--------|---------|
| Activar | `powershell -ExecutionPolicy Bypass -File autoarranque.ps1` |
| Desactivar | `powershell -ExecutionPolicy Bypass -File autoarranque.ps1 -Quitar` |
| Ver estado | `powershell -ExecutionPolicy Bypass -File autoarranque.ps1 -Estado` |

> Si **mueves el repo** de carpeta, vuelve a ejecutar el script: el acceso
> directo guarda una ruta absoluta.

También puedes hacerlo a mano: `Win + R` → `shell:startup` → y copiar ahí un
acceso directo de `NagaV2_Macros_Win.vbs`.

### Ajustes
Edita las constantes al principio de `naga_macros_win.py`:
`ALTTAB_TIMEOUT`, `TILT_DEBOUNCE`, `WHEEL_STEPS`, `ZOOM_STEPS`,
`TILT_SCROLL_INTERVAL` / `TILT_SCROLL_STEPS` (velocidad del scroll lateral).

---

## Windows — versión AutoHotkey (original)

### Requisitos
- [AutoHotkey **v2**](https://www.autohotkey.com/) (¡v2, no v1!).

### Uso
1. Doble clic en `windows-ahk/NagaV2_Macros.ahk`.
2. Aparece un icono verde **"H"** en la bandeja del sistema.
3. Tras editar el script: clic derecho en el icono → **Reload Script**.

### Arranque automático con Windows
Crea un acceso directo del `.ahk` en la carpeta de Inicio:

1. `Win + R` → escribe `shell:startup` → Enter.
2. Copia ahí un acceso directo de `NagaV2_Macros.ahk`.

A partir de entonces el script se lanza solo al iniciar sesión.
Para desactivarlo: borra el acceso directo de esa carpeta (o desde
**Administrador de tareas → Inicio**).

> ⚠️ **No ejecutes las dos versiones de Windows a la vez**: ambas capturan las
> mismas teclas y cada pulsación se procesaría dos veces. Si activaste el
> autoarranque de una, desactiva el de la otra.

---

## Linux (Ubuntu — Wayland o X11)

AutoHotkey no existe en Linux, así que se usa un demonio en Python que lee el
ratón con `evdev` e inyecta las teclas con `uinput` (a nivel de kernel, por
eso funciona **igual en Wayland y X11**).

### Requisitos
```bash
sudo apt install python3-evdev      # o:  pip install evdev
pip install pystray pillow          # ícono en la bandeja del sistema (opcional)
```

Para que el ícono aparezca en GNOME Shell también necesitas la extensión
[AppIndicator and KStatusNotifierItem Support](https://extensions.gnome.org/extension/615/appindicator-support/).
Si no la tienes instalada el script funciona igualmente, solo que sin ícono.

> **Nota con `sudo`:** para que el ícono sea visible debes preservar las
> variables de sesión del usuario: `sudo -E python3 linux/naga_macros.py`.
> Alternativamente, sigue la sección *Ejecutar sin sudo* más abajo.

### Configuración
Edita las constantes al principio de `linux/naga_macros.py`:

- `IMAGE_PATH` → por defecto apunta a `NagaV2_atajos.png` junto al script (igual que en Windows). Solo cámbialo si la imagen está en otra ubicación.
- `DEVICE_NAME_CONTAINS` → texto del nombre del ratón (por defecto `"naga"`).
- `ALTTAB_TIMEOUT`, `TILT_DEBOUNCE`, `WHEEL_STEPS`, `ZOOM_STEPS` → ajustes finos.
- `TILT_SCROLL_INTERVAL` / `TILT_SCROLL_STEPS` → velocidad y paso del desplazamiento lateral continuo del tilt.

### Uso
```bash
sudo -E python3 linux/naga_macros.py
```
Al arrancar imprime los dispositivos detectados (el Naga debe aparecer, y la
interfaz de ratón marcada como `(capturado)`). Si `pystray` y `Pillow` están
instalados, aparece un ícono circular en la bandeja:
- **Verde** → ratón detectado y macros activos.
- **Naranja** → esperando que el ratón se conecte.

Clic derecho sobre el ícono para acceder al menú **Reiniciar** / **Salir**.

### Ejecutar sin `sudo`
1. Añade tu usuario al grupo `input` y reinicia sesión:
   ```bash
   sudo usermod -aG input $USER
   ```
2. Permite el acceso a `/dev/uinput` con una regla udev:
   ```bash
   echo 'KERNEL=="uinput", MODE="0660", GROUP="input", OPTIONS+="static_node=uinput"' \
     | sudo tee /etc/udev/rules.d/99-uinput.rules
   sudo udevadm control --reload-rules && sudo udevadm trigger
   ```

### Arranque automático (servicio systemd de usuario)
El repo incluye la unidad lista: **`linux/naga-macros.service`**.

```bash
cp linux/naga-macros.service ~/.config/systemd/user/
# edita ExecStart: pon tu intérprete y la ruta real del repo
systemctl --user daemon-reload
systemctl --user enable --now naga-macros.service
```

Con esto las macros arrancan solas **cada vez que inicias sesión**. Comprobar
estado y ver los mensajes en vivo:

```bash
systemctl --user status naga-macros.service
journalctl --user -u naga-macros -f
```

Detalles de la unidad que conviene no cambiar a la ligera:

| Ajuste | Por qué |
|--------|---------|
| `WantedBy=graphical-session.target` | El ícono de bandeja necesita que la sesión gráfica ya exista. Con `default.target` el servicio arranca antes y el ícono no aparece. |
| `Environment=PYTHONUNBUFFERED=1` | Sin esto Python bufferiza `stdout` (no hay tty) y los mensajes solo aparecen en el journal cuando el proceso muere. |
| `Restart=on-failure` | Salir desde el menú **Salir** de la bandeja termina con código 0 y debe quedarse cerrado. Con `Restart=always` systemd lo relanzaría y no podrías cerrarlo desde el ícono. |

> **`ExecStart` debe apuntar al intérprete que tenga `evdev`, `pystray` y
> `Pillow` instalados.** Si usas conda o un venv, pon la ruta de *ese* python
> (ej. `~/miniconda3/bin/python3`), no `/usr/bin/python3`.

> Como es un servicio de **usuario**, corre sin `sudo`: necesita que hayas hecho
> los dos pasos de *Ejecutar sin `sudo`* de arriba. Sin root no puede fijar la
> prioridad en tiempo real (`SCHED_FIFO`) y avisa por el log; es inofensivo,
> solo se pierde una pequeña optimización de latencia.

---

## Regenerar la guía de atajos

La imagen `NagaV2_atajos.png` (la que abre el **Botón 5**) se genera con
**`generar_guia_atajos.py`**, en la raíz del repo:

```bash
python generar_guia_atajos.py
```

Escribe la imagen en **las tres carpetas** de una sola pasada
(`windows-python/`, `windows-ahk/`, `linux/`), porque cada script la abre desde
su propio directorio.

Requiere Pillow (`pip install pillow`). Funciona en Windows y en Linux: si no
encuentra la fuente *Segoe UI* usa una alternativa del sistema.

Para cambiar el contenido, edita las listas `CELDAS` y `SECCIONES` al principio
del archivo y vuelve a ejecutarlo.

---

## Diferencias Windows ↔ Linux

| Atajo | Windows | Linux (notas) |
|-------|---------|---------------|
| Portapapeles (HS2 + clic derecho) | `Win+V` nativo | `Super+V` en GNOME 44+ abre notificaciones. Configurar `PORTAPAPELES_CMD` en `naga_macros.py` con tu gestor (ej. `["copyq", "toggle"]`) |
| Vista de tareas (Botón 12) | `Win+Tab` | Tecla **Super** (Actividades de GNOME) |
| `Ctrl+Q` (capturas) | Tu software de capturas | Asegúrate de que tu app de capturas en Linux use el mismo atajo |
| **Tilt** (izq/der) | Funciona | Funciona reasignando el tilt en Synapse a `Shift+F13` (derecha) / `Shift+F14` (izquierda) — ver la nota de la sección *Tilt de la rueda*. Sin esa reasignación el tilt derecho se pierde en Linux (el firmware lo reporta como scroll, indistinguible de girar la rueda). |

---

## Detalles técnicos

- **Selector Alt+Tab persistente (botones 2 y 3):** mantiene `Alt` pulsado
  entre pulsaciones y lo suelta tras un periodo de inactividad
  (`ALTTAB_TIMEOUT`, por defecto 0.8 s). En AHK se declaran **dos hotkeys por
  botón** (`F14::` y `!F14::`) más el modo `{Blind}`, para no cerrar el selector
  en cada pulsación. No se usa el comodín `*F14::` porque capturaría también
  `Shift+F14`, que es el tilt izquierdo.
- **Hypershift:** los botones 10 y 11 actúan como modificador mientras se
  mantienen pulsados; la rueda/tilt/clics cambian de función y el scroll
  normal se suprime.
- **Anti-repetición del tilt:** mantener el tilt genera muchos eventos
  seguidos; copiar, pegar y cambio de pista se ejecutan **una sola vez** por
  inclinación (`TILT_DEBOUNCE`, por defecto 0.4 s).
- **Scroll lateral en Linux — se emite en alta resolución:** el desplazamiento
  lateral del tilt manda `REL_HWHEEL_HI_RES` (120 unidades por muesca) **además**
  del `REL_HWHEEL` clásico. Es obligatorio: como el dispositivo virtual declara
  el eje de alta resolución, libinput usa solo ese y descarta los eventos
  clásicos, así que mandando únicamente `REL_HWHEEL` no se movía nada. Los
  ratones reales mandan los dos juntos igual que aquí, y no se duplica el
  scroll.

---

## Estructura del repo

```
.
├── NagaV2_Macros.ahk        # Windows (AutoHotkey v2)
├── naga_macros.py           # Linux (Python evdev/uinput)
├── naga-macros.service      # Linux: unidad systemd de usuario (autoarranque)
├── generar_guia_atajos.ps1  # Genera la imagen NagaV2_atajos.png
├── NagaV2_atajos.png        # Guía de atajos (la abre el Botón 5)
├── CLAUDE.md                # Contexto para mantener el repo
└── README.md
```
