"""Agent loop tests with a mocked model: tools, citations, usage and vision."""

from __future__ import annotations

import base64
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

APP = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(APP))

from impedance_mcp import agent, attachments, config  # noqa: E402

try:
    from PIL import Image  # noqa: E402
except Exception:  # pragma: no cover
    Image = None


def fake_cfg():
    return {
        "llm": {
            "provider": "deepseek", "provider_name": "DeepSeek",
            "protocol": "openai", "api_style": "openai",
            "base_url": "https://api.deepseek.com",
            "model": "deepseek-flash", "api_key": "test-key",
            "temperature": 0.2, "max_tokens": 512,
            "model_profile": {},
        },
        "usage": {"auto_peak": False},
    }


class AgentTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.old_usage = config.USAGE_PATH
        self.old_upload = config.UPLOAD_DIR
        config.USAGE_PATH = self.root / "usage.jsonl"
        config.UPLOAD_DIR = self.root / "uploads"
        config.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    def tearDown(self):
        config.USAGE_PATH = self.old_usage
        config.UPLOAD_DIR = self.old_upload
        self.tmp.cleanup()

    def test_tool_loop_and_citations(self):
        calls = {"n": 0}

        def fake_chat(cfg, messages, tools=None, timeout=150):
            calls["n"] += 1
            if calls["n"] == 1:
                return {
                    "content": "",
                    "tool_calls": [{
                        "id": "call_1", "type": "function",
                        "function": {"name": "search_docs",
                                     "arguments": json.dumps({"query": "DeepSeek", "limit": 2})},
                    }],
                    "usage": {"prompt_tokens": 1000, "completion_tokens": 50,
                              "prompt_tokens_details": {"cached_tokens": 400}},
                    "model": "mock-model",
                }
            return {
                "content": "DeepSeek 的价格与能力见文档。",
                "tool_calls": [],
                "usage": {"prompt_tokens": 1200, "completion_tokens": 100},
                "model": "mock-model",
            }

        events = []
        with mock.patch.object(agent.llm, "chat", side_effect=fake_chat):
            result = agent.run_chat(
                fake_cfg(),
                [{"role": "user", "content": "DeepSeek 多少钱？"}],
                [], lambda event, data: events.append((event, data)),
            )
        names = [event for event, _ in events]
        self.assertIn("tool_call", names)
        self.assertIn("tool_result", names)
        self.assertIn("citation", names)
        self.assertIn("usage", names)
        self.assertIn("done", names)
        self.assertEqual(result["content"], "DeepSeek 的价格与能力见文档。")
        self.assertIn("search_docs", result["used_tools"])
        self.assertGreater(result["stats"]["total_cost"], 0)
        self.assertGreater(result["usage"]["prompt_tokens"], 2000)

    @unittest.skipIf(Image is None, "Pillow is not installed")
    def test_vision_message(self):
        image = Image.new("RGB", (32, 32), "white")
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        info = attachments.save_upload(
            "clip.png", base64.b64encode(buffer.getvalue()).decode())
        seen = []

        def fake_chat(cfg, messages, tools=None, timeout=150):
            seen.append(messages)
            return {"content": "已读取图片。", "tool_calls": [],
                    "usage": {"prompt_tokens": 100, "completion_tokens": 20},
                    "model": "mock-model"}

        with mock.patch.object(agent.llm, "chat", side_effect=fake_chat):
            agent.run_chat(
                fake_cfg(),
                [{"role": "user", "content": "看一下这张图"}],
                [{"id": info["id"], "name": info["name"]}],
                lambda event, data: None,
            )
        user_message = seen[0][-1]
        self.assertIsInstance(user_message["content"], list)
        self.assertTrue(any(block.get("type") == "image_url"
                            for block in user_message["content"]
                            if isinstance(block, dict)))


if __name__ == "__main__":
    unittest.main(verbosity=2)
