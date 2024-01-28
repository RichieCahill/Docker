"""test"""
import argparse
import logging
from os import environ
from pathlib import Path
from subprocess import run


def create_env_file(env_var_data: dict[str, str], env_path: Path) -> None:
    """Creates an env file from a dict

    Args:
        env_var_data (dict[str, str]): dict of env vars
        env_path (Path): path to env file
    """
    env_vars = "\n".join([f"{key}={value}" for key, value in env_var_data.items()])

    env_path.write_text(data=env_vars, encoding="utf-8", newline="\n")


def run_command(command: str) -> tuple[str, int]:
    """Runs a command and returns the output and return code

    Args:
        command (str): command to run

    Returns:
        tuple[str, int]: output and return code
    """
    proses = run(command.split(), capture_output=True, text=True, check=False)  # noqa: S603 input is trusted
    return proses.stdout, proses.returncode


def docker_compose_up() -> None:
    """Docker compose up"""
    path = "./jeeves-jr/docker-compose.yml"
    output, returncode = run_command(f"docker compose -f {path} up --force-recreate --build -d")

    if returncode != 0:
        error = f"docker compose up failed with return code: {returncode} and output: {output}"
        raise ValueError(error)


def main() -> None:
    """Main"""
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[logging.FileHandler("debug.log"), logging.StreamHandler()],
    )

    create_env_file(
        env_var_data={"TUNNEL_TOKEN": environ["TUNNEL_TOKEN"]},
        env_path=Path("/ZFS/Main/Docker/Docker/cloudflare_tunnel.env"),
    )

    # TODO(Richie): if zfs is up

    # TODO(Richie): argparser for machine name

    # docker_compose_up()


if __name__ == "__main__":
    main()
