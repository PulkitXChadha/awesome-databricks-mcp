#!/bin/bash

# Databricks MCP Project Status Line  
# Enhanced multi-line statusline with Claude Code integration showing:
# Line 1: Model, prompt, directory, git, services, processes, conversation, session metrics, system info
# Line 2: Last prompt text with thought bubble emoji (💭) - truncated to 100 chars if needed
#
# Features:
# - Model name with robot emoji (🤖)
# - Current prompt with clipboard emoji (📋) if active
# - Project directory with folder emoji (📁)
# - Git branch with plant emoji (🌿) + status indicators (* uncommitted, + untracked)
# - Service status: DB (Databricks), MCP (endpoint health), BE (backend), FE (frontend)
# - Active processes: 🧪 (testing), 🚀 (deployment)
# - Conversation context: 💬 (message count if reasonable)
# - Session metrics: 🧮 (token usage in K format), 💰 (estimated cost), ⏱️ (session duration)
# - System info: hostname and current time
# - Last prompt text preview on second line

# Read input JSON from stdin
input=$(cat)

# DEBUG: Uncomment the following lines to debug JSON structure issues
# echo "DEBUG: Input JSON structure:" >&2
# echo "$input" | jq . >&2
# echo "DEBUG: Conversation keys:" >&2  
# echo "$input" | jq -r 'if has("conversation") then .conversation | keys else "No conversation key" end' >&2
# echo "DEBUG: Available top-level keys:" >&2
# echo "$input" | jq -r 'keys' >&2

# Extract key information from Claude Code context
model_name=$(echo "$input" | jq -r '.model.display_name // "Claude"')
current_dir=$(echo "$input" | jq -r '.workspace.current_dir // "unknown"')
project_dir=$(echo "$input" | jq -r '.workspace.project_dir // "unknown"')
output_style=$(echo "$input" | jq -r '.output_style.name // "default"')
conversation_id=$(echo "$input" | jq -r '.conversation.id // ""')
total_tokens=$(echo "$input" | jq -r '.conversation.total_tokens // 0')
message_count=$(echo "$input" | jq -r '.conversation.message_count // 0')

# Extract session timing information
session_start=$(echo "$input" | jq -r '.conversation.started_at // ""')
current_timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

# Extract prompt information
current_prompt=$(echo "$input" | jq -r '.prompts.current.name // ""')
prompt_description=$(echo "$input" | jq -r '.prompts.current.description // ""')

# Extract last user message/prompt text (truncate if too long)
# Try multiple possible locations in the JSON structure
last_prompt_text=""

# Method 1: Try messages array (original approach)
if [ -z "$last_prompt_text" ]; then
    last_prompt_text=$(echo "$input" | jq -r '.conversation.messages[-1].content // empty' 2>/dev/null | head -c 100)
fi

# Method 2: Try direct user_message field
if [ -z "$last_prompt_text" ] || [ "$last_prompt_text" = "null" ]; then
    last_prompt_text=$(echo "$input" | jq -r '.user_message // empty' 2>/dev/null | head -c 100)
fi

# Method 3: Try current message content
if [ -z "$last_prompt_text" ] || [ "$last_prompt_text" = "null" ]; then
    last_prompt_text=$(echo "$input" | jq -r '.message.content // empty' 2>/dev/null | head -c 100)
fi

# Method 4: Try conversation current_message
if [ -z "$last_prompt_text" ] || [ "$last_prompt_text" = "null" ]; then
    last_prompt_text=$(echo "$input" | jq -r '.conversation.current_message // empty' 2>/dev/null | head -c 100)
fi

# Method 5: Try messages array with different structure
if [ -z "$last_prompt_text" ] || [ "$last_prompt_text" = "null" ]; then
    last_prompt_text=$(echo "$input" | jq -r '.conversation.messages | if type == "array" and length > 0 then .[length-1] | if type == "object" then .content else . end else empty end' 2>/dev/null | head -c 100)
fi

# Clean up null values and empty strings
if [ "$last_prompt_text" = "null" ] || [ -z "$last_prompt_text" ]; then
    last_prompt_text=""
