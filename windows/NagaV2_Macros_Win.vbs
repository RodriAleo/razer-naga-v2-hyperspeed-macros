' Lanza naga_macros_win.py SIN ventana de consola (usa pythonw.exe).
' Doble clic para arrancar las macros.
' Para el autoarranque: pon un acceso directo de este .vbs en shell:startup
' Para cerrarlo: menu del icono de bandeja, o finaliza "pythonw.exe" en el
' Administrador de tareas.

Set fso = CreateObject("Scripting.FileSystemObject")
Set sh  = CreateObject("WScript.Shell")

carpeta = fso.GetParentFolderName(WScript.ScriptFullName)
script  = carpeta & "\naga_macros_win.py"

If Not fso.FileExists(script) Then
    MsgBox "No encuentro naga_macros_win.py junto a este lanzador:" & vbCrLf & _
           script, vbCritical, "Naga V2 - Macros"
    WScript.Quit 1
End If

' pythonw.exe = Python sin consola. Se busca en el PATH; si no esta, se avisa.
sh.CurrentDirectory = carpeta
On Error Resume Next
sh.Run "pythonw.exe """ & script & """", 0, False
If Err.Number <> 0 Then
    MsgBox "No pude ejecutar pythonw.exe. Verifica que Python este instalado " & _
           "y en el PATH." & vbCrLf & vbCrLf & "Detalle: " & Err.Description, _
           vbCritical, "Naga V2 - Macros"
    WScript.Quit 1
End If
