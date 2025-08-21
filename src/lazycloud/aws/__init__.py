import asyncio
import json

import rich_click as click
from rich.progress import Progress
from aws_arn import parse_arn

from .tag import AwsTagManager, ResourceType


@click.group()
def cli() -> None:
    """
    Manage tags for Amazon Web Services resources.
    """


@cli.command()
@click.option(
    '-r', '--resource',
    required=True,
    type=click.Choice(ResourceType, case_sensitive=False),
    help='Resource type.',
)
@click.option(
    '-t', '--tag',
    required=True,
    help='Tag "key=value" pair.',
)
@click.option(
    '-u', '--unselected-value',
    help='Set value when tag is unselected; tag key is removed by default.',
)
def tag(
    resource: ResourceType,
    tag: str,
    unselected_value: str | None,
) -> None:
    """
    Edit tags for AWS resources.
    """
    key, value = tag.rsplit('=')
    manager = AwsTagManager(resource)

    with Progress(transient=True) as progress:
        progress.add_task('Loading...', total=None)
        asyncio.run(manager.load())

    changes = manager.edit_tag_selection(
        message={
            ResourceType.IAM_USER:
                f'Which IAM users will be tagged with {key}={value}?',
        }[resource],
        key=key,
        value=value,
        unselected_value=unselected_value,
    )

    with Progress(transient=True) as progress:
        progress.add_task('Updating...', total=None)
        asyncio.run(manager.apply(changes))


@cli.command()
@click.option(
    '-a', '--arn',
    required=True,
    help='Resource ARN.',
)
@click.option(
    '--json-schema',
    help='JSON Schema string if resource value is in JSON format.',
)
@click.option(
    '--json-schema-file',
    type=click.Path(exists=True, dir_okay=False),
    help='Path to JSON Schema file.',
)
def edit(
    arn: str,
    json_schema: str | None,
    json_schema_file: str | None,
) -> None:
    """
    Edit AWS resources.
    """
    raise NotImplementedError
