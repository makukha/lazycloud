import asyncio
from collections import defaultdict
from dataclasses import dataclass
from enum import StrEnum

import boto3
import questionary as q


class ResourceType(StrEnum):
    IAM_USER = 'iam-user'

    def boto3_client(self) -> boto3.Session:
        match self:
            case 'iam-user':
                return boto3.client('iam')
            case _:
                raise AssertionError


@dataclass
class Resource:
    name: str
    arn: str
    tags: dict[str, str]


@dataclass
class Change:
    resource: Resource
    key: str
    value: str | None


class AwsTagManager:
    def __init__(self, resource: ResourceType) -> None:
        self.resource = resource
        self.client = self.resource.boto3_client()
        self.tag_client = boto3.client('resourcegroupstaggingapi')
        self.resources: dict[str, Resource] = {}

    async def load(self) -> None:
        self.resources.clear()
        match self.resource:
            case ResourceType.IAM_USER:
                await self._load_iam_users()
            case _:
                raise AssertionError

    async def _load_iam_users(self) -> None:
        # users
        resp = self.client.list_users()
        if resp['IsTruncated']:
            raise NotImplementedError  # todo
        for user in resp['Users']:
            name = user['UserName']
            self.resources[name] = Resource(name=name, arn=user['Arn'], tags={})
        # user tags
        async with asyncio.TaskGroup() as tg:
            for name in self.resources:
                tg.create_task(self._load_iam_user_tags(name))

    async def _load_iam_user_tags(self, name: str) -> None:
        resp = await asyncio.to_thread(
            self.client.list_user_tags,
            UserName=name,
        )
        if resp['IsTruncated']:
            raise NotImplementedError  # todo
        self.resources[name].tags = dict(
            (t['Key'], t['Value']) for t in resp['Tags']
        )

    def edit_tag_selection(
        self,
        message: str,
        key: str,
        value: str,
        unselected_value: str | None,
    ) -> list[Change]:
        choices = [
            q.Choice(title=r.name, value=r, checked=key in r.tags)
            for r in self.resources.values()
        ]
        checked = q.checkbox(message, choices).ask()
        ret: list[Change] = []
        for c in choices:
            if not c.checked and c.value in checked:
                ret.append(Change(c.value, key, value))
            elif c.checked and c.value not in checked:
                ret.append(Change(c.value, key, unselected_value))
        return ret

    async def apply(self, changes: list[Change]) -> None:
        # group changes by tag key and value
        group = defaultdict(list)
        for c in changes:
            if c.value is None:
                group[c.key, None].append(c)
            else:
                group[c.key, c.value].append(c)
        # run operations per group
        async with asyncio.TaskGroup() as tg:
            for (key, value), changes in group.items():
                arns = [c.resource.arn for c in changes]
                if value is None:
                    tg.create_task(self.remove_tag(arns, key))
                else:
                    tg.create_task(self.add_tag(arns, key, value))

    async def add_tag(self, arns: list[str], key: str, value: str) -> None:
        await asyncio.to_thread(
            self.tag_client.tag_resources,
            ResourceARNList=arns,
            Tags={key: value},
        )

    async def remove_tag(self, arns: list[str], key: str) -> None:
        await asyncio.to_thread(
            self.tag_client.untag_resources,
            ResourceARNList=arns,
            TagKeys=[key],
        )
