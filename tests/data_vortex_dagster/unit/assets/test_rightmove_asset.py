import datetime
from pathlib import Path

from dagster import materialize

from src.data_vortex_dagster.assets.rightmove import (
    parsed_rightmove,
    raw_rightmove,
)
from src.data_vortex_dagster.resources import ExternalResourceOnFs


def test_rightmove_raw(dagster_resources_root: Path) -> None:
    test_resource = ExternalResourceOnFs(base_dir=str(dagster_resources_root))
    assets = [raw_rightmove]
    result = materialize(
        assets,
        resources={
            "external_resource": test_resource,
        },
        partition_key="partition_one",
    )

    assert result.success
    asset_val = result.asset_value(
        ["ingest_rightmove_backfill", "raw_rightmove"]
    )
    assert len(asset_val) == 2


def test_rightmove_process(dagster_resources_root: Path) -> None:
    test_resource = ExternalResourceOnFs(base_dir=str(dagster_resources_root))
    assets = [
        raw_rightmove,
        parsed_rightmove,
    ]
    result = materialize(
        assets,
        resources={
            "external_resource": test_resource,
        },
        partition_key="partition_one",
    )

    assert result.success
    asset_val = result.asset_value(
        ["ingest_rightmove_backfill", "raw_rightmove"]
    )
    assert len(asset_val) == 2

    asset_val = result.asset_value(
        ["ingest_rightmove_backfill", "parsed_rightmove"]
    )
    assert len(asset_val) == 2

    listing_one = asset_val[0]
    assert listing_one.property_id == "130561805"
    assert listing_one.added_date == datetime.date(2023, 1, 10)
    assert listing_one.description == (
        "1 bedroom apartment for rent in Ufford Street, London, SE1 8FF, UK, SE1 for "
        "£4,000 pcm. Marketed by BLUEGROUND FURNISHED APARTMENTS UK LTD, London"
    )
    assert listing_one.price.price == 4000
    assert listing_one.address == "Ufford Street, London, SE1 8FF, UK"
    assert listing_one.postcode == "SE1 8FF"
    assert listing_one.image_url is not None

    listing_two = asset_val[1]
