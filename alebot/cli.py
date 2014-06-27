import click
from . import Alebot


@click.command()
@click.option("--path", default=".",
              help="Path in which confi.json and plugins are.")
def run(path):
    alebot = Alebot(path)
    alebot.connect()
