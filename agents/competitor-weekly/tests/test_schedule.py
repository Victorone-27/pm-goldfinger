import importlib.util
import plistlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("schedule_manager", ROOT / "schedule" / "manage.py")
manager = importlib.util.module_from_spec(spec)
spec.loader.exec_module(manager)


def test_launch_agent_preserves_venv_path_and_contains_no_key(monkeypatch):
    monkeypatch.setenv("DEEPSEEK_API_KEY", "test-only-placeholder")
    root = Path("/tmp/项目 示例")
    python = str(root / ".venv/bin/python")
    definition = manager.definition(root, python, no_llm=True)
    content = plistlib.dumps(definition)
    decoded = plistlib.loads(content)
    assert decoded["ProgramArguments"] == [python, str(root / "run_weekly.py"), "--no-llm"]
    assert decoded["StartCalendarInterval"] == {"Weekday": 1, "Hour": 9, "Minute": 0}
    assert decoded["RunAtLoad"] is False
    assert b"test-only-placeholder" not in content and b"DEEPSEEK_API_KEY" not in content
