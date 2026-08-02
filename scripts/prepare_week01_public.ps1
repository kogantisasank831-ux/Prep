[CmdletBinding()]
param(
    [string]$Source = "content/inbox/week-01-public-rewrite.md",
    [string]$Destination = "content/reviewed/week-01-public-review-candidate.md",
    [switch]$Force
)

$ErrorActionPreference = "Stop"

$sourcePath = Join-Path $PSScriptRoot "..\$Source"
$destinationPath = Join-Path $PSScriptRoot "..\$Destination"

if (-not (Test-Path -LiteralPath $sourcePath -PathType Leaf)) {
    throw "Source lesson not found: $sourcePath"
}

if ((Test-Path -LiteralPath $destinationPath) -and -not $Force) {
    throw "Destination already exists. Use -Force only when replacing reviewed edits is intentional."
}

$content = Get-Content -LiteralPath $sourcePath -Raw -Encoding utf8

$validFrontMatter = @"
---
layout: week
permalink: /weeks/week-01/
description: Build a typed, validated and testable document extraction API with Python and FastAPI.
title: Python for production AI systems
---
"@

$invalidFrontMatterPattern = '(?s)\A---\r?\n\r?\nlayout: week\r?\npermalink: /weeks/week-01/\r?\ndescription: Build a typed, validated and testable document extraction API with Python and FastAPI\.\r?\ntitle: Python for production AI systems\r?\n-+\r?\n'
$frontMatterMatch = [regex]::Match($content, $invalidFrontMatterPattern)
if (-not $frontMatterMatch.Success) {
    throw "The source front matter did not match the expected generated form."
}

$content = $validFrontMatter + $content.Substring($frontMatterMatch.Length)
$content = [regex]::Replace(
    $content,
    '(?m)^<!-- VERIFIED_EXCERPT: [a-z_]+ -->\r?\n\r?\n',
    ''
)

if ($content.Contains('VERIFIED_EXCERPT')) {
    throw "At least one unverified excerpt marker remains."
}

$destinationDirectory = Split-Path -Parent $destinationPath
New-Item -ItemType Directory -Path $destinationDirectory -Force | Out-Null
$utf8WithoutBom = New-Object System.Text.UTF8Encoding($false)
[System.IO.File]::WriteAllText($destinationPath, $content, $utf8WithoutBom)

Write-Output "Prepared $Destination from $Source"
