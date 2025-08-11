param([string]$SourceDir = ".", [string]$ZipPath = "autoflow_pro_flask.zip")

if (Test-Path $ZipPath) { Remove-Item $ZipPath }
Compress-Archive -Path "$SourceDir/app","$SourceDir/run.py","$SourceDir/requirements.txt","$SourceDir/README.md","$SourceDir/USER_MANUAL.md" -DestinationPath $ZipPath
Write-Host "Created $ZipPath"
