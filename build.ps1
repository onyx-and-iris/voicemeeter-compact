param(
    [Parameter(Mandatory = $true)]
    [string]$prefix,
    [string]$theme
)

function Format-Path {
    param($Kind)
    return @(
        $prefix,
        (& { if ($theme) { $theme } else { "" } }),
        "${Kind}"
    ).Where({ $_ -ne "" }) -Join "_"
}

function Compress-Builds {
    $target = Join-Path -Path $PSScriptRoot -ChildPath "dist"
    @("basic", "banana", "potato") | ForEach-Object {
        $compress_path = Format-Path -Kind $_
        Compress-Archive -Path $(Join-Path -Path $target -ChildPath $compress_path) -DestinationPath $(Join-Path -Path $target -ChildPath "${compress_path}.zip") -Force
    } 
}

function Get-Builds {
    @("basic", "banana", "potato") | ForEach-Object {
        $spec_path = Format-Path -Kind $_

        "building $spec_path" | Write-Host

        poetry run pyinstaller "$spec_path.spec" --noconfirm
    }  
}

function main {
    Get-Builds

    Compress-Builds
}

if ($MyInvocation.InvocationName -ne '.') { main }