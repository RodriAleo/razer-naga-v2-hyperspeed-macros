# Activa o desactiva el arranque automatico de las macros al iniciar Windows.
#
# Crea (o borra) un acceso directo a NagaV2_Macros_Win.vbs en la carpeta de
# Inicio del usuario. NO requiere permisos de administrador ni toca el registro:
# es la misma carpeta que abre  Win+R -> shell:startup
#
#   Activar:     powershell -ExecutionPolicy Bypass -File autoarranque.ps1
#   Desactivar:  powershell -ExecutionPolicy Bypass -File autoarranque.ps1 -Quitar
#   Ver estado:  powershell -ExecutionPolicy Bypass -File autoarranque.ps1 -Estado
#
# Si mueves el repo de carpeta, vuelve a ejecutarlo: el acceso directo guarda
# una ruta absoluta.

param(
    [switch]$Quitar,
    [switch]$Estado
)

$ErrorActionPreference = 'Stop'

$carpeta = Split-Path -Parent $MyInvocation.MyCommand.Path
$destino = Join-Path $carpeta 'NagaV2_Macros_Win.vbs'
$inicio  = [Environment]::GetFolderPath('Startup')
$enlace  = Join-Path $inicio 'Naga V2 Macros.lnk'

if ($Estado) {
    if (Test-Path $enlace) {
        $sh = New-Object -ComObject WScript.Shell
        $apunta = $sh.CreateShortcut($enlace).Arguments
        Write-Output "ACTIVADO"
        Write-Output "  Acceso directo: $enlace"
        Write-Output "  Apunta a      : $apunta"
    } else {
        Write-Output "DESACTIVADO (no hay acceso directo en la carpeta de Inicio)"
    }
    return
}

if ($Quitar) {
    if (Test-Path $enlace) {
        Remove-Item $enlace -Force
        Write-Output "Autoarranque DESACTIVADO. Se borro: $enlace"
    } else {
        Write-Output "El autoarranque ya estaba desactivado (no habia acceso directo)."
    }
    return
}

# --- activar ---
if (-not (Test-Path $destino)) {
    Write-Error "No encuentro NagaV2_Macros_Win.vbs junto a este script ($destino)."
    exit 1
}

# Se apunta a wscript.exe con el .vbs como argumento: asi el acceso directo
# funciona aunque el .vbs no tenga asociacion de archivos.
$sh = New-Object -ComObject WScript.Shell
$lnk = $sh.CreateShortcut($enlace)
$lnk.TargetPath       = Join-Path $env:WINDIR 'System32\wscript.exe'
$lnk.Arguments        = '"' + $destino + '"'
$lnk.WorkingDirectory = $carpeta
$lnk.Description      = 'Macros Razer Naga V2 Hyperspeed'
$lnk.IconLocation     = Join-Path $env:WINDIR 'System32\shell32.dll,21'
$lnk.Save()

Write-Output "Autoarranque ACTIVADO."
Write-Output "  Acceso directo: $enlace"
Write-Output "  Ejecuta       : $destino"
Write-Output ""
Write-Output "Las macros arrancaran solas al iniciar sesion."
Write-Output "Para desactivarlo:  powershell -ExecutionPolicy Bypass -File autoarranque.ps1 -Quitar"