fi

# Get basic system info
user=$(whoami)
hostname=$(hostname -s)
current_time=$(date "+%H:%M")

# Calculate session duration (if session_start is available)
session_duration=""
if [ -n "$session_start" ] && [ "$session_start" != "null" ]; then
    # Debug session start parsing
    # echo "DEBUG: session_start = '$session_start'" >&2
    
    # Try different date parsing approaches for cross-platform compatibility
    start_epoch=""
    current_epoch=$(date -u +%s)
    
    # Try GNU date first (gdate on macOS)
    if command -v gdate >/dev/null 2>&1; then
        start_epoch=$(gdate -d "$session_start" +%s 2>/dev/null)
        # echo "DEBUG: gdate result = '$start_epoch'" >&2
    fi
    
    # Try BSD date (macOS native) - force UTC interpretation
    if [ -z "$start_epoch" ]; then
        # Handle both with and without Z suffix
        if [[ "$session_start" == *"Z" ]]; then
            start_epoch=$(TZ=UTC date -j -f "%Y-%m-%dT%H:%M:%SZ" "$session_start" +%s 2>/dev/null)
        else
            start_epoch=$(TZ=UTC date -j -f "%Y-%m-%dT%H:%M:%S" "$session_start" +%s 2>/dev/null)
        fi
        # echo "DEBUG: BSD date result = '$start_epoch'" >&2
    fi
    
    # Try standard date (Linux)
    if [ -z "$start_epoch" ]; then
        start_epoch=$(date -d "$session_start" +%s 2>/dev/null)
        # echo "DEBUG: standard date result = '$start_epoch'" >&2
    fi
    
    # Calculate duration if we got a valid start time
    if [ -n "$start_epoch" ] && [ "$start_epoch" != "0" ] && [ "$start_epoch" -gt 0 ]; then
        duration_seconds=$((current_epoch - start_epoch))
        # echo "DEBUG: current_epoch=$current_epoch, start_epoch=$start_epoch, duration_seconds=$duration_seconds" >&2
        
        # Only show duration if it's reasonable (less than 24 hours)
        if [ $duration_seconds -ge 0 ] && [ $duration_seconds -lt 86400 ]; then
            if [ $duration_seconds -lt 60 ]; then
                session_duration="${duration_seconds}s"
            elif [ $duration_seconds -lt 3600 ]; then
                session_duration="$((duration_seconds / 60))m"
            else
                hours=$((duration_seconds / 3600))
                minutes=$(((duration_seconds % 3600) / 60))
                session_duration="${hours}h${minutes}m"
            fi
        fi
    fi
fi

# Format token count (K for thousands)
formatted_tokens="$total_tokens"
if [ "$total_tokens" -gt 1000 ]; then
    formatted_tokens="$((total_tokens / 1000))K"
fi

# Calculate estimated cost based on Claude pricing
# Claude 3.5 Sonnet pricing: ~$3 per million input tokens, ~$15 per million output tokens
# Using a conservative estimate of $6 per million tokens (average)
estimated_cost=""
if [ "$total_tokens" -gt 0 ]; then
    # Calculate cost in cents to avoid floating point in bash
    cost_cents=$((total_tokens * 600 / 100000))  # $6 per million = 0.6 cents per 100 tokens
    
    if [ $cost_cents -lt 100 ]; then
        # Less than $1 - show in cents
        estimated_cost="${cost_cents}¢"
    else
        # $1 or more - show in dollars
        cost_dollars=$((cost_cents / 100))
        cost_remainder=$((cost_cents % 100))
        if [ $cost_remainder -eq 0 ]; then
            estimated_cost="\$${cost_dollars}"
        else
            estimated_cost="\$${cost_dollars}.$(printf "%02d" $cost_remainder)"
        fi
    fi
fi

# Project-specific information
project_name="awesome-databricks-mcp"

