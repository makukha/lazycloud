import asyncio
from functools import wraps
from typing import Callable, ParamSpec, TypeVar

import rich_click as click
from caseutil import to_kebab, to_lower
from rich.progress import Progress

from .tag_manager import AwsTagManager, ResourceType

P = ParamSpec('P')
R = TypeVar('R')


@click.group()
def cli() -> None:
    """
    Manage Amazon Web Services resources.
    """


def resource_type_options(f: Callable[P, R]) -> Callable[P, R]:
    cmd = f
    for rt in ResourceType:
        cmd = click.option(
            f'--{to_kebab(rt)}',
            help=f'Load "{to_lower(rt)}" resources.',
            is_flag=True,
            default=False,
        )(cmd)
    return wraps(f)(cmd)


@cli.command()
@click.option(
    '-t',
    '--tag',
    required=True,
    help='Tag "key=value" pair.',
)
@click.option(
    '-u',
    '--unset',
    help='When unchecked, set tag to this value instead of removing.',
)
@resource_type_options
def tag(
    tag: str,
    unset: str | None,
    **resource_type_flags: bool,
) -> None:
    """
    Edit tags for AWS resources.
    """
    key, value = tag.rsplit('=')
    resource_types = {ResourceType(k) for k, v in resource_type_flags.items() if v}
    manager = AwsTagManager(resource_types)

    with Progress(transient=True) as progress:
        progress.add_task('Loading...', total=None)
        asyncio.run(manager.load())

    if not manager.resources:
        click.echo('No resources found.')
        raise SystemExit(0)

    changes = manager.edit_tag(
        message=f'Which resources will be tagged with {key}={value}?',
        key=key,
        value_checked=value,
        value_unchecked=unset,
    )

    with Progress(transient=True) as progress:
        progress.add_task('Updating...', total=None)
        asyncio.run(manager.apply(changes))
