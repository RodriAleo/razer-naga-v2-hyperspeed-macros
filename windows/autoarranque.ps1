# Activa o desactiva el arranque automatico de las macros al iniciar Windows.
#
# Crea (o borra) un acceso directo a las macros en la carpeta de Inicio del
# usuario. Apunta al lanzador .vbs (el script arranca al instante; el .exe
# onefile tarda unos segundos en descomprimirse) y solo si no esta, al .exe. NO requiere permisos de administrador ni toca el registro:
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
$exe     = Join-Path $carpeta 'NagaV2_Macros_Win.exe'
$ico     = Join-Path $carpeta 'NagaV2_Macros.ico'
$inicio  = [Environment]::GetFolderPath('Startup')
$enlace  = Join-Path $inicio 'Naga V2 Macros.lnk'

if ($Estado) {
    if (Test-Path $enlace) {
        $sh = New-Object -ComObject WScript.Shell
        $l = $sh.CreateShortcut($enlace)
        $apunta = ($l.TargetPath + ' ' + $l.Arguments).Trim()
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
$sh = New-Object -ComObject WScript.Shell
$lnk = $sh.CreateShortcut($enlace)
if (Test-Path $destino) {
    # Se apunta a wscript.exe con el .vbs como argumento: asi el acceso directo
    # funciona aunque el .vbs no tenga asociacion de archivos.
    $lnk.TargetPath = Join-Path $env:WINDIR 'System32\wscript.exe'
    $lnk.Arguments  = '"' + $destino + '"'
} elseif (Test-Path $exe) {
    $lnk.TargetPath = $exe
    $lnk.Arguments  = ''
    $destino        = $exe
} else {
    Write-Error "No encuentro ni NagaV2_Macros_Win.exe ni NagaV2_Macros_Win.vbs en $carpeta"
    exit 1
}
$lnk.WorkingDirectory = $carpeta
$lnk.Description      = 'Macros Razer Naga V2 Hyperspeed'
if (Test-Path $ico) { $lnk.IconLocation = "$ico,0" }
$lnk.Save()

Write-Output "Autoarranque ACTIVADO."
Write-Output "  Acceso directo: $enlace"
Write-Output "  Ejecuta       : $destino"
Write-Output ""
Write-Output "Las macros arrancaran solas al iniciar sesion."
Write-Output "Para desactivarlo:  powershell -ExecutionPolicy Bypass -File autoarranque.ps1 -Quitar"
