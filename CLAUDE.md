# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

OpenArena is a Python project for generating high-quality datasets by having Language Models compete against each other. It uses an ELO rating system to rank LLMs based on their performance on various prompts, with evaluations done by a judge model.

## Development Commands

### Run the Arena
```bash
python llm_arena.py
```

### Install Dependencies
```bash
pip install -r requirements.txt
pip install datasets pyyaml  # Additional dependencies used but not in requirements.txt
```

## Architecture

### Core Components

1. **Model Classes** (llm_arena.py)
   - `Endpoint`: Manages API endpoints and authentication for different LLM providers
   - `Model`: Represents competing LLMs with ELO ratings and response caching
   - `JudgeModel`: Evaluates and scores responses from competing models
   - `ArenaLearning`: Orchestrates battles, manages ELO calculations, and generates training data

2. **Configuration System**
   - Uses `arena_config.yaml` for all configuration
   - Supports multiple endpoints (Ollama, OpenAI, custom)
   - Configurable models, judge, and datasets

3. **Battle Flow**
   - Loads prompts from Hugging Face datasets
   - Generates responses asynchronously in batches
   - Runs pairwise battles between all models
   - Updates ELO ratings after each batch
   - Outputs training data to `training_data.json`

### Key Implementation Details

- **Async Processing**: Uses `aiohttp` for concurrent API calls to multiple models
- **ELO System**: K-factor of 32, updates after each batch of battles
- **Batch Size**: Default 3 prompts per batch for memory efficiency
- **Response Caching**: Models cache responses per prompt to avoid duplicate API calls
- **Judge Evaluation Format**: Structured format requiring "Explanation:", "Score-A:", "Score-B:"

## Configuration Structure

The `arena_config.yaml` must include:
- `default_endpoint`: Default API endpoint for models
- `judge_model`: Configuration for the evaluation model
- `models`: List of competing models
- `datasets`: Hugging Face datasets to use for prompts

## Output Files

- `training_data.json`: Generated dataset with prompts and ranked model responses
- Console output includes ELO progression and final ratings