# Git information (if in git repo)
git_branch=""
git_status=""
if git rev-parse --git-dir > /dev/null 2>&1; then
    git_branch=$(git branch --show-current 2>/dev/null || echo "detached")
    # Check if there are uncommitted changes
    if ! git diff-index --quiet HEAD -- 2>/dev/null; then
        git_status="*"
    fi
    # Check if there are untracked files
    if [ -n "$(git ls-files --others --exclude-standard 2>/dev/null)" ]; then
        git_status="${git_status}+"
    fi
fi

# Databricks connection status (check if env vars are set)
databricks_status="❌"
if [ -n "$DATABRICKS_HOST" ] && [ -n "$DATABRICKS_TOKEN" ]; then
    databricks_status="🟢"
elif [ -f ".env.local" ] && grep -q "DATABRICKS_HOST" ".env.local"; then
    databricks_status="🟡"
fi

# Development server status (check if ports are in use)
backend_status="❌"
frontend_status="❌"
mcp_status="❌"
if lsof -i:8000 > /dev/null 2>&1; then
    backend_status="🟢"
    # Check if MCP endpoint is responding
    if curl -s -f http://localhost:8000/mcp/ > /dev/null 2>&1; then
        mcp_status="🟢"
    else
        mcp_status="🟡"
    fi
fi
if lsof -i:5173 > /dev/null 2>&1; then
    frontend_status="🟢"
fi

# Check for active testing or deployment
testing_status=""
if pgrep -f "pytest" > /dev/null 2>&1; then
    testing_status="🧪"
fi
if pgrep -f "databricks.*deploy" > /dev/null 2>&1; then
    testing_status="${testing_status}🚀"
fi

# Directory context - show relative path if we're in the project
display_dir="$current_dir"
if [[ "$current_dir" == *"$project_name"* ]]; then
    # Show relative path from project root
    project_root=$(echo "$current_dir" | sed "s|.*$project_name|$project_name|")
    display_dir="$project_root"
fi

# Build the status line with colors and emojis for better visual scanning
printf "\033[1;35m🤖%s\033[0m " "$model_name"

# Current prompt (if set)
if [ -n "$current_prompt" ] && [ "$current_prompt" != "null" ]; then
    printf "\033[1;33m📋%s\033[0m " "$current_prompt"
fi

# Directory and git context
printf "\033[1;34m📁%s\033[0m " "$display_dir"
if [ -n "$git_branch" ]; then
    printf "\033[1;32m🌿%s%s\033[0m " "$git_branch" "$git_status"
fi

# Service status with visual indicators
printf "| DB:%s MCP:%s BE:%s FE:%s " "$databricks_status" "$mcp_status" "$backend_status" "$frontend_status"

# Active processes
if [ -n "$testing_status" ]; then
    printf "%s " "$testing_status"
fi

# Conversation context (if meaningful)
if [ "$message_count" -gt 0 ] && [ "$message_count" -le 50 ]; then
    printf "\033[2m💬%s\033[0m " "$message_count"
fi

# Session metrics: tokens, cost, and duration
session_metrics=""
if [ "$total_tokens" -gt 0 ]; then
    session_metrics="🧮${formatted_tokens}"
    # Add cost if available
    if [ -n "$estimated_cost" ]; then
        session_metrics="${session_metrics} 💰${estimated_cost}"
    fi
fi
if [ -n "$session_duration" ]; then
    if [ -n "$session_metrics" ]; then
        session_metrics="${session_metrics} ⏱️${session_duration}"
    else
        session_metrics="⏱️${session_duration}"
    fi
fi
if [ -n "$session_metrics" ]; then
    printf "\033[2m%s\033[0m " "$session_metrics"
fi

# Compact system info
printf "\033[2m@%s %s\033[0m" "$hostname" "$current_time"

# Second line: Last prompt text (if available and meaningful)
if [ -n "$last_prompt_text" ] && [ "$last_prompt_text" != "null" ] && [ ${#last_prompt_text} -gt 5 ]; then
    printf "\n\033[2m💭 %s\033[0m" "$last_prompt_text"
    # Add ellipsis if text was truncated
    if [ ${#last_prompt_text} -eq 100 ]; then
        printf "..."
    fi
fi

# Always end with a newline
printf "\n"