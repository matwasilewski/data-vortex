import click

from data_vortex.rightmove_query import get_new_listings


@click.group()
def cli():
    """Rental Properties CLI"""
    pass


@click.command(
    help="Fetch and display rental properties starting from the specified index."
)
@click.option('--continue_search', is_flag=True, default=False, help='Continue searching and saving new listings even '
                                                                     'if all current listings are already saved.')
def get_new_properties(continue_search: bool):
    """
    Fetch and save new rental property listings. If the --continue_search flag is set, the function
    will continue to fetch additional listings even if all current listings are already saved.
    """
    get_new_listings(continue_search=continue_search)


cli.add_command(get_new_properties)

if __name__ == "__main__":
    cli()
