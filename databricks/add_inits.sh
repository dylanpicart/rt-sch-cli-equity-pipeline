#!/usr/bin/env bash
set -euo pipefail

echo "📦 Creating __init__.py files for Databricks package structure..."

for d in . bronze silver snowflake utils configs workflows notebooks dbt; do
    if [ -d "$d" ]; then
        touch "$d/__init__.py"
        echo "  - Added $d/__init__.py"
    else
        echo "  - Skipped missing dir: $d"
    fi
done

echo "✅ All __init__.py files created."
