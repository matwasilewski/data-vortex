from typing import List

from dagster import asset, StaticPartitionsDefinition, AssetExecutionContext
from dagster._core.remote_representation.external import ExternalResource

KEY_PREFIX = "ingest_rightmove_backfill"
RIGHTMOVE_GROUP = "rightmove"
STATIC_PARTITIONS_DEF_RIGHTMOVE_BACKFILL = (
    StaticPartitionsDefinition(
        [
            "Pfizer_Backfile_2023_April_Main",
            "Pfizer_Backfile_2023_April_SpringerNature",
        ]
    ))


@asset(
    key_prefix=KEY_PREFIX,
    group_name=RIGHTMOVE_GROUP,
    partitions_def=STATIC_PARTITIONS_DEF_RIGHTMOVE_BACKFILL,
)
def raw_rightmove(
        context: AssetExecutionContext,
        external_resource: ExternalResource,
) -> List[bytes]:
    return external_resource.read("source_ccc", context.partition_key)


def raw_ccc(
        context: AssetExecutionContext,
        external_resource: ExternalResource,
) -> List[FileWithMetadata]:
    return external_resource.read("source_ccc", context.partition_key)
