# Publish this folder to the course Posit Connect server from Windows.
# Put CONNECT_SERVER and CONNECT_API_KEY in a gitignored .env first.
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
if (-not (Test-Path .env)) {
  throw "Copy .env.example to .env and fill in CONNECT_SERVER and CONNECT_API_KEY. Do not commit .env."
}
Get-Content .env | ForEach-Object {
  $line = $_.Trim()
  if ($line -eq "" -or $line.StartsWith("#") -or -not $line.Contains("=")) { return }
  $k, $v = $line.Split("=", 2)
  Set-Item -Path "Env:$($k.Trim())" -Value $v.Trim()
}
if (-not $env:CONNECT_SERVER -or -not $env:CONNECT_API_KEY) {
  throw "CONNECT_SERVER and CONNECT_API_KEY must both be set in .env."
}
rsconnect add --server $env:CONNECT_SERVER --api-key $env:CONNECT_API_KEY --name connect
rsconnect deploy flask --server connect --entrypoint app:app .
