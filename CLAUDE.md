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

## WORKFLOW RULES
### Phase 1
- At the starting point of a feature on plan mode phase you MUST ALWAYS init a `.claude/sessions/context_session_{feature_name}.md` with yor first analisis
- You MUST ask to the subagents that you considered that have to be involved about the implementation and check their opinions, try always to run them on parallel if is posible
- After a plan mode phase you ALWAYS update the `.claude/sessions/context_session_{feature_name}.md` with the definition of the plan and the recomentations of the subagents
### Phase 2
- Before you do any work, MUST view files in `.claude/sessions/context_session_{feature_name}.md` file to get the full context (x being the id of the session we are operate)
- `.claude/sessions/context_session_{feature_name}.md` should contain most of context of what we did, overall plan, and sub agents will continusly add context to the file
- After you finish the each phase, MUST update the `.claude/sessions/context_session_{feature_name}.md` file to make sure others can get full context of what you did
- After you finish the work, MUST update the `.claude/sessions/context_session_{feature_name}.md` file to make sure others can get full context of what you did
### Phase 3
- After finish the final implementation MUST use qa-criteria-validator subagent to provide a report feedback an iterate over this feedback until acceptance criterias are passed
- After qa-criteria-validator finish, you MUST review their report and implement the feedback related with the feature

### SUBAGENTS MANAGEMENT
You have access to 8 subagents:
- shadcn-ui-architect: all task related to UI building & tweaking HAVE TO consult this agent
- qa-criteria-validator: all final client UI/UX implementations has to be validated by this subagent to provide feedback an iterate.
- ui-ux-analyzer: all the task related with UI review, improvements & tweaking HAVE TO consult this agent
- pydantic-ai-architect: all task related to ai agents using pydantic-ai framework & tweaking HAVE TO consult this agent
- frontend-developer: all task related to business logic in the client side before create the UI building & tweaking HAVE TO consult this agent
- frontend-test-engineer: all task related to business logic in the client side after implementation has to consult this agent to get the necesary test cases definitions
- backend-developer: all task related to business logic in the backend side HAVE TO consult this agent
- backend-test-engineer: all task related to business logic in the backned side after implementation has to consult this agent to get the necesary test cases definitions

Subagents will do research about the implementation and report feedback, but you will do the actual implementation;

When passing task to sub agent, make sure you pass the context file, e.g. `.claude/sessions/context_session_{feature_name}.md`.

After each sub agent finish the work, make sure you read the related documentation they created to get full context of the plan before you start executing
