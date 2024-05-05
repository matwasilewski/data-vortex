from pathlib import Path

from dagster import materialize

from src.data_vortex_dagster.assets.rightmove import raw_rightmove
from src.data_vortex_dagster.resources import ExternalResourceOnFs


def test_rightmove_raw_fs(dagster_resources_root: Path) -> None:
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

