param([switch]$NoBrowser)
$ErrorActionPreference = 'Stop'
$projectRoot = $PSScriptRoot
$runtimeFile = Join-Path $projectRoot '.local\runtime.json'
if (-not (Test-Path -LiteralPath $runtimeFile)) {
    throw 'Este acceso requiere la configuración local. Consulta LEEME.md para instalar en otro equipo.'
}
$runtime = Get-Content -LiteralPath $runtimeFile -Raw | ConvertFrom-Json
$mysqlBase = Split-Path (Split-Path $runtime.mysql -Parent) -Parent
$mysqlData = Join-Path $projectRoot '.local\mysql-data'
if (-not (Test-Path -LiteralPath $runtime.mysql) -or -not (Test-Path -LiteralPath $runtime.python)) {
    throw 'No se encontró Python o MySQL. Mantén la carpeta work del espacio de trabajo junto a outputs.'
}
$mysqlPort = Get-NetTCPConnection -LocalPort 3307 -State Listen -ErrorAction SilentlyContinue
if (-not $mysqlPort) {
    $mysqlProcess = Start-Process -FilePath $runtime.mysql -ArgumentList @('--no-defaults', ('--basedir="'+$mysqlBase+'"'), ('--datadir="'+$mysqlData+'"'), '--port=3307', '--bind-address=127.0.0.1', '--mysqlx=OFF', '--default-time-zone=-04:00', '--console') -WindowStyle Hidden -PassThru -RedirectStandardOutput (Join-Path $projectRoot '.local\mysql-out.log') -RedirectStandardError (Join-Path $projectRoot '.local\mysql-err.log')
    $mysqlProcess.Id | Set-Content -LiteralPath (Join-Path $projectRoot '.local\mysql.pid')
}
$healthy = $false
try { $result = Invoke-RestMethod 'http://127.0.0.1:5050/health' -TimeoutSec 2; $healthy = $result.status -eq 'ok' } catch {}
if (-not $healthy) {
    $occupied = Get-NetTCPConnection -LocalPort 5050 -State Listen -ErrorAction SilentlyContinue
    if ($occupied) { throw 'El puerto 5050 está ocupado o MySQL aún no está listo. Espera unos segundos y vuelve a iniciar.' }
    $appFile = Join-Path $projectRoot 'app.py'
    $appProcess = Start-Process -FilePath $runtime.python -ArgumentList @(('"'+$appFile+'"')) -WorkingDirectory $projectRoot -WindowStyle Hidden -PassThru -RedirectStandardOutput (Join-Path $projectRoot '.local\app-out.log') -RedirectStandardError (Join-Path $projectRoot '.local\app-err.log')
    $appProcess.Id | Set-Content -LiteralPath (Join-Path $projectRoot '.local\app.pid')
}
for ($attempt=0; $attempt -lt 30; $attempt++) {
    try { $result = Invoke-RestMethod 'http://127.0.0.1:5050/health' -TimeoutSec 2; if ($result.status -eq 'ok') { if (-not $NoBrowser) { Start-Process 'http://127.0.0.1:5050' }; Write-Host 'KING CLEANER listo en http://127.0.0.1:5050'; exit 0 } } catch {}
    Start-Sleep -Milliseconds 500
}
throw 'No se pudo iniciar. Revisa los registros de la carpeta .local.'
