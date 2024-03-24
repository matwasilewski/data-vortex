from itertools import product

import click

from data_vortex.rightmove_models import RightmoveRentParams
from data_vortex.rightmove_query import get_new_listings


@click.group()
def cli():
    """Rental Properties CLI"""
    pass


@click.command(
    help="Fetch and display rental properties starting from the specified index."
)
@click.option(
    "--continue_search",
    is_flag=True,
    default=False,
    help="Continue searching and saving new listings even "
    "if all current listings are already saved.",
)
@click.option(
    "--download_raw_listings",
    is_flag=True,
    default=False,
    help="Download raw HTML listings to the raw_data directory.",
)
@click.option(
    "--wait_time",
    default=0,
    type=float,
)
@click.option(
    "--min_bed", default=None, type=int, help="Minimum number of bedrooms."
)
@click.option(
    "--max_bed", default=None, type=int, help="Maximum number of bedrooms."
)
@click.option("--min_price", default=None, type=int, help="Minimum price.")
@click.option("--max_price", default=None, type=int, help="Maximum price.")
@click.option(
    "--price_increment",
    default=100,
    type=int,
    help="Increment for the price range if using price range search.",
)
def get_new_properties(
    continue_search,
    download_raw_listings,
    wait_time,
    min_bed,
    max_bed,
    min_price,
    max_price,
    price_increment,
):
    """
    Fetch and save new rental property listings for all combinations of bedroom numbers and price ranges.
    If a parameter is set to None, it will not restrict that particular filter in the search.
    """
    bed_range = (
        range(min_bed, max_bed + 1)
        if min_bed is not None and max_bed is not None
        else [None]
    )
    price_range = (
        range(min_price, max_price + 1, price_increment)
        if min_price is not None and max_price is not None
        else [None]
    )

    for beds, price in product(bed_range, price_range):
        params = RightmoveRentParams(
            include_shared_accommodation="false",
            minimum_bedrooms=str(beds) if beds is not None else None,
            maximum_bedrooms=str(max_bed) if beds is not None else None,
            minimum_price=str(price) if price is not None else None,
            maximum_price=str(price + price_increment - 1)
            if price is not None
            else str(max_price),
        )
        click.echo(
            f"Fetching listings for {beds if beds is not None else 'any'} bedrooms and price range £{price if price is not None else '0'} - £{price + price_increment - 1 if price is not None else max_price if max_price is not None else 'any'}"
        )
        click.echo(f"Params: {params.dict()}")
        get_new_listings(
            baseline_params=params,
            continue_search=continue_search,
            download_raw_listings=download_raw_listings,
            wait_time=wait_time,
        )


cli.add_command(get_new_properties)

if __name__ == "__main__":
    cli()
