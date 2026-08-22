# Compila naga_macros_win.py en un unico NagaV2_Macros_Win.exe.
#
#   powershell -ExecutionPolicy Bypass -File compilar_exe.ps1
#
# Requiere:  pip install pyinstaller pystray pillow
#
# El .exe NO se versiona (esta en .gitignore): es un artefacto que se regenera.
# Tras recompilar no hace falta rehacer los accesos directos: apuntan al mismo
# archivo.

$ErrorActionPreference = 'Stop'
$carpeta = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $carpeta

$png = Join-Path $carpeta 'NagaV2_atajos.png'
$ico = Join-Path $carpeta 'NagaV2_Macros.ico'
foreach ($f in @($png, $ico, (Join-Path $carpeta 'naga_macros_win.py'))) {
    if (-not (Test-Path $f)) { Write-Error "Falta $f"; exit 1 }
}

# Hay que cerrar el .exe si esta corriendo: si no, PyInstaller no puede
# sobrescribirlo.
Get-Process NagaV2_Macros_Win -ErrorAction SilentlyContinue | Stop-Process -Force
Start-Sleep -Milliseconds 500

# --onefile   : un solo archivo, comodo de mover y de anclar al menu de Inicio
# --noconsole : sin ventana de consola (equivale a pythonw)
# --add-data  : la guia de atajos viaja DENTRO del exe, para que el Boton 5
#               funcione aunque el .exe se mueva solo a otra carpeta
python -m PyInstaller --noconfirm --clean --onefile --noconsole `
    --name "NagaV2_Macros_Win" `
    --icon "$ico" `
    --add-data "$png;." `
    --distpath $carpeta `
    --workpath (Join-Path $env:TEMP 'naga_build') `
    --specpath (Join-Path $env:TEMP 'naga_build') `
    naga_macros_win.py

$exe = Join-Path $carpeta 'NagaV2_Macros_Win.exe'
if (Test-Path $exe) {
    $mb = [math]::Round((Get-Item $exe).Length / 1MB, 1)
    Write-Output ""
    Write-Output "Listo: $exe  ($mb MB)"
    Write-Output "Ojo: en modo onefile el primer arranque tarda unos segundos"
    Write-Output "(se descomprime en una carpeta temporal)."
} else {
    Write-Error "La compilacion no genero el .exe"
}
