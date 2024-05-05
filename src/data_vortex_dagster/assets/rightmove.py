from typing import List

from bs4 import BeautifulSoup
from dagster import AssetExecutionContext, StaticPartitionsDefinition, asset

from data_vortex.rightmove_processing import get_listings
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



@asset(
    key_prefix=KEY_PREFIX,
    group_name=RIGHTMOVE_GROUP,
    partitions_def=STATIC_PARTITIONS_DEF_RIGHTMOVE_BACKFILL,
)
def parsed_rightmove(
    context: AssetExecutionContext,
    raw_rightmove: List[bytes],
) -> List[bytes]:

    for listing_bytes in raw_rightmove:
        BeautifulSoup(listing_bytes, "xml")
        nested_listings = get_listings(listing_bytes)

    return []