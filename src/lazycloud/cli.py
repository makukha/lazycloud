import caseutil
import rich_click as click

try:
    from .aws import cli as aws_cli
except ImportError:
    aws_cli = None  # type: ignore[assignment]


@click.group()
@click.pass_context
def cli(ctx: click.Context) -> None:
    """
    Visual tag manager for cloud infrastructure.
    """

    ctx.token_normalize_func = caseutil.to_kebab


for name, cmd in {
    'aws': aws_cli,
}.items():
    if cmd is not None:
        cli.add_command(cmd, name)
