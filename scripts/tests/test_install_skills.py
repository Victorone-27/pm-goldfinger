import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
INSTALLER = REPO / "scripts/install_skills.sh"
SOURCE = REPO / "skills/plain-talk"
TEARDOWN = REPO / "skills/teardown"
REDESIGN = REPO / "skills/redesign"


def run(tmp_path, *args, answer=None):
    return subprocess.run(
        ["bash", str(INSTALLER), "--codex-dir", str(tmp_path / "Codex skills"),
         "--claude-dir", str(tmp_path / "Claude skills"), *args],
        input=answer, text=True, capture_output=True,
    )


def test_preview_and_cancel_do_not_write(tmp_path):
    preview = run(tmp_path, "--dry-run")
    assert preview.returncode == 0 and "plain-talk" in preview.stdout and "teardown" in preview.stdout
    assert "redesign" in preview.stdout and "跳过未完成" not in preview.stdout
    assert not list(tmp_path.iterdir())
    cancelled = run(tmp_path, answer="n\n")
    assert cancelled.returncode == 0 and "已取消" in cancelled.stdout
    assert not list(tmp_path.iterdir())


def test_install_is_repeatable_and_uninstall_preserves_source_and_unrelated_skill(tmp_path):
    original = (SOURCE / "SKILL.md").read_bytes()
    teardown_original = (TEARDOWN / "SKILL.md").read_bytes()
    redesign_original = (REDESIGN / "SKILL.md").read_bytes()
    installed = run(tmp_path, answer="y\n")
    assert installed.returncode == 0, installed.stderr
    for host in ("Codex skills", "Claude skills"):
        link = tmp_path / host / "plain-talk"
        assert link.is_symlink() and link.resolve() == SOURCE
        teardown_link = tmp_path / host / "teardown"
        assert teardown_link.is_symlink() and teardown_link.resolve() == TEARDOWN
        redesign_link = tmp_path / host / "redesign"
        assert redesign_link.is_symlink() and redesign_link.resolve() == REDESIGN
        (tmp_path / host / "other-skill").mkdir()
    assert run(tmp_path, "--yes").returncode == 0
    assert run(tmp_path, "--uninstall", "--yes").returncode == 0
    for host in ("Codex skills", "Claude skills"):
        assert not (tmp_path / host / "plain-talk").is_symlink()
        assert not (tmp_path / host / "teardown").is_symlink()
        assert not (tmp_path / host / "redesign").is_symlink()
        assert (tmp_path / host / "other-skill").is_dir()
    assert (SOURCE / "SKILL.md").read_bytes() == original
    assert (TEARDOWN / "SKILL.md").read_bytes() == teardown_original
    assert (REDESIGN / "SKILL.md").read_bytes() == redesign_original


def test_conflict_is_detected_before_any_other_target_is_changed(tmp_path):
    conflict = tmp_path / "Claude skills/plain-talk"
    conflict.mkdir(parents=True)
    (conflict / "user.txt").write_text("existing user data")
    result = run(tmp_path, "--yes")
    assert result.returncode == 1 and "不覆盖也不删除" in result.stderr
    assert not (tmp_path / "Codex skills").exists()
    assert (conflict / "user.txt").read_text() == "existing user data"
    assert run(tmp_path, "--uninstall", "--yes").returncode == 1
    assert (conflict / "user.txt").exists()


def test_foreign_or_broken_symlink_is_not_removed(tmp_path):
    root = tmp_path / "Codex skills"
    root.mkdir()
    target = tmp_path / "someone-elses-skill"
    (root / "plain-talk").symlink_to(target)
    result = run(tmp_path, "--target", "codex", "--uninstall", "--yes")
    assert result.returncode == 1
    assert (root / "plain-talk").is_symlink()


def test_target_and_skill_selection(tmp_path):
    result = run(tmp_path, "--target", "codex", "--skill", "plain-talk", "--yes")
    assert result.returncode == 0, result.stderr
    assert (tmp_path / "Codex skills/plain-talk").is_symlink()
    assert not (tmp_path / "Claude skills").exists()
    assert not (tmp_path / "Codex skills/teardown").exists()
    assert run(tmp_path, "--target", "codex", "--skill", "redesign", "--yes").returncode == 0
    assert (tmp_path / "Codex skills/redesign").resolve() == REDESIGN
    assert not (tmp_path / "Claude skills").exists()
    assert run(tmp_path, "--skill", "does-not-exist", "--yes").returncode == 1
