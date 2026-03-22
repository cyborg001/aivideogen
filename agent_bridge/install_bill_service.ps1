# 🛠️ Instalador de Servicio Bill Bridge
# Este script registra bill_receiver.py como una tarea programada de Windows

$ScriptName = "bill_receiver.py"
$TaskName = "BillBridgeService"
$BaseDir = "c:\Users\hp\aivideogen\agent_bridge"
$ScriptPath = Join-Path $BaseDir $ScriptName
$PythonPath = "pythonw.exe" # Usamos pythonw para que no abra ventana de consola

Write-Host "--- Configurando Bill Bridge como Servicio de Fondo ---" -ForegroundColor Cyan

# 1. Verificar existencia del archivo
if (-not (Test-Path $ScriptPath)) {
    Write-Error "No se encontró el archivo $ScriptPath"
    exit
}

# 2. Definir la acción (Ejecutar Python con el script)
# Se usa -WorkingDir para asegurar que cargue el .env correctamente
$Action = New-ScheduledTaskAction -Execute $PythonPath -Argument $ScriptPath -WorkingDirectory $BaseDir

# 3. Definir el disparador (Al iniciar sesión)
$Trigger = New-ScheduledTaskTrigger -AtLogOn

# 4. Definir configuraciones adicionales
$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

# 5. Registrar la tarea (Si ya existe, se actualiza)
Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Settings $Settings -Description "Servicio Bill Bridge para recepción de misiones por correo" -Force

Write-Host "✅ ¡Éxito! La tarea '$TaskName' ha sido registrada." -ForegroundColor Green
Write-Host "Bill ahora se iniciará automáticamente cada vez que inicies sesión."
Write-Host "Para iniciarla manualmente ahora, ejecuta: Start-ScheduledTask -TaskName $TaskName"
