@echo off
rem Stops the review app started by "Start Capacity Monitor.bat".
powershell -NoProfile -Command "Get-CimInstance Win32_Process -Filter \"Name='python.exe'\" | Where-Object { $_.CommandLine -like '*-m webapp.app*' } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force; Write-Output ('stopped ' + $_.ProcessId) }"
echo done
