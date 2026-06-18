"""Tests for orchestrator dry_run mode."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from src.orchestrator import HorizonOrchestrator
from src.ai.dry_run import DryRunAIClient


def _make_config():
    """Minimal Config stub for orchestrator instantiation."""
    from src.models import (
        Config, AIConfig, AIProvider, SourcesConfig, FilteringConfig,
        HackerNewsConfig, RedditConfig, TelegramConfig,
    )
    ai = AIConfig(provider=AIProvider.OPENAI, model="gpt-4o", api_key_env="OPENAI_API_KEY")
    sources = SourcesConfig(
        hackernews=HackerNewsConfig(enabled=False),
        reddit=RedditConfig(enabled=False),
        telegram=TelegramConfig(enabled=False),
    )
    filtering = FilteringConfig(ai_score_threshold=7.0, time_window_hours=24)
    return Config(ai=ai, sources=sources, filtering=filtering)


def _make_storage(tmp_path):
    from src.storage.manager import StorageManager
    storage = StorageManager(data_dir=str(tmp_path / "data"))
    (tmp_path / "data" / "summaries").mkdir(parents=True, exist_ok=True)
    return storage


def test_dry_run_uses_dry_run_client(tmp_path):
    config = _make_config()
    storage = _make_storage(tmp_path)
    orch = HorizonOrchestrator(config, storage, dry_run=True)
    client = orch._make_ai_client()
    assert isinstance(client, DryRunAIClient)


def test_normal_run_uses_real_client(tmp_path):
    config = _make_config()
    storage = _make_storage(tmp_path)
    orch = HorizonOrchestrator(config, storage, dry_run=False)
    from src.ai.client import AIClient
    import os
    os.environ.setdefault("OPENAI_API_KEY", "test-key-placeholder")
    client = orch._make_ai_client()
    assert not isinstance(client, DryRunAIClient)
    assert isinstance(client, AIClient)
