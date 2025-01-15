param(
    [Parameter(Mandatory = $true)]
    [string]$prefix,
    [string]$theme
)

function Format-SpecName {
    param(
        [string]$Kind
    )
    return @(
        $prefix,
        (& { if ($theme) { $theme } else { "" } }),
        $Kind
    ).Where({ $_ -ne "" }) -Join "_"
}

function Compress-Builds {
    $target = Join-Path -Path $PSScriptRoot -ChildPath "dist"
    @("basic", "banana", "potato") | ForEach-Object {
        $compressPath = Format-SpecName -Kind $_
        Compress-Archive -Path (Join-Path -Path $target -ChildPath $compressPath) -DestinationPath (Join-Path -Path $target -ChildPath "${compressPath}.zip") -Force
    } 
}

function Get-Builds {
    @("basic", "banana", "potato") | ForEach-Object {
        $specName = Format-SpecName -Kind $_

        Write-Host "building $specName"

        poetry run pyinstaller --noconfirm --distpath (Join-Path -Path "dist" -ChildPath $specName) (Join-Path -Path "spec" -ChildPath "${specName}.spec")
    }
}

function main {
    Get-Builds
    Compress-Builds
}

if ($MyInvocation.InvocationName -ne '.') { main }