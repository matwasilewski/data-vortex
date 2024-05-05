from pathlib import Path

import pytest
from data_vortex_dagster.resources import ExternalResourceOnFs


def test_external_resource_on_fs_without_partitions(
    dagster_resources_root: Path,
) -> None:
    path = str(dagster_resources_root)
    resource = ExternalResourceOnFs(base_dir=path)
    assert resource.base_dir == path

    files_as_bytes = resource.read("rightmove_backfill_no_partition")
    assert len(files_as_bytes) == 4


def test_external_resource_on_fs_with_dir(
    dagster_resources_root: Path,
) -> None:
    path = str(dagster_resources_root)
    resource = ExternalResourceOnFs(base_dir=path)
    assert resource.base_dir == path

    with pytest.raises(FileNotFoundError):
        resource.read("nonexistent_dir_for_resources_test")


def test_external_resource_on_fs_with_partitions(
    dagster_resources_root: Path,
) -> None:
    path = str(dagster_resources_root)
    resource = ExternalResourceOnFs(base_dir=path)
    assert resource.base_dir == path

    file_as_bytes = resource.read(
        "rightmove_backfill_partitions", "partition_two"
    )
    assert len(file_as_bytes) == 2

    files_with_meta = resource.read(
        "rightmove_backfill_partitions", "partition_two"
    )
    assert len(files_with_meta) == 2
