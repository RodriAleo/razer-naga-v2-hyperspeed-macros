# Genera la imagen NagaV2_atajos.png (guia de atajos) a partir de las tablas de abajo.
# Uso:  powershell -ExecutionPolicy Bypass -File generar_guia_atajos.ps1
# Al cambiar una macro: edita $cells y/o las secciones Hypershift y re-ejecuta.

Add-Type -AssemblyName System.Drawing
$W=920; $H=820
$bmp=New-Object System.Drawing.Bitmap $W,$H
$g=[System.Drawing.Graphics]::FromImage($bmp)
$g.SmoothingMode=[System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
$g.TextRenderingHint=[System.Drawing.Text.TextRenderingHint]::ClearTypeGridFit

$bg   =[System.Drawing.Color]::FromArgb(28,28,30)
$panel=[System.Drawing.Color]::FromArgb(44,44,48)
$panelEmpty=[System.Drawing.Color]::FromArgb(34,34,37)
$green=[System.Drawing.Color]::FromArgb(68,214,44)
$white=[System.Drawing.Color]::FromArgb(238,238,238)
$grey =[System.Drawing.Color]::FromArgb(160,160,165)
$dim  =[System.Drawing.Color]::FromArgb(95,95,100)

$bGreen=New-Object System.Drawing.SolidBrush $green
$bWhite=New-Object System.Drawing.SolidBrush $white
$bGrey =New-Object System.Drawing.SolidBrush $grey
$bDim  =New-Object System.Drawing.SolidBrush $dim
$bBlack=New-Object System.Drawing.SolidBrush ([System.Drawing.Color]::Black)
$bPanel=New-Object System.Drawing.SolidBrush $panel
$bPanelE=New-Object System.Drawing.SolidBrush $panelEmpty

$fTitle=New-Object System.Drawing.Font('Segoe UI',22,[System.Drawing.FontStyle]::Bold)
$fHead =New-Object System.Drawing.Font('Segoe UI',13,[System.Drawing.FontStyle]::Bold)
$fNum  =New-Object System.Drawing.Font('Segoe UI',12,[System.Drawing.FontStyle]::Bold)
$fCell =New-Object System.Drawing.Font('Segoe UI',12)
$fRow  =New-Object System.Drawing.Font('Segoe UI',14)
$fSmall=New-Object System.Drawing.Font('Segoe UI',11)

$sf=New-Object System.Drawing.StringFormat
$sf.LineAlignment=[System.Drawing.StringAlignment]::Center

$g.Clear($bg)
$g.FillRectangle($bGreen,0,0,$W,62)
$g.DrawString('RAZER NAGA V2 HYPERSPEED  -  Atajos',$fTitle,$bBlack,24,13)

# numero, texto, tipo (0=normal, 1=hypershift, 2=libre)
$cells=@(
 @(1,'Alt+Tab rapido',0),
 @(2,'Alt+Tab: ventana anterior',0),
 @(3,'Alt+Tab: ventana siguiente',0),
 @(4,'(libre)',2),
 @(5,'Abrir esta ayuda',0),
 @(6,'(libre)',2),
 @(7,'Pantalla completa (F11)',0),
 @(8,'(libre)',2),
 @(9,'(libre)',2),
 @(10,'HYPERSHIFT 1  (ver abajo)',1),
 @(11,'HYPERSHIFT 2  (ver abajo)',1),
 @(12,'Win+Tab: vista de tareas',0)
)
$mLeft=20; $gap=16; $top=80
$cellW=[int](($W-2*$mLeft-2*$gap)/3)
$cellH=92; $vgap=14
for($i=0;$i -lt 12;$i++){
  $col=$i%3; $row=[int][math]::Floor($i/3)
  $cx=$mLeft+$col*($cellW+$gap)
  $cy=$top+$row*($cellH+$vgap)
  $t=$cells[$i][2]
  $pBrush= if($t -eq 2){$bPanelE}else{$bPanel}
  $accent= if($t -eq 2){$bDim}else{$bGreen}
  $g.FillRectangle($pBrush,$cx,$cy,$cellW,$cellH)
  $g.FillRectangle($accent,$cx,$cy,5,$cellH)
  $g.FillEllipse($accent,($cx+16),($cy+12),30,30)
  $n=[string]$cells[$i][0]
  $sz=$g.MeasureString($n,$fNum)
  $numCol= if($t -eq 2){$bWhite}else{$bBlack}
  $g.DrawString($n,$fNum,$numCol,($cx+16+(30-$sz.Width)/2),($cy+12+(30-$sz.Height)/2))
  $tb= if($t -eq 1){$bGreen}elseif($t -eq 2){$bDim}else{$bWhite}
  $rect=New-Object System.Drawing.RectangleF (($cx+56),($cy+8),($cellW-66),($cellH-16))
  $g.DrawString([string]$cells[$i][1],$fCell,$tb,$rect,$sf)
}

$y=$top+4*$cellH+3*$vgap+22
function Section($title,$pairs){
  $g.DrawString($title,$fHead,$bGreen,24,$script:y); $script:y+=30
  foreach($p in $pairs){
    $g.DrawString([string]$p[0],$fRow,$bGrey,56,$script:y)
    $g.DrawString([string]$p[1],$fRow,$bWhite,360,$script:y)
    $script:y+=28
  }
  $script:y+=8
}
Section 'HYPERSHIFT 1  -  Boton 10  (manten pulsado)' @(
 @('Rueda arriba / abajo','Subir / bajar volumen'),
 @('Clic de rueda','Play / Pausa multimedia'),
 @('Tilt derecha / izquierda','Pista siguiente / anterior')
)
Section 'HYPERSHIFT 2  -  Boton 11  (manten pulsado)' @(
 @('Rueda arriba / abajo','Acercar / alejar zoom  (Ctrl + / -)'),
 @('Clic de rueda','Abrir software de capturas  (Ctrl+Q)'),
 @('Clic derecho','Portapapeles  (Win+V)'),
 @('Tilt izquierda / derecha','Copiar / Pegar  (Ctrl+C / Ctrl+V)')
)

$g.DrawString('Pulsa el Boton 5 para volver a abrir esta ayuda.',$fSmall,$bGrey,24,($H-30))

$out=Join-Path $PSScriptRoot 'NagaV2_atajos.png'
$bmp.Save($out,[System.Drawing.Imaging.ImageFormat]::Png)
$g.Dispose(); $bmp.Dispose()
Write-Output "Imagen generada: $out"
