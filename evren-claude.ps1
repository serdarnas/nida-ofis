# Nida Zeytin Ajan Ofisi — EVREN Anthropic Geçidi ile Claude Code Başlatıcı (Windows PowerShell)
$envDosyasi = Join-Path $PSScriptRoot ".env"
if (Test-Path $envDosyasi) {
    Get-Content $envDosyasi | ForEach-Object {
        if ($_ -match '^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*)\s*$') {
            $k = $matches[1]
            $v = $matches[2].Trim('"', "'")
            [System.Environment]::SetEnvironmentVariable($k, $v, "Process")
        }
    }
}

$env:ANTHROPIC_BASE_URL = "https://evren-llmapi.ssyz.org.tr"
$env:ANTHROPIC_AUTH_TOKEN = $env:EVREN_API_KEY
$env:ANTHROPIC_MODEL = "glm-5.3"
$env:ANTHROPIC_DEFAULT_OPUS_MODEL = "glm-5.3"
$env:ANTHROPIC_DEFAULT_SONNET_MODEL = "deepseek-v4.1-flash"
$env:ANTHROPIC_DEFAULT_HAIKU_MODEL = "qwen3.8-flash-next"
$env:CLAUDE_CODE_SUBAGENT_MODEL = "deepseek-v4.1-flash"
$env:CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC = "1"

Write-Host "EVREN LLM Geçidi aktif: $env:ANTHROPIC_BASE_URL (Model: $env:ANTHROPIC_MODEL)" -ForegroundColor Green
claude @args
