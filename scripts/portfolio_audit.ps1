param(
    [string]$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path,
    [int]$MaxFileMB = 5
)

$ErrorActionPreference = "Stop"

$passes = New-Object System.Collections.Generic.List[string]
$warnings = New-Object System.Collections.Generic.List[string]
$failures = New-Object System.Collections.Generic.List[string]

function Add-Pass([string]$Message) { $passes.Add($Message) | Out-Null }
function Add-Warn([string]$Message) { $warnings.Add($Message) | Out-Null }
function Add-Fail([string]$Message) { $failures.Add($Message) | Out-Null }

function Get-RelativePath([string]$Path) {
    $root = $RepoRoot
    if (-not $root.EndsWith([System.IO.Path]::DirectorySeparatorChar)) {
        $root = $root + [System.IO.Path]::DirectorySeparatorChar
    }
    $rootUri = New-Object System.Uri($root)
    $pathUri = New-Object System.Uri($Path)
    $relative = $rootUri.MakeRelativeUri($pathUri).ToString()
    return [System.Uri]::UnescapeDataString($relative).Replace("/", [System.IO.Path]::DirectorySeparatorChar)
}

function New-UnicodeString([int[]]$CodePoints) {
    return -join ($CodePoints | ForEach-Object { [char]$_ })
}

function Read-Utf8([string]$Path) {
    return Get-Content -LiteralPath $Path -Raw -Encoding UTF8
}

$requiredFiles = @(
    "README.md",
    "AGENTS.md",
    ".gitignore",
    "requirements.txt",
    "LICENSE",
    "docs/case-study.md",
    "docs/workflow.md",
    "docs/prd-methodology.md",
    "docs/safe-demo.md",
    "docs/interview-summary.md",
    "skills/prd-research-agent/SKILL.md",
    "scripts/generate_prd.py",
    "scripts/competitor_matrix.py",
    "scripts/portfolio_audit.ps1",
    "configs/prd_rules.yaml",
    "configs/user_preferences.yaml",
    "examples/sample_requirement.md",
    "examples/sample_competitors.csv",
    "examples/generated_prd.md"
)

foreach ($file in $requiredFiles) {
    $path = Join-Path $RepoRoot $file
    if (Test-Path -LiteralPath $path) {
        Add-Pass "Required file exists: $file"
    } else {
        Add-Fail "Missing required file: $file"
    }
}

$readmePath = Join-Path $RepoRoot "README.md"
if (Test-Path -LiteralPath $readmePath) {
    $readmeStart = (Get-Content -LiteralPath $readmePath -TotalCount 8 -Encoding UTF8) -join "`n"
    $interviewerSummary = New-UnicodeString @(0x9762, 0x8bd5, 0x5b98, 0x20, 0x33, 0x30, 0x20, 0x79d2, 0x7248)
    if ($readmeStart -match [regex]::Escape($interviewerSummary)) {
        Add-Pass "README starts with the interviewer 30-second summary."
    } else {
        Add-Fail "README must include the interviewer 30-second summary near the top."
    }
}

$generatedPrdPath = Join-Path $RepoRoot "examples/generated_prd.md"
if (Test-Path -LiteralPath $generatedPrdPath) {
    $generatedPrd = Read-Utf8 $generatedPrdPath
    $featurePhrase = New-UnicodeString @(0x4ea7, 0x54c1, 0x6709)
    $acceptancePhrase = New-UnicodeString @(0x9a8c, 0x6536, 0x6807, 0x51c6)
    if ($generatedPrd -match [regex]::Escape($featurePhrase) -and $generatedPrd -match [regex]::Escape($acceptancePhrase)) {
        Add-Pass "Generated PRD includes feature overview and acceptance criteria."
    } else {
        Add-Fail "Generated PRD is missing feature overview or acceptance criteria."
    }
}

$allFiles = Get-ChildItem -LiteralPath $RepoRoot -Recurse -File -Force |
    Where-Object {
        $_.FullName -notmatch "\\\.git\\" -and
        $_.FullName -notmatch "\\__pycache__\\" -and
        $_.FullName -notmatch "\\\.pytest_cache\\"
    }

foreach ($file in $allFiles) {
    if ($file.Length -gt ($MaxFileMB * 1024 * 1024)) {
        Add-Fail "Large file exceeds ${MaxFileMB}MB: $(Get-RelativePath $file.FullName)"
    }
}
Add-Pass "Large file scan completed."

