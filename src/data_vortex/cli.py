from itertools import product

import click

from src.data_vortex.rightmove_models import RightmoveRentParams
from src.data_vortex.rightmove_query import get_new_listings


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
        min_bedrooms = str(beds) if beds is not None else None
        max_bedrooms = min_bedrooms

        if price is not None:
            if price >= 10000:
                price += 5 * price_increment
            elif price >= 5000:
                price += 2 * price_increment

        min_price = str(price) if price is not None else None
        max_price_str = (
            str(price + price_increment - 1)
            if price is not None
            else str(max_price)
        )

        params = RightmoveRentParams(
            minBedrooms=min_bedrooms,
            maxBedrooms=max_bedrooms,
            minPrice=min_price,
            maxPrice=max_price_str,
        )

        bedrooms_display = f"{beds if beds is not None else 'any'} bedrooms"
        price_range_display = f"£{price if price is not None else '0'} - £{max_price_str if price is not None else max_price if max_price is not None else 'any'}"

        click.echo(
            f"Fetching listings for {bedrooms_display} and price range {price_range_display}"
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
