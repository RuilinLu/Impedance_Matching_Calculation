# Example code-signing script (requires YOUR OWN Authenticode certificate).
#
# This repository does NOT contain a certificate.  A self-signed certificate is
# not trusted on other PCs and does not prevent SmartScreen/Kaspersky warnings.
# Buy or obtain an OV/EV code-signing certificate from a trusted CA, then run:
#
#   powershell -ExecutionPolicy Bypass -File installer\sign_example.ps1 `
#       -Pfx "D:\certs\mycert.pfx" -Password "***" `
#       -Files "release\ImpedanceMCP_v4.2.0_App\ImpedanceMCP.exe",
#              "release\ImpedanceMCP_Setup_v4.2.0.exe"
#
param(
    [Parameter(Mandatory = $true)][string]$Pfx,
    [Parameter(Mandatory = $true)][string]$Password,
    [Parameter(Mandatory = $true)][string[]]$Files
)

$signtool = Get-Command signtool.exe -ErrorAction SilentlyContinue
if (-not $signtool) {
    $candidates = @(
        "${env:ProgramFiles(x86)}\Windows Kits\10\bin\*\x64\signtool.exe",
        "${env:ProgramFiles}\Windows Kits\10\bin\*\x64\signtool.exe"
    )
    foreach ($pattern in $candidates) {
        $hit = Get-ChildItem $pattern -ErrorAction SilentlyContinue | Select-Object -First 1
        if ($hit) { $signtool = $hit; break }
    }
}
if (-not $signtool) {
    throw "signtool.exe not found. Install the Windows SDK signing tools."
}

foreach ($file in $Files) {
    if (-not (Test-Path $file)) {
        Write-Warning "missing: $file"
        continue
    }
    & $signtool.Source sign /fd SHA256 /tr http://timestamp.digicert.com /td SHA256 `
        /f $Pfx /p $Password $file
    if ($LASTEXITCODE -ne 0) { throw "sign failed: $file" }
    & $signtool.Source verify /pa $file
}

Write-Host "Signed files:" -ForegroundColor Green
$Files | ForEach-Object { Get-AuthenticodeSignature $_ | Format-Table Path, Status, SignerCertificate }
