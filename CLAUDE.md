# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is a demonstration repository for Claude Code, primarily showcasing hook configuration and workspace setup. The repository is currently minimal with no production code.

## Hook Configuration

This repository has custom hooks configured in `.claude/settings.json` that provide audio feedback (macOS):

- **Stop Hook**: Announces "Se ha terminado el trabajo" (Work has finished) when Claude Code stops
- **SubagentStop Hook**: Announces "El subagente ha terminado su tarea" (The subagent has finished its task) when a subagent completes
- **Notification Hook**: Uses `.claude/hooks/on-notification-say.sh` to speak notification messages using the Kate voice

### Hook Script Details

The notification hook script (`.claude/hooks/on-notification-say.sh`):
- Reads JSON payload from stdin
- Extracts the message field using `jq`
- Uses macOS `say` command with Kate voice to announce the message
- Requires `jq` to be installed on the system

## Development Environment

- **Platform**: macOS (Darwin-based)
- **Git**: Repository initialized with main branch
- **Dependencies**: `jq` (required for notification hook)
