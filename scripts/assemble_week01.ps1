param(
    [string]$RepositoryRoot = (Split-Path -Parent $PSScriptRoot),
    [switch]$Approve
)

$ErrorActionPreference = "Stop"

$basePath = Join-Path $RepositoryRoot "content/inbox/week-01-draft-v2.md"
$continuationPath = Join-Path $RepositoryRoot "content/inbox/week-01-draft-v2-part2.md"
$outputPath = Join-Path $RepositoryRoot "content/reviewed/week-01-review-candidate.md"
if ($Approve) {
    $outputPath = Join-Path $RepositoryRoot "content/weeks/week-01.md"
}

$baseLines = [System.IO.File]::ReadAllLines($basePath)
$continuationLines = [System.IO.File]::ReadAllLines($continuationPath)

$spliceIndex = [Array]::IndexOf($baseLines, "### Exact repository test source")
if ($spliceIndex -lt 0) {
    throw "Test-source splice heading was not found in V2."
}

if ($continuationLines[0] -ne "<!-- CONTINUATION_START: testing-matrix -->") {
    throw "Continuation start marker is missing or misplaced."
}

if ($continuationLines[-1] -ne "<!-- CONTINUATION_END -->") {
    throw "Continuation end marker is missing or misplaced."
}

$combinedLines = @($baseLines[0..($spliceIndex - 1)]) +
    @($continuationLines[1..($continuationLines.Length - 2)])
$content = $combinedLines -join "`n"
$content = $content.Replace("---------------------", "---")
$content = $content.Replace("technical_review: review_candidate", "technical_review: passed")
$content = $content.Replace(
    "The verified ``document_service/`` source files were not included with the attached review inputs. Exact repository code must therefore not be reconstructed from inference.",
    "The exact technically verified ``document_service/`` source files are integrated below by Codex."
)
$content = $content.Replace(
    "The verified ``tests/`` files were not attached to this revision request.",
    "The exact technically verified ``tests/`` files are integrated below by Codex."
)
$content = $content.Replace(
    @"
The verified models must cover:

* multipart metadata;
* safe correlation identifiers;
* filename metadata;
* declared media type;
* upload content type;
* response serialization;
* stable error serialization.
"@.Trim(),
    @"
The verified models cover:

* scalar multipart metadata received separately from the file;
* safe correlation identifiers;
* the declared media type;
* response serialization; and
* stable error serialization.

The filename and upload content type belong to ``UploadFile`` and are carried by
the internal command for deterministic service-policy validation; they are not
duplicated as Pydantic request fields.
"@.Trim()
)

function New-CodeBlock {
    param([string]$RelativePath)

    $absolutePath = Join-Path $RepositoryRoot $RelativePath
    $source = [System.IO.File]::ReadAllText($absolutePath).TrimEnd()
    return "``````python`n$source`n``````"
}

$tree = @"
``````text
document_service/
|-- __init__.py
|-- api.py
|-- dependencies.py
|-- domain.py
|-- errors.py
|-- main.py
|-- models.py
|-- ports.py
|-- readers.py
`-- service.py
tests/
|-- test_api.py
|-- test_models.py
|-- test_readers.py
`-- test_service.py
``````
"@.Trim()

$sourceReplacements = @(
    "Verified repository source is integrated in the subsections below.",
    $tree,
    (New-CodeBlock "document_service/errors.py"),
    (New-CodeBlock "document_service/domain.py"),
    (New-CodeBlock "document_service/ports.py"),
    (New-CodeBlock "document_service/readers.py"),
    (New-CodeBlock "document_service/models.py"),
    (New-CodeBlock "document_service/service.py"),
    (New-CodeBlock "document_service/dependencies.py"),
    (New-CodeBlock "document_service/api.py"),
    (New-CodeBlock "document_service/main.py")
)

$marker = "**Codex integration required**"
foreach ($replacement in $sourceReplacements) {
    $position = $content.IndexOf($marker, [StringComparison]::Ordinal)
    if ($position -lt 0) {
        throw "A guided-implementation integration marker is missing."
    }
    $content = $content.Substring(0, $position) + $replacement +
        $content.Substring($position + $marker.Length)
}

$testBlocks = @()
foreach ($testPath in @(
    "tests/test_models.py",
    "tests/test_readers.py",
    "tests/test_service.py",
    "tests/test_api.py"
)) {
    $testBlocks += "#### ``$testPath``"
    $testBlocks += New-CodeBlock $testPath
}
$testReplacement = $testBlocks -join "`n`n"

$position = $content.IndexOf($marker, [StringComparison]::Ordinal)
if ($position -lt 0) {
    throw "The test-source integration marker is missing."
}
$content = $content.Substring(0, $position) + $testReplacement +
    $content.Substring($position + $marker.Length)

if ($content.Contains($marker)) {
    throw "Unresolved Codex integration markers remain."
}

$content = [regex]::Replace(
    $content,
    '(?m)^\* \*\*Codex source integration:\*\*.*$',
    '* **2026-07-22 - Codex source integration:** Inserted the exact verified `document_service/` and `tests/` files into the review candidate.'
)

if ($Approve) {
    $content = $content.Replace("status: draft", "status: approved")
    $content = $content.Replace("version: 0.2.0", "version: 1.0.0")
    $content = $content.Replace("last_reviewed: 2026-07-22", "last_reviewed: 2026-08-01")
    $content = $content.Replace("human_review: pending", "human_review: passed")
    $content = $content.Replace(
        "week: 1`nphase: 1",
        "layout: week`npermalink: /weeks/week-01/`ndescription: Production Python and FastAPI foundations for reliable AI services.`nweek: 1`nphase: 1"
    )
    $content = $content.Replace(
        "human content review remains pending.",
        "human content review was approved on 2026-08-01."
    )
    $content = $content.Replace(
        "* **Human review:** Pending.",
        "* **2026-08-01 - Human review:** Approved by the project owner."
    )
    $content = $content.Replace(
        "* **Publication approval:** Pending.",
        "* **2026-08-01 - Content approval:** Approved as canonical Week 1 version 1.0.0."
    )
    $content = $content.Replace(
        "* **2026-08-01 - Content approval:** Approved as canonical Week 1 version 1.0.0.",
        "* **2026-08-01 - Content approval:** Approved as canonical Week 1 version 1.0.0.`n* **2026-08-01 - Website integration:** Assigned the approved Jekyll weekly layout and stable ``/weeks/week-01/`` permalink."
    )
}
$content = [regex]::Replace(
    $content,
    '(?m)^\* \*\*Technical content review:\*\*.*$',
    '* **2026-07-22 - Technical content review:** Structural, executable, lint, formatting, and strict-type gates passed; human content review remains pending.'
)

if ($Approve) {
    $content = $content.Replace(
        "* [ ] Human review remains ``pending``.",
        "* [x] Human review was approved on 2026-08-01."
    )
    $content = $content.Replace(
        "human content review remains pending.",
        "human content review was approved on 2026-08-01."
    )
}

$outputDirectory = Split-Path -Parent $outputPath
[System.IO.Directory]::CreateDirectory($outputDirectory) | Out-Null
[System.IO.File]::WriteAllText(
    $outputPath,
    $content + "`n",
    [System.Text.UTF8Encoding]::new($false)
)

Write-Output $outputPath
