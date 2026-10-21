#!/usr/bin/env bash
# Instala las macros como aplicacion para el usuario actual (sin sudo):
#   - servicio systemd de usuario: arrancan solas al iniciar sesion
#   - icono + lanzador "Naga V2 Macros" en el menu de aplicaciones; al abrirlo
#     (re)arranca las macros, util si se cerraron o dejaron de responder
#
#   ./instalar.sh                          instalar o actualizar
#   ./instalar.sh --desinstalar
#   PYTHON=/ruta/a/python3 ./instalar.sh   elegir el interprete
#
# El interprete debe tener evdev (y pystray/Pillow para el icono de bandeja).
# Por defecto se reutiliza el del servicio ya instalado, o el python3 del PATH.
# Si mueves el repo, vuelve a ejecutarlo: el servicio y el lanzador guardan
# rutas absolutas.

set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP=naga-macros
UNIT_DIR="$HOME/.config/systemd/user"
UNIT="$UNIT_DIR/$APP.service"
DATA="${XDG_DATA_HOME:-$HOME/.local/share}"
ICON_DIR="$DATA/icons/hicolor/256x256/apps"
DESKTOP="$DATA/applications/$APP.desktop"

refrescar_menus() {
    update-desktop-database "$DATA/applications" 2>/dev/null || true
    gtk-update-icon-cache -q -t "$DATA/icons/hicolor" 2>/dev/null || true
}

if [[ "${1:-}" == "--desinstalar" ]]; then
    systemctl --user disable --now "$APP.service" 2>/dev/null || true
    rm -f "$UNIT" "$DESKTOP" "$ICON_DIR/$APP.png"
    systemctl --user daemon-reload
    refrescar_menus
    echo "Desinstalado (servicio, lanzador e icono)."
    exit 0
fi

# --- interprete: $PYTHON > el del servicio ya instalado > python3 del PATH ---
py="${PYTHON:-}"
if [[ -z "$py" && -f "$UNIT" ]]; then
    py="$(sed -n 's/^ExecStart="\{0,1\}\([^" ]*\).*/\1/p' "$UNIT" | head -n1)"
fi
py="${py:-$(command -v python3 || true)}"
if [[ -z "$py" ]] || ! "$py" -c 'import evdev' 2>/dev/null; then
    echo "ERROR: '${py:-python3}' no tiene el modulo evdev." >&2
    echo "Instalalo (pip install evdev) o indica el interprete:" >&2
    echo "  PYTHON=/ruta/a/python3 $0" >&2
    exit 1
fi
"$py" -c 'import pystray, PIL' 2>/dev/null ||
    echo "Aviso: sin pystray/Pillow no habra icono en la bandeja (pip install pystray pillow)."
"$py" -c 'import tkinter' 2>/dev/null ||
    echo "Aviso: sin tkinter el Boton 5 abrira la guia en el visor (sudo apt install python3-tk)."
"$py" -c 'import PIL; from PIL import ImageTk' 2>/dev/null ||
    echo "Aviso: sin PIL.ImageTk la guia del Boton 5 se escala peor (sudo apt install python3-pil.imagetk)."
if [[ ! -w /dev/uinput ]]; then
    echo "Aviso: sin permiso de escritura en /dev/uinput el servicio no podra inyectar"
    echo "       teclas. Mira la seccion 'Ejecutar sin sudo' del README."
fi

# --- 1) servicio (copia de la plantilla del repo con las rutas reales) ---
mkdir -p "$UNIT_DIR"
sed "s|^ExecStart=.*|ExecStart=\"$py\" \"$DIR/naga_macros.py\"|" \
    "$DIR/$APP.service" > "$UNIT"
systemctl --user daemon-reload
systemctl --user enable "$APP.service" >/dev/null 2>&1
systemctl --user restart "$APP.service"

# --- 2) icono ---
mkdir -p "$ICON_DIR"
cp "$DIR/NagaV2_Macros.png" "$ICON_DIR/$APP.png"

# --- 3) lanzador del menu de aplicaciones ---
chmod +x "$DIR/lanzar.sh"
mkdir -p "$(dirname "$DESKTOP")"
cat > "$DESKTOP" <<EOF
[Desktop Entry]
Type=Application
Name=Naga V2 Macros
Comment=Macros del Razer Naga V2 Hyperspeed. Abrir = (re)iniciar las macros
Exec="$DIR/lanzar.sh"
Icon=$APP
Terminal=false
Categories=Utility;
Keywords=razer;naga;raton;mouse;macros;
StartupNotify=false
Actions=guia;detener;

[Desktop Action guia]
Name=Ver la guia de atajos
Exec=xdg-open "$DIR/NagaV2_atajos.png"

[Desktop Action detener]
Name=Detener las macros
Exec=systemctl --user stop $APP.service
EOF
refrescar_menus

sleep 2
if systemctl --user is-active --quiet "$APP.service"; then
    estado="en marcha"
else
    estado="NO arranco (mira: journalctl --user -u $APP -e)"
fi
echo "Instalado."
echo "  Servicio : $UNIT  ->  $estado"
echo "  Lanzador : busca 'Naga V2 Macros' en el menu de aplicaciones"
echo "  Interprete: $py"
