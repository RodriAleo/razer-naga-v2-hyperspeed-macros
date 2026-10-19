# Instala las macros como aplicacion: accesos directos con su icono en el menu
# Inicio y en el escritorio, y arranque automatico al iniciar sesion.
# NO requiere administrador ni toca el registro.
#
#   Instalar:     doble clic en instalar.bat
#                 (o: powershell -ExecutionPolicy Bypass -File instalar.ps1)
#   Opciones:     -SinEscritorio     no crear el acceso del escritorio
#                 -SinAutoarranque   no arrancar al iniciar sesion
#   Desinstalar:  powershell -ExecutionPolicy Bypass -File instalar.ps1 -Desinstalar
#
# Los accesos del menu Inicio y del escritorio apuntan al .exe si existe
# (compilar_exe.ps1) y si no al lanzador .vbs; el de inicio de sesion lo crea
# autoarranque.ps1 (prefiere el .vbs, que arranca al instante). Si compilas el
# .exe despues, o mueves el repo, vuelve a ejecutarlo: los accesos directos
# guardan una ruta absoluta.
#
# Si las macros dejan de responder, abrir la app desde cualquier acceso ofrece
# reiniciarlas (la instancia unica detecta la anterior).

param(
    [switch]$Desinstalar,
    [switch]$SinEscritorio,
    [switch]$SinAutoarranque
)

$ErrorActionPreference = 'Stop'

$carpeta = Split-Path -Parent $MyInvocation.MyCommand.Path
$exe = Join-Path $carpeta 'NagaV2_Macros_Win.exe'
$vbs = Join-Path $carpeta 'NagaV2_Macros_Win.vbs'
$ico = Join-Path $carpeta 'NagaV2_Macros.ico'
$autoarranque = Join-Path $carpeta 'autoarranque.ps1'

$nombre     = 'Naga V2 Macros.lnk'
$menu       = Join-Path ([Environment]::GetFolderPath('Programs')) $nombre
$escritorio = Join-Path ([Environment]::GetFolderPath('Desktop')) $nombre

if ($Desinstalar) {
    foreach ($l in @($menu, $escritorio)) {
        if (Test-Path $l) { Remove-Item $l -Force; Write-Output "Borrado: $l" }
    }
    & $autoarranque -Quitar
    Write-Output ""
    Write-Output "Desinstalado. Si las macros siguen abiertas, cierralas con 'Salir'"
    Write-Output "en el menu del icono de la bandeja."
    return
}

function Nuevo-Acceso([string]$ruta) {
    $sh  = New-Object -ComObject WScript.Shell
    $lnk = $sh.CreateShortcut($ruta)
    if (Test-Path $exe) {
        $lnk.TargetPath = $exe
        $lnk.Arguments  = ''
    } else {
        # wscript.exe + .vbs como argumento: funciona aunque el .vbs no tenga
        # asociacion de archivos.
        $lnk.TargetPath = Join-Path $env:WINDIR 'System32\wscript.exe'
        $lnk.Arguments  = '"' + $vbs + '"'
    }
    $lnk.WorkingDirectory = $carpeta
    $lnk.Description      = 'Macros Razer Naga V2 Hyperspeed'
    if (Test-Path $ico) { $lnk.IconLocation = "$ico,0" }
    $lnk.Save()
    Write-Output "  $ruta"
}

if (-not (Test-Path $exe) -and -not (Test-Path $vbs)) {
    Write-Error "No encuentro ni NagaV2_Macros_Win.exe ni NagaV2_Macros_Win.vbs en $carpeta"
    exit 1
}

Write-Output "Accesos directos creados:"
Nuevo-Acceso $menu
if (-not $SinEscritorio) { Nuevo-Acceso $escritorio }
Write-Output ""
if ($SinAutoarranque) {
    & $autoarranque -Quitar
} else {
    & $autoarranque
}

Write-Output ""
if (Test-Path $exe) {
    Write-Output "Los accesos abren: $exe"
} else {
    Write-Output "Los accesos abren el lanzador .vbs (necesita Python instalado)."
    Write-Output "Para usar el .exe: compilar_exe.ps1 y vuelve a ejecutar este instalador."
}
Write-Output "Busca 'Naga V2 Macros' en el menu Inicio para abrirlas cuando quieras."
