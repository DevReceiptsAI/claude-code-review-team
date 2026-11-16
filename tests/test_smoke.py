"""Smoke tests. No model calls, no plan usage."""
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "eval"))
import score  # noqa: E402

HOOK = ROOT / "demo-app" / ".claude" / "hooks" / "block-commit.sh"


def test_answer_key_matches_demo_app():
    key = score.load_key()
    assert len(key["bugs"]) == 10
    assert len(key["decoys"]) == 3
    for item in key["bugs"] + key["decoys"]:
        path = ROOT / "demo-app" / item["file"]
        assert path.exists(), item["id"]
        lines = path.read_text().splitlines()
        assert 1 <= item["start"] <= item["end"] <= len(lines), item["id"]
        window = "\n".join(lines[item["start"] - 1 : item["end"]])
        assert item["marker"] in window, f"{item['id']}: marker moved, update bugs.json"


def test_demo_app_tests_pass_as_shipped():
    r = subprocess.run([sys.executable, "-m", "pytest", "-q"], cwd=ROOT / "demo-app", capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr


def test_answer_key_not_inside_demo_app():
    assert not list((ROOT / "demo-app").rglob("bugs.json"))


def test_parse_findings_variants():
    text = (
        "FINDING: app/orders.py:13 | logic | high | off by one\n"
        "- **FINDING: `app/auth.py:14-15`** | injection\n"
        "not a finding line\n"
    )
    got = score.parse_findings(text)
    assert [(f, l) for f, l, _ in got] == [("app/orders.py", 13), ("app/auth.py", 14)]


def test_scoring_counts():
    text = "\n".join(
        [
            "FINDING: app/orders.py:13 | caught L1",
            "FINDING: app/orders.py:12 | duplicate of L1",
            "FINDING: demo-app/app/auth.py:14 | caught S1 (path prefix)",
            "FINDING: app/db.py:28 | decoy D1",
            "FINDING: app/auth.py:30 | unmatched",
        ]
    )
    res = score.score_text(text)
    assert res["caught"] == ["L1", "S1"]
    assert len(res["decoy_hits"]) == 1
    assert len(res["unmatched"]) == 1
    assert res["duplicates"] == 1


def test_run_stats_reads_cli_json_fields():
    data = {
        "duration_ms": 12_345,
        "total_cost_usd": 0.1,
        "num_turns": 4,
        "usage": {"input_tokens": 10, "output_tokens": 5, "cache_read_input_tokens": 100},
        "is_error": False,
    }
    stats = score.run_stats(data)
    assert stats["duration_s"] == 12.3
    assert stats["tokens_main_thread"] == 115


# ---- hook behaviour -------------------------------------------------------

def _run_hook(project_dir, command):
    assert shutil.which("jq"), "jq is required by the hook (brew install jq)"
    payload = json.dumps({"tool_name": "Bash", "tool_input": {"command": command}})
    env = {**os.environ, "CLAUDE_PROJECT_DIR": str(project_dir)}
    return subprocess.run([str(HOOK)], input=payload, env=env, capture_output=True, text=True)


@pytest.fixture
def failing_project(tmp_path):
    (tmp_path / "test_fail.py").write_text("def test_fail():\n    assert False\n")
    return tmp_path


@pytest.fixture
def passing_project(tmp_path):
    (tmp_path / "test_ok.py").write_text("def test_ok():\n    assert True\n")
    return tmp_path


def test_hook_is_executable():
    assert os.access(HOOK, os.X_OK)


def test_hook_ignores_other_commands_even_when_tests_fail(failing_project):
    for cmd in ["ls -la", "git status", "git log --oneline", 'echo "git commit"']:
        assert _run_hook(failing_project, cmd).returncode == 0, cmd


def test_hook_blocks_commit_when_tests_fail(failing_project):
    r = _run_hook(failing_project, 'git commit -m "wip"')
    assert r.returncode == 2
    assert "blocked" in r.stderr.lower()


def test_hook_blocks_chained_commit(failing_project):
    assert _run_hook(failing_project, "git add -A && git commit -m wip").returncode == 2


def test_hook_allows_commit_when_tests_pass(passing_project):
    assert _run_hook(passing_project, 'git commit -m "ok"').returncode == 0


@pytest.mark.parametrize("script", ["eval/run_eval.sh", "eval/hook_test.sh", "demo-app/.claude/hooks/block-commit.sh"])
def test_shell_scripts_parse(script):
    assert subprocess.run(["bash", "-n", str(ROOT / script)]).returncode == 0


def test_settings_json_valid_and_wires_hook():
    s = json.loads((ROOT / "demo-app/.claude/settings.json").read_text())
    cmd = s["hooks"]["PreToolUse"][0]["hooks"][0]["command"]
    assert cmd.endswith("block-commit.sh")


def test_no_secrets_or_api_keys_in_repo():
    for p in ROOT.rglob("*"):
        if p.is_file() and ".git/" not in str(p) and p.suffix in {".py", ".sh", ".md", ".json", ".example"}:
            assert ("sk-" + "ant-") not in p.read_text(errors="ignore"), p


# ---- starter-kit hook (wider matching, configurable test command) ----------

KIT_HOOK = ROOT / "starter-kit" / "hooks" / "block-commit.sh"


def _run_kit_hook(project_dir, command, test_cmd=None):
    payload = json.dumps({"tool_name": "Bash", "tool_input": {"command": command}})
    env = {**os.environ, "CLAUDE_PROJECT_DIR": str(project_dir), "TEST_CMD": test_cmd or f"{sys.executable} -m pytest -q"}
    return subprocess.run([str(KIT_HOOK)], input=payload, env=env, capture_output=True, text=True)


@pytest.mark.parametrize("cmd", [
    'git commit -m "wip"',
    "git add -A && git commit -m wip",
    "git -C subdir commit -m wip",
    "/usr/bin/git commit -m wip",
    'bash -c "git commit -m wip"',
    "cd x; git commit --amend",
])
def test_kit_hook_blocks_commit_spellings_when_tests_fail(failing_project, cmd):
    r = _run_kit_hook(failing_project, cmd)
    assert r.returncode == 2, cmd
    assert "blocked" in r.stderr.lower()


@pytest.mark.parametrize("cmd", ["ls -la", "git status", "git push origin main", 'echo "hello"', "git add . ; echo commit"])
def test_kit_hook_ignores_other_commands(failing_project, cmd):
    assert _run_kit_hook(failing_project, cmd).returncode == 0, cmd


def test_kit_hook_allows_commit_when_tests_pass(passing_project):
    assert _run_kit_hook(passing_project, 'git commit -m "ok"').returncode == 0


def test_kit_hook_uses_custom_test_command(passing_project):
    r = _run_kit_hook(passing_project, "git commit -m x", test_cmd="false")
    assert r.returncode == 2


def test_kit_hook_fails_closed_when_project_dir_missing(tmp_path):
    r = _run_kit_hook(tmp_path / "does-not-exist", "git commit -m x")
    assert r.returncode == 2
    assert "cannot enter" in r.stderr
