import click
import os


TF_VARS = {
    'project': ("The name of the project.", "vine"),
}
OPTIONS_TF_VARS = {}


for name, (description, default) in TF_VARS.items():
    def _option_tf_var(function: callable):
        def callback(ctx, param, value):
            os.environ[f"TF_VAR_{name}"] = value
            return value
        
        return click.option(
            f'--{name}', f'-{name[0]}', f'-{name}',
            help=description,
            callback=callback,
            default=default,
            envvar=f"TF_VAR_{name}",
            required=True,
            show_default=True,
        )(function)
    
    OPTIONS_TF_VARS[name] = _option_tf_var


def options_tf_vars(function: callable):
    for option in OPTIONS_TF_VARS.values():
        function = option(function)
    return function
