# Cria um atalho "Club GG Hand Reader" no ambiente de trabalho, apontando
# para start_app.bat neste projeto. Corre uma vez com:
#   powershell -ExecutionPolicy Bypass -File create_shortcut.ps1

$projectDir = $PSScriptRoot
$batPath = Join-Path $projectDir "start_app.bat"
$desktop = [Environment]::GetFolderPath("Desktop")
$shortcutPath = Join-Path $desktop "Club GG Hand Reader.lnk"

$shell = New-Object -ComObject WScript.Shell
$shortcut = $shell.CreateShortcut($shortcutPath)
$shortcut.TargetPath = $batPath
$shortcut.WorkingDirectory = $projectDir
$shortcut.WindowStyle = 7  # minimized console
$shortcut.IconLocation = "shell32.dll,167"  # spade-ish card icon
$shortcut.Description = "Abrir o Club GG Hand Reader"
$shortcut.Save()

Write-Host "Atalho criado em: $shortcutPath"
