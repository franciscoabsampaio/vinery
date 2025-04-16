import click
import networkx
import subprocess
from vinery.cli.arguments import argument_plan
from vinery.cli.options import options_init, option_runner, option_auto_approve
from vinery.cli.options_tf_vars import options_tf_vars
from vinery.cli.setup import setup
from vinery.dependency_graph import DependencyGraph
from vinery.io import echo
import vinery.tf as tf
import vinery


def callback(ctx):
    tf.select_workspace(ctx.obj['workspace'], ctx.obj['runner'])

    # Create dependency graph
    ctx.ensure_object(dict)
    ctx.obj["graph"] = DependencyGraph().from_library(ctx.obj["path_to_library"])

    # Trim dependency graph up to target node plan
    # If no plan is provided, the entire graph is used
    plan = ctx.obj['plan']
    if plan:
        try:
            ctx.obj["graph"] = (
                ctx.obj["graph"].from_nodes_wsubgraph(plan)
            ) if ctx.obj["recursive"] else DependencyGraph().from_nodes(plan)
        except networkx.exception.NetworkXError:
            echo(f"Invalid plan(s) provided: {plan}", log_level="ERROR")
            ctx.exit(1)


########################
# version
@click.command()
def version():
    """
    Get the version of the CLI.
    """
    click.echo(vinery.__version__)


########################
# fmt
@click.command()
@option_runner
@click.pass_context
def fmt(ctx, runner: str):
    """
    Recursively format all infrastructure plans.
    """
    subprocess.run(args=[runner, "fmt", "-recursive"], cwd=ctx.obj["path_to_library"])


########################
# init
@click.command()
@argument_plan
@options_init
@click.pass_context
def init(ctx, plan: str, runner: str, recursive: bool, upgrade: bool, workspace: str):
    """
    Initialize the library and targeted plans.
    """
    setup(ctx, ctx.obj["path_to_library"])
    callback(ctx)
    tf.init(ctx.obj["graph"], ctx.obj["path_to_library"], runner, upgrade)


########################
# validate
@click.command()
@argument_plan
@options_init
@click.option(
    '--json', '-j', '-json',
    default=False,
    is_flag=True,
    help="""
    Pass -json flag to 'RUNNER plan'.
    Additionally, saves JSON output to a file.
    """
)
@click.pass_context
def validate(ctx, plan: str, runner: str, recursive: bool, upgrade: bool, workspace: str, json: bool):
    """
    Validate plans' syntax and correctness.
    By default, runs 'RUNNER init -upgrade' prior to execution.
    Plans that fail to 'init' are not validated.
    """
    callback(ctx)
    tf.validate(ctx.obj["graph"], ctx.obj["path_to_library"], runner, upgrade, json)


########################
# plan
@click.command()
@argument_plan
@options_init
@options_tf_vars
@click.pass_context
def plan(ctx, plan: str, runner: str, recursive: bool, upgrade: bool, workspace: str, project: str):
    """
    Execute a dry run of all infrastructure plans,
    showing what changes would be made.
    """
    callback(ctx)
    tf.plan(ctx.obj["graph"], ctx.obj["path_to_library"], runner, upgrade)


########################
# apply
@click.command()
@argument_plan
@options_init
@option_auto_approve
@options_tf_vars
@click.pass_context
def apply(ctx, plan: str, runner: str, recursive: bool, upgrade: bool, auto_approve: bool, workspace: str, project: str):
    """
    Apply the plans, building the infrastructure and applying any latent changes.
    """
    callback(ctx)
    tf.apply(ctx.obj["graph"], ctx.obj["path_to_library"], runner, upgrade, auto_approve)


########################
# destroy
@click.command()
@argument_plan
@options_init
@option_auto_approve
@options_tf_vars
@click.pass_context
def destroy(ctx, plan: str, runner: str, recursive: bool, upgrade: bool, auto_approve: bool, workspace: str, project: str):
    """
    Destroy all infrastructure described in the associated set of plans.
    """
    callback(ctx)
    tf.destroy(ctx.obj["graph"], ctx.obj["path_to_library"], runner, upgrade, auto_approve)