$textExtensions = @(".md", ".py", ".ps1", ".yaml", ".yml", ".txt", ".csv", ".gitignore", "")
$forbiddenProject = "Rough" + "Cut"
$lowerForbiddenProject = "rough" + "cut"
$sensitivePatterns = @(
    @{ Name = "private key"; Pattern = 'BEGIN (RSA |OPENSSH |DSA |EC |PGP )?PRIVATE KEY' },
    @{ Name = "OpenAI style key"; Pattern = 'sk-[A-Za-z0-9]{20,}' },
    @{ Name = "GitHub token"; Pattern = 'gh[pousr]_[A-Za-z0-9]{20,}' },
    @{ Name = "Slack token"; Pattern = 'xox[baprs]-[A-Za-z0-9-]{20,}' },
    @{ Name = "cloud access key"; Pattern = 'AKIA[0-9A-Z]{16}' },
    @{ Name = "password assignment"; Pattern = '(?i)\bpassword\s*[:=]\s*[''"]?[^''"\s#]{8,}' },
    @{ Name = "secret assignment"; Pattern = '(?i)\bsecret\s*[:=]\s*[''"]?[^''"\s#]{8,}' },
    @{ Name = "token assignment"; Pattern = '(?i)\btoken\s*[:=]\s*[''"]?[^''"\s#]{8,}' },
    @{ Name = "local absolute user path"; Pattern = '[A-Za-z]:\\Users\\[^\\\s]+' },
    @{ Name = "forbidden source project name"; Pattern = $forbiddenProject },
    @{ Name = "forbidden source project name lowercase"; Pattern = $lowerForbiddenProject }
)

foreach ($file in $allFiles) {
    if ($textExtensions -notcontains $file.Extension) {
        continue
    }

    try {
        $content = Read-Utf8 $file.FullName
    } catch {
        Add-Warn "Skipped unreadable text file: $(Get-RelativePath $file.FullName)"
        continue
    }

    foreach ($item in $sensitivePatterns) {
        if ($content -match $item.Pattern) {
            Add-Fail "Sensitive pattern '$($item.Name)' found in $(Get-RelativePath $file.FullName)"
        }
    }
}
Add-Pass "Sensitive information scan completed."

$exampleFiles = $allFiles | Where-Object { (Get-RelativePath $_.FullName).StartsWith("examples") }
$realDataPatterns = @(
    @{ Name = "email address"; Pattern = '(?i)[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}' },
    @{ Name = "long phone-like number"; Pattern = '(?<!\d)(\+?\d[\d\s-]{9,}\d)(?!\d)' },
    @{ Name = "national id-like number"; Pattern = '(?<!\d)\d{17}[\dXx](?!\d)' }
)

foreach ($file in $exampleFiles) {
    $content = Read-Utf8 $file.FullName
    # Input fingerprints are content digests, not contact data. Only mask the
    # documented JSON field and Markdown digest line; scan all other text.
    $dataScanContent = $content -replace '("analysis_id"\s*:\s*")[a-f0-9]{64}("|$)', '${1}<sha256>${2}'
    $dataScanContent = $dataScanContent -replace '(?m)^\u8f93\u5165\u6307\u7eb9\uff1a\x60[a-f0-9]{64}\x60\s*$', '<sha256>'
    foreach ($item in $realDataPatterns) {
        if ($dataScanContent -match $item.Pattern) {
            Add-Fail "Possible real data '$($item.Name)' found in $(Get-RelativePath $file.FullName)"
        }
    }
}
Add-Pass "Example data scan completed."

$gitDir = Join-Path $RepoRoot ".git"
if (Test-Path -LiteralPath $gitDir) {
    $remote = ""
    try {
        $remote = git -C $RepoRoot remote get-url origin 2>$null
    } catch {
        $remote = ""
    }

    if ([string]::IsNullOrWhiteSpace($remote)) {
        Add-Warn "GitHub publicness check skipped: origin remote is not configured yet."
    } elseif ($remote -notmatch "github\.com") {
        Add-Fail "Origin remote is not a GitHub URL: $remote"
    } else {
        $slug = $remote.Trim()
        $slug = $slug -replace "^git@github\.com:", ""
        $slug = $slug -replace "^https://github\.com/", ""
        $slug = $slug -replace "\.git$", ""

        $ghCommand = Get-Command gh -ErrorAction SilentlyContinue
        if ($null -eq $ghCommand) {
            Add-Warn "GitHub publicness check skipped: gh CLI not found."
        } else {
            $repoJson = gh repo view $slug --json isPrivate,nameWithOwner,url 2>$null
            if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($repoJson)) {
                Add-Warn "GitHub publicness check skipped: repo is not available through gh yet."
            } else {
                $repo = $repoJson | ConvertFrom-Json
                if ($repo.isPrivate -eq $true) {
                    Add-Fail "GitHub repository is private: $($repo.nameWithOwner)"
                } else {
                    Add-Pass "GitHub repository is public: $($repo.url)"
                }
            }
        }
    }
} else {
    Add-Warn "GitHub publicness check skipped: repository is not initialized yet."
}

foreach ($message in $passes) { Write-Host "[PASS] $message" }
foreach ($message in $warnings) { Write-Host "[WARN] $message" }
foreach ($message in $failures) { Write-Host "[FAIL] $message" }

if ($failures.Count -gt 0) {
    Write-Host "AUDIT RESULT: FAIL"
    exit 1
}

Write-Host "AUDIT RESULT: PASS"
exit 0
