import click
from vinery.io import echo


def argument_plan(function: callable):
    help_text = """
    PLAN: apply command to the PLAN dependency tree, including PLAN.
    Can take multiple plans as arguments.
    If no PLAN is provided, the entire dependency tree is used.
    """

    if function.__doc__:
        function.__doc__ += help_text
    else:
        function.__doc__ = help_text
    
    def callback(ctx, param, value):        
        plans_stripped = [plan.strip("/") for plan in value]
        if not all(plans_stripped):
            echo("Invalid plan provided. Plans must not be '/'.", log_level="ERROR")
            ctx.exit(1)
        
        echo(f"Plans provided: {plans_stripped}", log_level="DEBUG")
        ctx.ensure_object(dict)
        ctx.obj['plan'] = plans_stripped

        return plans_stripped
    
    return click.argument(
        'plan',
        callback=callback,
        nargs=-1  # Variadic argument
    )(function)
