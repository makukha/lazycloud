from asyncio import TaskGroup
from collections import defaultdict
from contextlib import AsyncExitStack
from dataclasses import dataclass
from enum import StrEnum

import questionary as q
from aiobotocore.session import get_session
from types_aiobotocore_iam import IAMClient


class ResourceType(StrEnum):
    IAM_ROLE = 'iam_role'
    IAM_USER = 'iam_user'

    @property
    def service(self) -> str:
        return self.split('_', 1)[0]


@dataclass
class Resource:
    type: ResourceType
    name: str
    arn: str
    tags: dict[str, str]


@dataclass
class TagChange:
    resource: Resource
    key: str
    value: str | None


class AwsTagManager:
    def __init__(self, resource_types: set[ResourceType]) -> None:
        self.resource_types = resource_types
        self.resources: dict[str, Resource] = {}
        self.session = get_session()

    async def load(self) -> None:
        self.resources.clear()
        # group resource types by service
        service_resource_types = defaultdict(list)
        for rt in self.resource_types:
            service_resource_types[rt.service].append(rt)
        # load for each service
        async with AsyncExitStack() as stack:
            async with TaskGroup() as tg:
                for service, resource_types in service_resource_types.items():
                    client = await stack.enter_async_context(
                        self.session.create_client(service)  # type: ignore[call-overload]
                    )
                    for rt in resource_types:
                        loader = getattr(self, f'load_{rt}s')
                        tg.create_task(loader(client, tg))

    async def load_iam_roles(self, client: IAMClient, tg: TaskGroup) -> None:
        async def load_tags(res: Resource) -> None:
            paginator = client.get_paginator('list_role_tags')
            async for resp in paginator.paginate(RoleName=res.name):
                res.tags.update({t['Key']: t['Value'] for t in resp['Tags']})

        async for resp in client.get_paginator('list_roles').paginate():
            resources = [
                Resource(
                    type=ResourceType.IAM_ROLE,
                    name=obj['RoleName'],
                    arn=obj['Arn'],
                    tags={},
                )
                for obj in resp['Roles']
            ]
            for res in resources:
                tg.create_task(load_tags(res))
            self.resources.update({res.name: res for res in resources})

    async def load_iam_users(self, client: IAMClient, tg: TaskGroup) -> None:
        async def load_tags(res: Resource) -> None:
            paginator = client.get_paginator('list_user_tags')
            async for resp in paginator.paginate(UserName=res.name):
                res.tags.update({t['Key']: t['Value'] for t in resp['Tags']})

        async for resp in client.get_paginator('list_users').paginate():
            resources = [
                Resource(
                    type=ResourceType.IAM_USER,
                    name=obj['UserName'],
                    arn=obj['Arn'],
                    tags={},
                )
                for obj in resp['Users']
            ]
            for res in resources:
                tg.create_task(load_tags(res))
            self.resources.update({res.name: res for res in resources})

    def edit_tag(
        self,
        message: str,
        key: str,
        value_checked: str,
        value_unchecked: str | None,
    ) -> list[TagChange]:
        choices = [
            q.Choice(title=r.name, value=r, checked=key in r.tags)
            for r in self.resources.values()
        ]
        checked = q.checkbox(message, choices).ask()
        ret: list[TagChange] = []
        for c in choices:
            if not c.checked and c.value in checked:
                ret.append(TagChange(c.value, key, value_checked))  # type: ignore[arg-type]
            elif c.checked and c.value not in checked:
                ret.append(TagChange(c.value, key, value_unchecked))  # type: ignore[arg-type]
        return ret

    async def apply(self, changes: list[TagChange]) -> None:
        # group additions by key and value
        addition = defaultdict(list)
        for c in changes:
            if c.value is not None:
                addition[c.key, c.value].append(c.resource.arn)
        # group removals by key
        removal = defaultdict(list)
        for c in changes:
            if c.value is None:
                removal[c.key].append(c.resource.arn)
        # apply to groups
        async with self.session.create_client('resourcegroupstaggingapi') as client:
            async with TaskGroup() as tg:
                for (k, v), arns in addition.items():
                    tg.create_task(
                        client.tag_resources(ResourceARNList=arns, Tags={k: v})
                    )
                for k, arns in removal.items():
                    tg.create_task(
                        client.untag_resources(ResourceARNList=arns, TagKeys=[k])
                    )
