"""CLI entry point — registers all remo commands."""

import click
from remo import __version__
from remo.commands.startup import show_startup
from remo.commands.init import init
from remo.commands.remind import remind
from remo.commands.check import check
from remo.commands.log import log
from remo.commands.run import run, shortcuts
from remo.commands.snooze import snooze
from remo.commands.status import status


@click.group(invoke_without_command=True)
@click.version_option(version=__version__, prog_name="remo")
@click.pass_context
def main(ctx: click.Context) -> None:
    """remo — Project-aware terminal companion for developers.

    Run without arguments to show the startup panel for the current project.
    """
    if ctx.invoked_subcommand is None:
        show_startup()


main.add_command(init)
main.add_command(remind)
main.add_command(check)
main.add_command(log)
main.add_command(run)
main.add_command(shortcuts)
main.add_command(snooze)
main.add_command(status)
