#Requires AutoHotkey v2.0
#SingleInstance Force
SendMode("Input")
SetWorkingDir(A_ScriptDir)

; ============================================================
;  MACROS para Razer Naga V2 Hyperspeed
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
; El * hace que se active aunque Alt ya este presionado por el script
*F14::NagaAltTab("atras")    ; retrocede en el selector (Alt+Shift+Tab)

; --- Boton 3 (tecla F15) ---------------------------------
*F15::NagaAltTab("adelante") ; avanza en el selector (Alt+Tab)

; --- Boton 4 (tecla F16) = LIBRE -------------------------
; Sin asignar. Para usarlo, quita los ; y pon tu accion dentro:
; F16::
; {
;     Send("tu macro aqui")
; }

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
F22 & WheelRight::TiltUnaVez("next", "{Media_Next}")
F22 & WheelLeft::TiltUnaVez("prev", "{Media_Prev}")

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
F23 & WheelLeft::TiltUnaVez("copy", "^c")
F23 & WheelRight::TiltUnaVez("paste", "^v")

; --- Boton 12 (tecla F24) --------------------------------
F24::
{
    ; Win+Tab (vista de tareas / escritorios)
    Send("#{Tab}")
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
