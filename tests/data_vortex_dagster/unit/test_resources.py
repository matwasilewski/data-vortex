import os
import tempfile
from pathlib import Path

import pytest
from data_vortex_dagster.resources import DbResource, ExternalResourceOnFs
from sqlalchemy import Column, Integer, MetaData, String, Table


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


@pytest.fixture(scope="function")
def db_resource():
    db_file = tempfile.NamedTemporaryFile(delete=False)
    url = f"sqlite:///{db_file.name}"
    resource = DbResource(url=url)
    engine = resource.engine

    metadata = MetaData()
    test_table = Table(
        "test_table",
        metadata,
        Column("id", Integer, primary_key=True),
        Column("name", String),
    )

    metadata.create_all(engine)
    yield resource, test_table, engine

    engine.dispose()
    os.unlink(db_file.name)


def test_engine_initialization(db_resource) -> None:
    resource, test_table, engine = db_resource
    assert engine is not None
    assert engine.url.drivername.startswith("sqlite")


def test_session_creation_and_usage(db_resource):
    resource, test_table, engine = db_resource
    with resource.get_session() as session:
        session.execute(test_table.insert(), {"name": "Jane Doe"})
        session.commit()

        result = session.execute(test_table.select()).fetchall()
        assert len(result) == 1
        assert result[0]._asdict()["name"] == "Jane Doe"
