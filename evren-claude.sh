#!/usr/bin/env bash
# Nida Zeytin Ajan Ofisi — EVREN Anthropic Geçidi ile Claude Code Başlatıcı (Linux / macOS)
set -e
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ -f "$DIR/.env" ]; then
  set -a
  source "$DIR/.env"
  set +a
fi

export ANTHROPIC_BASE_URL="https://evren-llmapi.ssyz.org.tr"
export ANTHROPIC_AUTH_TOKEN="${EVREN_API_KEY}"
export ANTHROPIC_MODEL="glm-5.3"
export ANTHROPIC_DEFAULT_OPUS_MODEL="glm-5.3"
export ANTHROPIC_DEFAULT_SONNET_MODEL="deepseek-v4.1-flash"
export ANTHROPIC_DEFAULT_HAIKU_MODEL="qwen3.8-flash-next"
export CLAUDE_CODE_SUBAGENT_MODEL="deepseek-v4.1-flash"
export CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1

echo "EVREN LLM Geçidi aktif: $ANTHROPIC_BASE_URL (Model: $ANTHROPIC_MODEL)"
exec claude "$@"
