import datetime
import os
import tempfile
from pathlib import Path
from typing import Generator, Tuple

import pytest
from dagster import materialize
from pydantic_core import Url
from sqlalchemy import Column, Integer, MetaData, String, Table
from sqlalchemy.engine import Engine

from src.data_vortex.rightmove_models import (
    Currency,
    FurnishedStatus,
    Price,
    PriceUnit,
)
from src.data_vortex_dagster.assets.rightmove import (
    db_rightmove,
    parsed_rightmove,
    raw_rightmove,
)
from src.data_vortex_dagster.resources import DbResource, ExternalResourceOnFs


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


def test_rightmove_parse(dagster_resources_root: Path) -> None:
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
    assert listing_two.property_id == "142675904"
    assert listing_two.added_date == datetime.date(2023, 12, 4)
    assert (
        listing_two.description
        == "2 bedroom apartment for rent in Nottingham Place, London, W1U 5NB, UK, W1U for £4,400 pcm. Marketed by "
        "BLUEGROUND FURNISHED APARTMENTS UK LTD, London"
    )
    assert listing_two.furnished_status == FurnishedStatus.FURNISHED
    assert listing_two.image_url == Url(
        "https://media.rightmove.co.uk/79k/78429/142675904/78429_LON-429_IMG_08_0000.jpeg"
    )
    assert listing_two.price == Price(
        price=4400, currency=Currency.GBP, per=PriceUnit.PER_MONTH
    )
    assert listing_two.address == "Nottingham Place, London, W1U 5NB, UK"
    assert listing_two.postcode == "W1U 5NB"


@pytest.fixture()
def db_resource() -> Generator[Tuple[DbResource, Table, Engine], None, None]:
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


def test_rightmove_parse_empty(
    db_resource: Tuple[DbResource, Table, Engine],
) -> None:
    resource, test_table, engine = db_resource
    assets = [
        raw_rightmove,
        parsed_rightmove,
        db_rightmove,
    ]
    result = materialize(
        assets,
        resources={
            "db_resource": resource,
            "datastore_io_manager": resource.io_manager,
        },
        partition_key="partition_one",
    )

    assert result.success
    asset_val = result.asset_value(
        ["ingest_rightmove_backfill", "db_rightmove"]
    )
    assert len(asset_val) == 2
