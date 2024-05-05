from typing import List

from dagster import AssetExecutionContext, StaticPartitionsDefinition, asset

from src.data_vortex_dagster.resources import ExternalResource

KEY_PREFIX = "ingest_rightmove_backfill"
RIGHTMOVE_GROUP = "rightmove"
STATIC_PARTITIONS_DEF_RIGHTMOVE_BACKFILL = StaticPartitionsDefinition(
    [
        "partition_one",
    ]
)


@asset(
    key_prefix=KEY_PREFIX,
    group_name=RIGHTMOVE_GROUP,
    partitions_def=STATIC_PARTITIONS_DEF_RIGHTMOVE_BACKFILL,
)
def raw_rightmove(
    context: AssetExecutionContext,
    external_resource: ExternalResource,
) -> List[bytes]:
    return external_resource.read("source_rigthmove_backfill", context.partition_key)
