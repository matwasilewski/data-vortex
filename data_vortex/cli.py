import click

from data_vortex.rightmove_query import get_new_listings


@click.group()
def cli():
    """Rental Properties CLI"""
    pass


@click.command()
def get_new_properties():
    """
    Fetch and display rental properties starting from the specified index.
    """
    get_new_listings()


cli.add_command(get_new_properties)

if __name__ == "__main__":
    cli()
