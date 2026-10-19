#!/usr/bin/env bash
# Lo ejecuta el lanzador "Naga V2 Macros" del menu de aplicaciones (lo instala
# instalar.sh): (re)arranca el servicio y avisa con una notificacion. Reiniciar
# en vez de solo arrancar es a proposito: si las macros se colgaron, abrir la
# app las recupera.

APP=naga-macros

aviso() {
    command -v notify-send >/dev/null &&
        notify-send -a "Naga V2 Macros" -i "$APP" "Naga V2 Macros" "$1"
}

if systemctl --user restart "$APP.service"; then
    sleep 2
    if systemctl --user is-active --quiet "$APP.service"; then
        aviso "Macros iniciadas."
        exit 0
    fi
fi
aviso "No se pudieron iniciar las macros. Revisa: journalctl --user -u $APP -e"
exit 1
