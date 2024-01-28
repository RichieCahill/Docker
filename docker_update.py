"""test"""
import argparse
import logging
import re
from os import environ
from pathlib import Path
from subprocess import run


def create_env_file(env_var_data: dict[str, str], env_path: Path) -> None:
    """Creates an env file from a dict

    Args:
        env_var_data (dict[str, str]): dict of env vars
        env_path (Path): path to env file
    """
    logging.info(f"Creating env file at path: {env_path}")

    env_vars = "\n".join([f"{key}={value}" for key, value in env_var_data.items()])

    logging.debug(f"{env_vars=}")

    env_path.write_text(data=f"{env_vars}\n", encoding="utf-8")


def run_command(command: str) -> tuple[str, int]:
    """Runs a command and returns the output and return code

    Args:
        command (str): command to run

    Returns:
        tuple[str, int]: output and return code
    """
    proses = run(command.split(), capture_output=True, text=True, check=False)  # noqa: S603 input is trusted
    return proses.stdout, proses.returncode


def docker_compose_up(path: str) -> None:
    """Runs docker compose up

    Args:
        path (str): path to docker compose file
    """
    logging.info(f"Running docker compose up with path: {path}")

    output, returncode = run_command(f"docker compose -f {path} up --force-recreate --build -d")
    logging.debug(f"docker compose up output: {output} returncode: {returncode} returncode: {returncode}")

    if returncode != 0:
        error = f"docker compose up failed with return code: {returncode} and output: {output}"
        raise ValueError(error)

    logging.info("docker compose succeeded")


def check_zfs(pool_name: str, data_set_name: str) -> None:
    """Checks if a zfs data set is up

    Args:
        pool_name (str): zfs pool name
        data_set_name (str): zfs data set name
    """
    logging.info(f"Checking if ZFS-{pool_name}-{data_set_name} is up")

    output, returncode = run_command(f"systemctl status ZFS-{pool_name}-{data_set_name}.mount")
    logging.debug(f"systemctl status ZFS-{pool_name}-{data_set_name}.mount output: {output} returncode: {returncode}")

    if not re.compile(r"active \(mounted\)").search(output):
        error = f"ZFS-{pool_name}-{data_set_name} is not up with output: {output}"
        raise ValueError(error)

    if returncode != 0:
        error = f"systemctl status ZFS-{pool_name}-{data_set_name}.mount had returncode {returncode}: {output}"
        raise ValueError(error)

    logging.info(f"ZFS-{pool_name}-{data_set_name} is up")


def jeeves_jr_update() -> None:
    """Updates jeeves jr"""
    check_zfs(pool_name="Main", data_set_name="Docker")

    create_env_file(
        env_var_data={"TUNNEL_TOKEN": environ["TUNNEL_TOKEN"]},
        env_path=Path("/ZFS/Main/Docker/Docker/jeeves-jr/cloudflare_tunnel.env"),
    )

    docker_compose_up(path="./jeeves-jr/docker-compose.yml")



def main() -> None:
    """Main"""
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[logging.FileHandler("debug.log"), logging.StreamHandler()],
    )

    logging.info("Starting docker update")

    # TODO(Richie): argparser for machine name
    jeeves_jr_update()

    logging.info("docker update succeeded")


if __name__ == "__main__":
    main()
