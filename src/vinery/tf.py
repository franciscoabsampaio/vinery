import os
import subprocess
from vinery.dependency_graph import DependencyGraph
from vinery.io import read_file, update_file, echo, read_deps_conf

SUPPORTED_RUNNERS=["terraform", "tofu"]


class RunnerNotFoundError(Exception):
    pass


def load_runners() -> list[str]:
    runners = [
        runner for runner in SUPPORTED_RUNNERS
        if subprocess.run(
            args=["which", runner],
            capture_output=True
        ).stdout.decode().strip()
    ]

    if not runners:
        raise RunnerNotFoundError("ERROR: No runner is installed.")
    
    return runners


def list_workspaces(runner: str) -> list[str]:
    output = subprocess.run(
        args=[runner, "workspace", "list"],
        check=True,
        capture_output=True,
    ).stdout.decode().replace("*", "")

    return [line.strip() for line in output.split("\n") if line]


def select_workspace(workspace: str, runner: str) -> int:
    list_of_existing_workspaces = list_workspaces(runner)
    cmd = "new" if workspace not in list_of_existing_workspaces else "select"
    try:
        subprocess.run(
            args=[runner, "workspace", cmd, workspace],
            check=True,
        )
        echo(f"Selected workspace '{workspace}'.", log_level="INFO")
        return 0
    
    except subprocess.CalledProcessError:
        echo(f"Failed to select workspace '{workspace}'.", log_level="ERROR")
        return 1


def option_var_files(path_to_library: str, path_to_plan: str) -> str:
    """
    Commands are executed from the `path_to_plan` directory.
    The global.tfvars file is located in the library directory.
    The {workspace}.tfvars file is located in the plan directory.
    The variables from parent plans are located in the respective directories.
    """
    path_from_plan_to_library_root = os.path.relpath(path_to_library, start=path_to_plan)

    # -var-files
    var_files = [f'-var-file="{path_from_plan_to_library_root}/global.tfvars"'] + [
        f'-var-file="{path_from_plan_to_library_root}/{dep}/output.json"'
        for dep in read_deps_conf(path_to_plan)
    ]
    # By checking if the file exists,
    # error handling is delegated to the runner,
    # which will fail if variables are missing.
    file_name_workspace_tfvars = f"{os.getenv('TF_VAR_workspace')}.tfvars"
    if os.path.exists(os.path.join(path_to_plan, file_name_workspace_tfvars)):
        var_files.append(f'-var-file="{file_name_workspace_tfvars}"')

    return ' '.join(var_files)


def tf(
    plan: str,
    runner: str,
    cmd: str,
    path_to_library: str,
    save_output: bool = False,
    skip_var_files: bool = False,
) -> int:
    cmd = f"{runner} {cmd}"
    echo(f"tf('{plan}', '{cmd}', '{path_to_library}', {save_output})", log_level="DEBUG")
    echo(f"Running command '{cmd}' for plan '{plan}'.", log_level="INFO")

    path_to_plan = os.path.join(path_to_library, plan)
    if not skip_var_files:
        cmd = ' '.join([
            cmd,
            option_var_files(path_to_library, path_to_plan),
            f"&& {runner} output -json | jq 'map_values(.value)' > output.json"
        ])

    try:
        output = subprocess.run(
            args=cmd,
            cwd=path_to_plan,
            check=True,
            capture_output=save_output,
            shell=True,
        )
        if save_output:
            update_file(
                f"{cmd.split(' ')[1]}_{plan.replace('/', '_')}.log",
                [output.stdout.decode()],
                dir='output'
            )
        echo(f"Command '{cmd}' for plan '{plan}' was successful!", log_level="SUCCESS")
        return 0
    
    except subprocess.CalledProcessError:
        echo(f"Command '{cmd}' failed for plan {plan}!", log_level="ERROR")
        return 1


def tf_loop(
    graph_of_plans_to_run: DependencyGraph,
    *args,
    reverse: bool = False,
    **kwargs
) -> DependencyGraph:
    set_of_plans_completed = set()

    for plan in graph_of_plans_to_run.sorted_list(reverse):
        exit_code = tf(plan, *args, **kwargs)
        if exit_code != 0:
            break
        else:
            set_of_plans_completed.add(plan)

    return graph_of_plans_to_run.wsubgraph(set_of_plans_completed)


def init(graph_of_plans, path_to_library, runner, upgrade) -> DependencyGraph:
    graph_of_plans_initialized = graph_of_plans.wsubgraph(
        read_file("init_status") if not upgrade else set()
    )
    graph_of_plans_to_initialize = graph_of_plans - graph_of_plans_initialized

    if not graph_of_plans_to_initialize:
        echo("No plans require initialization.", log_level="INFO")
        if not upgrade:
            echo("Did you mean to run -upgrade?", log_level="INFO")
        return graph_of_plans.wsubgraph(graph_of_plans_initialized.nodes)

    graph_of_plans_initialized += tf_loop(
        graph_of_plans_to_initialize,
        runner, f"init{' -upgrade' if upgrade else ''}", path_to_library,
    )

    update_file("init_status", graph_of_plans_initialized.nodes)

    return graph_of_plans_initialized


def with_tf_init(function):
    """
    Decorator that runs 'init' before the function.
    """
    def wrapper(graph_of_plans, path_to_library, runner, upgrade, *args, **kwargs):
        graph_of_plans_initialized = init(graph_of_plans, path_to_library, runner, upgrade=upgrade)
        return function(graph_of_plans_initialized, path_to_library, runner, *args, **kwargs)

    return wrapper


@with_tf_init
def validate(graph_of_plans_initialized, path_to_library, runner, json) -> DependencyGraph:
    return tf_loop(
        graph_of_plans_initialized,
        runner, f"validate{' -json' if json else ''}", path_to_library,
        save_output=json,
        skip_var_files=True
    )


@with_tf_init
def plan(graph_of_plans_initialized, path_to_library, runner) -> DependencyGraph:
    return tf_loop(
        graph_of_plans_initialized,
        runner,
        "plan",
        path_to_library,
    )


@with_tf_init
def apply(graph_of_plans_initialized, path_to_library, runner, auto_approve) -> DependencyGraph:
    return tf_loop(
        graph_of_plans_initialized,
        runner,
        f"apply{' -auto-approve' if auto_approve else ''}",
        path_to_library,
    )


@with_tf_init
def destroy(graph_of_plans_initialized, path_to_library, runner, auto_approve) -> DependencyGraph:
    return tf_loop(
        graph_of_plans_initialized,
        runner,
        f"destroy{' -auto-approve' if auto_approve else ''}",
        path_to_library,
        reverse=True,
        skip_var_files=True
    )
