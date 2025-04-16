import click
import collections
import vinery.cli.commands as cmd
from vinery.cli.options import option_path_to_library
from vinery.io import LOG_LEVELS, set_log_level, echo


class OrderedGroup(click.Group):
    def __init__(self, name=None, commands=None, **attrs):
        super().__init__(name, **attrs)
        # Use an OrderedDict to keep the commands in the preferred order
        self.commands = collections.OrderedDict([
            ("version", cmd.version),
            ("fmt", cmd.fmt),
            ("init", cmd.init),
            ("validate", cmd.validate),
            ("plan", cmd.plan),
            ("apply", cmd.apply),
            ("destroy", cmd.destroy)
        ])

    def list_commands(self, ctx):
        return self.commands.keys()  # Use the keys for listing the commands in order


def callback_log_level(ctx, param, value):
    try:
        set_log_level(value)
        echo(f"--log-level: {value}", log_level="DEBUG")
    except ValueError as e:
        echo(str(e), log_level="ERROR")
        ctx.exit(1)
        
    return value


@click.group(cls=OrderedGroup)
@click.option(
    '--log-level', '-l', '-log-level',
    callback=callback_log_level,
    default="INFO",
    envvar="VINE_LOG_LEVEL",
    help=f"""
    Set the global log level for the CLI.
    Can be overridden by setting the VINE_LOG_LEVEL environment variable.
    
    Accepted values: {LOG_LEVELS}
    """,
    show_default=True
)
@option_path_to_library
@click.pass_context
def cli(ctx, log_level: str, path_to_library: str):
    """
    Manage infrastructure plans.
    """
    pass
