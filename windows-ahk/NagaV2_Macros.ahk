#Requires AutoHotkey v2.0
#SingleInstance Force
SendMode("Input")
SetWorkingDir(A_ScriptDir)

; Version FIJA: este script esta DEPRECADO y congelado en la v1.1.0. No lee el
; CHANGELOG.md a proposito, para no mostrar versiones posteriores que no tiene.
NAGA_VERSION := "1.1.0 (deprecada)"
A_IconTip := "Naga V2 Macros v" NAGA_VERSION
; Primera linea del menu de la bandeja: solo informativa (deshabilitada).
A_TrayMenu.Insert("1&", "Naga V2 Macros v" NAGA_VERSION, (*) => 0)
A_TrayMenu.Disable("1&")
A_TrayMenu.Insert("2&")    ; separador

; ============================================================
;  MACROS para Razer Naga V2 Hyperspeed
;
;  ⛔ DEPRECADO desde la v1.1.0 -- NO SE MANTIENE. ⛔
;  En Windows se usa solo la version Python (windows-python/naga_macros_win.py).
;  Este archivo se conserva como referencia historica, congelado tal como
;  quedo en la v1.1.0: no anadir macros ni arreglos aqui.
;
;  Los 12 botones laterales estan configurados (en Razer Synapse)
;  para enviar las teclas F13 a F24.
;
;  Este script "captura" esas teclas y ejecuta la macro que tu
;  quieras en su lugar.
;
;  COMO USARLO:
;   1. Instala AutoHotkey v2:  https://www.autohotkey.com/
;   2. Haz doble clic en este archivo para ejecutarlo.
;   3. Veras un icono verde "H" en la bandeja del sistema.
;   4. Pulsa los botones del raton para probar las macros.
;
;  COMO EDITAR:
;   - Cada bloque de abajo (F13::  hasta  F24:: ) es un boton.
;   - Cambia el contenido por lo que quieras que haga.
;   - Guarda el archivo y haz clic derecho en el icono de la
;     bandeja -> "Reload Script" para aplicar los cambios.
;
;  SINTAXIS UTIL (referencia rapida):
;   Send("texto")              -> escribe texto
;   Send("^c")                 -> Ctrl+C   (^ = Ctrl, ! = Alt, + = Shift, # = Win)
;   Send("{Enter}")            -> pulsa Enter
;   Run("notepad.exe")         -> abre un programa
;   Run("https://google.com")  -> abre una web
;   MsgBox("hola")             -> muestra un mensaje
;   Sleep(500)                 -> espera 500 ms
; ============================================================
;
;  DISPOSICION DE TECLAS (segun Razer Synapse)
;  Numero de boton  ->  Tecla asignada
;
;     Columna izquierda          Columna derecha
;     -----------------          ---------------
;       Boton 1  = F13             Boton 7  = F19
;       Boton 2  = F14             Boton 8  = F20
;       Boton 3  = F15             Boton 9  = F21
;       Boton 4  = F16             Boton 10 = F22
;       Boton 5  = F17             Boton 11 = F23
;       Boton 6  = F18             Boton 12 = F24
;
;  Vista del teclado lateral (12 botones fisicos del raton):
;
;        [ 1 ] [ 2 ] [ 3 ]
;        [ 4 ] [ 5 ] [ 6 ]
;        [ 7 ] [ 8 ] [ 9 ]
;        [10 ] [11 ] [12 ]
; ============================================================


; --- Boton 1 (tecla F13) ---------------------------------
F13::
{
    ; Alt+Tab (cambiar de ventana)
    Send("!{Tab}")
}

; --- Boton 2 (tecla F14) ---------------------------------
; Dos casos EXPLICITOS (no usar '*'): primera pulsacion sin modificadores, y
; pulsaciones con Alt sostenido por el selector abierto. El '*' capturaria
; tambien Shift+F14, que es el tilt izquierdo, y abriria el selector por error.
F14::NagaAltTab("atras")     ; primera pulsacion (Alt+Shift+Tab)
!F14::NagaAltTab("atras")    ; con el selector ya abierto (Alt sostenido)

; --- Boton 3 (tecla F15) ---------------------------------
F15::NagaAltTab("adelante")  ; primera pulsacion (Alt+Tab)
!F15::NagaAltTab("adelante") ; con el selector ya abierto (Alt sostenido)

; --- Boton 4 (tecla F16) ---------------------------------
F16::
{
    ; Ctrl+Tab (siguiente pestaña)
    Send("^{Tab}")
}

; --- Boton 5 (tecla F17) ---------------------------------
F17::
{
    ; Abrir la guia de atajos (ayuda a memoria)
    Run(A_ScriptDir . "\NagaV2_atajos.png")
}

; --- Boton 6 (tecla F18) = LIBRE -------------------------
; Sin asignar. Para usarlo, quita los ; y pon tu accion dentro:
; F18::
; {
;     Send("tu macro aqui")
; }

; --- Boton 7 (tecla F19) ---------------------------------
F19::
{
    ; Pulsar F11 (pantalla completa)
    Send("{F11}")
}

; --- Boton 8 (tecla F20) = LIBRE -------------------------
; Sin asignar. Para usarlo, quita los ; y pon tu accion dentro:
; F20::
; {
;     Send("tu macro aqui")
; }

; --- Boton 9 (tecla F21) = LIBRE -------------------------
; Sin asignar. Para usarlo, quita los ; y pon tu accion dentro:
; F21::
; {
;     Send("tu macro aqui")
; }

; --- Boton 10 (tecla F22) = HYPERSHIFT -------------------
; Manten pulsado el Boton 10 y combinalo con la rueda:
;   Boton 10 + rueda arriba   -> sube volumen
;   Boton 10 + rueda abajo    -> baja volumen
;   Boton 10 + clic de rueda  -> play/pausa multimedia
;   Boton 10 + tilt derecha   -> pista siguiente
;   Boton 10 + tilt izquierda -> pista anterior
; Al soltar el Boton 10, la rueda vuelve a funcionar normal.
F22 & WheelUp::Send("{Volume_Up 2}")
F22 & WheelDown::Send("{Volume_Down 2}")
F22 & MButton::Send("{Media_Play_Pause}")
; El tilt (pista sig/ant) ya NO llega como rueda: Synapse lo manda como
; Shift+F13 (derecha) / Shift+F14 (izquierda). Ver mas abajo, bloque
; "TILT LATERAL", donde se traduce segun el hypershift activo.

; --- Boton 11 (tecla F23) = HYPERSHIFT (ZOOM) ------------
; Manten pulsado el Boton 11 y combinalo con la rueda:
;   Boton 11 + rueda arriba   -> acercar zoom  (Ctrl +)
;   Boton 11 + rueda abajo    -> alejar zoom   (Ctrl -)
;   Boton 11 + clic de rueda  -> Ctrl+Q  (abrir software de capturas)
;   Boton 11 + clic derecho   -> portapapeles (Win+V)
;   Boton 11 + tilt izquierda -> copiar  (Ctrl+C)
;   Boton 11 + tilt derecha   -> pegar   (Ctrl+V)
; Usa los atajos de teclado Ctrl + / Ctrl -, mas fiables en
; navegadores y editores que el gesto Ctrl+rueda.
F23 & WheelUp::Send("^{+}")
F23 & WheelDown::Send("^-")
F23 & MButton::Send("^q")
F23 & RButton::Send("#v")
; El tilt (copiar/pegar) tampoco llega como rueda: ver bloque "TILT LATERAL".

; --- Boton 12 (tecla F24) --------------------------------
F24::
{
    ; Win+Tab (vista de tareas / escritorios)
    Send("#{Tab}")
}


; ============================================================
;  TILT LATERAL  (rueda inclinada izquierda / derecha)
;
;  El firmware del Naga reporta el tilt como un scroll de rueda,
;  que en Linux NO se distingue del scroll normal. Para arreglarlo,
;  el tilt se reasigna en Razer Synapse a un combo de teclado:
;     Tilt derecha   -> Shift+F13
;     Tilt izquierda -> Shift+F14
;  IMPORTANTE: el combo NO lleva Ctrl. Con Ctrl la rueda se interpreta como
;  Ctrl+rueda = zoom (imposible de evitar de forma fiable si Synapse mantiene
;  Ctrl pulsado). El Shift solo sirve para distinguir el tilt del boton (F13/F14
;  pelados = botones 1/2); NO se usa para el scroll: se manda rueda horizontal
;  nativa (WheelRight/Left), que no depende de ningun modificador.
;  Aqui se traduce ese combo al gesto original segun el hypershift:
;     Sin hypershift -> desplazamiento lateral continuo (mientras manten)
;     HYPERSHIFT 1   -> pista siguiente / anterior
;     HYPERSHIFT 2   -> pegar / copiar
;  Velocidad del scroll lateral (ms entre pasos; mayor = mas lento):
global SCROLL_INTERVALO := 60
global scrollLado := ""           ; "" inactivo | "der" | "izq" (scroll en curso)

+F13::TiltLateral("der")
+F14::TiltLateral("izq")

; El combo deja Shift pulsado; sus auto-repeticiones de la F-key se ignoran
; mientras el scroll de ese lado esta activo, para que no disparen los botones
; 1 (Alt+Tab) y 2 (selector).
#HotIf (scrollLado = "der")
*F13::return                 ; ignora auto-repeticiones (no dispara boton 1)
*F13 up::DetenerScroll()     ; soltar el tilt frena el scroll (event-driven)
#HotIf (scrollLado = "izq")
*F14::return                 ; ignora auto-repeticiones (no dispara boton 2)
*F14 up::DetenerScroll()     ; soltar el tilt frena el scroll (event-driven)
#HotIf

TiltLateral(lado)
{
    global SCROLL_INTERVALO, scrollLado

    ; HYPERSHIFT 1 (Boton 10 mantenido) -> pista siguiente / anterior
    if (GetKeyState("F22", "P"))
    {
        if (lado = "der")
            TiltUnaVez("next", "{Media_Next}")
        else
            TiltUnaVez("prev", "{Media_Prev}")
        return
    }
    ; HYPERSHIFT 2 (Boton 11 mantenido) -> pegar / copiar
    if (GetKeyState("F23", "P"))
    {
        if (lado = "der")
            TiltUnaVez("paste", "^v")
        else
            TiltUnaVez("copy", "^c")
        return
    }

    ; Sin hypershift -> desplazamiento lateral continuo mientras se mantiene.
    ; Un timer AUTO-VERIFICADO hace el scroll y se detiene solo al soltar el
    ; tilt (mira el estado fisico de la tecla). Antes se usaba KeyWait, que a
    ; veces no veia el soltado y dejaba el scroll disparado ("trabado").
    if (scrollLado != "")            ; ya hay un scroll en curso -> no reiniciar
        return
    scrollLado := lado
    SetTimer(ScrollTick, SCROLL_INTERVALO)
    ScrollTick()                     ; primer paso inmediato
}

DetenerScroll()
{
    global scrollLado
    SetTimer(ScrollTick, 0)
    scrollLado := ""
}

ScrollTick()
{
    global scrollLado
    tecla := (scrollLado = "der") ? "F13" : "F14"
    ; respaldo del stop: si el tilt ya no esta fisicamente pulsado, frena
    ; (por si el evento de soltado *Fxx up no llegara por algun motivo)
    if (scrollLado = "" || !GetKeyState(tecla, "P"))
    {
        DetenerScroll()
        return
    }
    ; SendEvent (NO Send/SendInput): SendInput congela el hook mientras envia y
    ; a veces se comia el soltado del tilt, dejando el scroll trabado. SendEvent
    ; no bloquea el hook, asi GetKeyState ve el soltado y el timer se detiene.
    ; Rueda HORIZONTAL nativa (WheelRight/Left): scroll lateral directo, SIN
    ; depender de Shift (Synapse lo suelta enseguida, no lo mantiene pulsado).
    ; Sin Ctrl en el binding no hay zoom.
    ;   der -> WheelRight ; izq -> WheelLeft (si queda invertido, intercambialos)
    rueda := (scrollLado = "der") ? "{WheelRight}" : "{WheelLeft}"
    SendEvent(rueda)
}


; ============================================================
;  SELECTOR Alt+Tab PERSISTENTE  (Botones 2 y 3)
;
;  Boton 3 (F15) -> avanza entre ventanas
;  Boton 2 (F14) -> retrocede entre ventanas
;
;  El selector se queda ABIERTO mientras sigas pulsando.
;  Se cierra solo (confirmando la ventana elegida) tras
;  1.5 segundos sin pulsar ningun boton.
;  Cambia el 1500 de abajo para ajustar ese tiempo (en ms).
; ============================================================

global altTabAbierto := false

NagaAltTab(direccion)
{
    global altTabAbierto

    ; Modo "Event": imprescindible para que el selector Alt+Tab
    ; acepte varias pulsaciones de Tab seguidas.
    SendMode("Event")
    SetKeyDelay(60, 30)

    ; La primera pulsacion abre el selector manteniendo Alt pulsado
    if (!altTabAbierto)
    {
        SendEvent("{Blind}{Alt down}")
        altTabAbierto := true
        Sleep(40)   ; deja que aparezca el selector
    }

    ; {Blind} = NO sueltes Alt; manten el selector abierto entre pulsaciones
    if (direccion = "atras")
        SendEvent("{Blind}+{Tab}")   ; Alt+Shift+Tab -> retrocede
    else
        SendEvent("{Blind}{Tab}")    ; Alt+Tab        -> avanza

    ; Reinicia la cuenta atras para cerrar el selector
    SetTimer(CerrarAltTab, -800)
}

CerrarAltTab()
{
    global altTabAbierto
    if (altTabAbierto)
    {
        SendEvent("{Blind}{Alt up}")   ; suelta Alt -> confirma la ventana seleccionada
        altTabAbierto := false
    }
}


; ============================================================
;  ANTI-REPETICION PARA EL TILT (copiar, pegar, pista sig/ant)
;
;  Al mantener el tilt, Windows envia muchos eventos seguidos.
;  Esta funcion ejecuta la accion UNA SOLA VEZ y la ignora
;  mientras sigas manteniendo el tilt. Al soltar y volver a
;  inclinar (pasados >400 ms) se vuelve a ejecutar.
;  Cambia el 400 para ajustar la sensibilidad (en ms).
; ============================================================

global ultimoTilt := Map()

TiltUnaVez(nombre, accion)
{
    global ultimoTilt
    ahora := A_TickCount
    yaSono := ultimoTilt.Has(nombre) && (ahora - ultimoTilt[nombre]) < 400
    ultimoTilt[nombre] := ahora   ; refresca el tiempo en cada evento
    if (yaSono)
        return                    ; sigues manteniendo el tilt -> no repite
    Send(accion)
}
