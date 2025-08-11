# Product Requirements Document

## Overview

**MCP Guessing Game Server** - A minimal viable MCP server that exposes a single prompt-based slash command for a number guessing game.

### Problem Statement
We need to validate the FastAPI MCP integration pattern with the simplest possible implementation before building complex Databricks-integrated prompts.

### Solution
Create an ultra-simple MCP server that:
- Exposes one prompt file (`prompts/guess_number.md`) as a slash command
- Implements one FastAPI endpoint to handle the game logic
- Validates the end-to-end MCP architecture

## Target Users

**Primary User:** Developers testing MCP integration
**Use Case:** Validate that FastAPI can expose prompts as Claude Code slash commands

## Core Features  

### Single Feature: Number Guessing Game
- **Slash Command:** `/mcp__mcp-commands__guess_number`
- **Prompt File:** `prompts/guess_number.md` (static markdown file)
- **API Endpoint:** Single FastAPI endpoint that accepts a guess and returns response
- **Game Logic:** 
  - Server picks random number 1-100
  - User guesses via slash command
  - Server responds "higher", "lower", or "correct"
  - No state persistence (new game each request)

### Technical Scope
- **1 prompt file** in `prompts/` directory
- **1 FastAPI endpoint** for game logic  
- **0 external dependencies** beyond fastapi_mcp
- **0 Databricks integration** (future enhancement)

## Success Metrics

### MVP Success Criteria
- [ ] Prompt file is discovered and exposed as slash command
- [ ] Slash command executes and calls FastAPI endpoint
- [ ] Game logic works (higher/lower responses)
- [ ] MCP server connects to Claude Code successfully

### Implementation Success
- [ ] Code is deployed to Databricks Apps
- [ ] MCP server is accessible via network
- [ ] Claude Code can connect to MCP server
- [ ] User can play guessing game via `/mcp__mcp-commands__guess_number` command

## Implementation Priority

**Phase 1: Ultra-Simple MVP** (This Release)
1. Create `prompts/guess_number.md`
2. Add fastapi_mcp integration to existing FastAPI app
3. Implement single guessing game endpoint
4. Test MCP server connection locally
5. Deploy to Databricks Apps and test slash command

**Phase 2: Future Enhancements** (Later)
- Add Databricks SQL query prompts
- Add MLflow model interaction prompts  
- Add workspace file management prompts
- Support prompt arguments and parameters

## Technical Requirements

### Minimal Architecture
- **Framework:** Extend existing FastAPI app with `fastapi_mcp`
- **Prompts:** Single markdown file in `prompts/` directory
- **State:** Stateless (no persistence required)
- **Dependencies:** Add `fastapi_mcp` to existing `pyproject.toml`

### Acceptance Criteria
1. User types `/mcp__mcp-commands__guess_number` in Claude Code
2. Prompt is executed and calls our FastAPI endpoint
3. Server responds with game feedback
4. Integration validates MCP architecture works end-to-end