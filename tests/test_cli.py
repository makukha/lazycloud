from click.testing import CliRunner

from lazycloud.cli import cli


def test_help():
    runner = CliRunner()
    result = runner.invoke(cli, ['--help'])
    assert result.exit_code == 0
    assert result.output.strip().startswith('Usage: ')
