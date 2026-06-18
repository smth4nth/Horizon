"""Tests for DryRunAIClient."""

import json
import pytest
from src.ai.dry_run import DryRunAIClient


@pytest.fixture
def client():
    return DryRunAIClient()


@pytest.mark.asyncio
async def test_analysis_default_returns_score_8(client):
    result = await client.complete(
        system="You are an expert content curator",
        user="Title: My Cool Article\nSource: hackernews\nAuthor: alice\nURL: https://example.com\n",
    )
    data = json.loads(result)
    assert data["score"] == 8.0
    assert data["reason"] == "[dry-run]"
    assert data["summary"] == "My Cool Article"
    assert data["tags"] == ["dry-run"]


@pytest.mark.asyncio
async def test_dedup_returns_empty(client):
    result = await client.complete(
        system="You are a news deduplication assistant.",
        user="[0] Article A\n[1] Article B",
    )
    data = json.loads(result)
    assert data == {"duplicates": []}


@pytest.mark.asyncio
async def test_concept_extraction_returns_empty(client):
    result = await client.complete(
        system="You identify technical concepts in news",
        user="Title: Foo\nSummary: bar\nTags: baz\nContent: qux",
    )
    data = json.loads(result)
    assert data == {"queries": []}


@pytest.mark.asyncio
async def test_enrichment_returns_bilingual_fields(client):
    result = await client.complete(
        system="You are a knowledgeable technical writer who helps readers",
        user="Title: Rust 2.0 Released\nURL: https://rust-lang.org\nSummary: Major release.\n",
    )
    data = json.loads(result)
    assert "title_en" in data
    assert "title_zh" in data
    assert "whats_new_en" in data
    assert "whats_new_zh" in data
    assert data["sources"] == []


@pytest.mark.asyncio
async def test_translation_returns_zh_fields(client):
    result = await client.complete(
        system="You are a translator. Translate to Simplified Chinese.",
        user="Title: Hello World\nSummary: A simple program.\n",
    )
    data = json.loads(result)
    assert "title_zh" in data
    assert "summary_zh" in data


@pytest.mark.asyncio
async def test_title_extracted_from_user_prompt(client):
    result = await client.complete(
        system="You are an expert content curator",
        user="Title: OpenAI Releases GPT-5\nSource: twitter\nAuthor: sam\nURL: https://x.com/1\n",
    )
    data = json.loads(result)
    assert data["summary"] == "OpenAI Releases GPT-5"
