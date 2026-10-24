$ErrorActionPreference = 'Stop'
$runtime = Get-Content -LiteralPath (Join-Path $PSScriptRoot '.local\runtime.json') -Raw | ConvertFrom-Json
$appFile = Join-Path $PSScriptRoot 'app.py'
$appProcesses = Get-CimInstance Win32_Process | Where-Object { $_.Name -match '^python(w)?\.exe$' -and $_.CommandLine -like ('*"'+$appFile+'"*') }
foreach ($process in $appProcesses) { Stop-Process -Id $process.ProcessId -ErrorAction SilentlyContinue }
& $runtime.python (Join-Path $PSScriptRoot 'stop_mysql.py')
if ($LASTEXITCODE -ne 0) { throw 'No se pudo detener MySQL de forma normal.' }
Write-Host 'KING CLEANER detenido. Los datos permanecen guardados.'
