# PowerShell launcher for Skilly
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
if (Test-Path "$ScriptDir\skilly_core") {
    $PkgRoot = $ScriptDir
} elseif (Test-Path "$ScriptDir\..\skilly_core") {
    $PkgRoot = (Resolve-Path "$ScriptDir\..").Path
} else {
    $PkgRoot = $ScriptDir
}

$env:PYTHONPATH = "$PkgRoot;$env:PYTHONPATH"
& python -m skilly_core.cli @args
