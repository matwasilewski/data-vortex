from pathlib import Path

from dagster import materialize

from src.data_vortex_dagster.assets.rightmove import raw_rightmove, parsed_rightmove
from src.data_vortex_dagster.resources import ExternalResourceOnFs


def test_rightmove_raw(dagster_resources_root: Path) -> None:
    test_resource = ExternalResourceOnFs(
        base_dir=str(dagster_resources_root)
    )
    assets = [raw_rightmove]
    result = materialize(
        assets,
        resources={
            "external_resource": test_resource,
        },
        partition_key="partition_one",
    )

    assert result.success
    asset_val = result.asset_value(["ingest_rightmove_backfill", "raw_rightmove"])
    assert len(asset_val) == 2


def test_rightmove_process(dagster_resources_root: Path) -> None:
    test_resource = ExternalResourceOnFs(
        base_dir=str(dagster_resources_root)
    )
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
    asset_val = result.asset_value(["ingest_rightmove_backfill", "raw_rightmove"])
    assert len(asset_val) == 2

    asset_val = result.asset_value(["ingest_rightmove_backfill", "parsed_rightmove"])
    assert len(asset_val) == 2

    listing_one = asset_val[0]
    listing_two = asset_val[1]
    assert listing_one[0].listing_id == 1

    assert listing_one.added_date == "2024-02-10"

