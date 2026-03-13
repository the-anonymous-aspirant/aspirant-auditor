"""Tests for CLI invocation."""

from click.testing import CliRunner

from app.main import cli


def test_cli_help():
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "aspirant-auditor" in result.output


def test_scan_help():
    runner = CliRunner()
    result = runner.invoke(cli, ["scan", "--help"])
    assert result.exit_code == 0
    assert "PATH" in result.output


def test_scan_all_help():
    runner = CliRunner()
    result = runner.invoke(cli, ["scan-all", "--help"])
    assert result.exit_code == 0


def test_scan_deploy_help():
    runner = CliRunner()
    result = runner.invoke(cli, ["scan-deploy", "--help"])
    assert result.exit_code == 0


def test_version():
    runner = CliRunner()
    result = runner.invoke(cli, ["--version"])
    assert result.exit_code == 0
    assert "1.0.0" in result.output


def test_scan_repo(tmp_repo):
    runner = CliRunner()
    result = runner.invoke(cli, ["scan", str(tmp_repo)])
    assert "aspirant-test" in result.output


def test_scan_json(tmp_repo):
    runner = CliRunner()
    result = runner.invoke(cli, ["scan", str(tmp_repo), "--format", "json"])
    import json
    data = json.loads(result.output)
    assert "aspirant-test" in data


def test_scan_nonexistent():
    runner = CliRunner()
    result = runner.invoke(cli, ["scan", "/nonexistent/path"])
    assert result.exit_code != 0
