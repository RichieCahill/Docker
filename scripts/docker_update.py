"""test"""
import argparse
import logging
import re
from os import environ
from pathlib import Path
from subprocess import run


def create_env_file(env_var_data: str, env_path: Path) -> None:
    """Creates an env file from a dict

    Args:
        env_var_data (dict[str, str]): dict of env vars
        env_path (Path): path to env file
    """
    logging.info(f"Creating env file at path: {env_path}")

    logging.debug(f"{env_var_data=}")

    env_path.write_text(data=env_var_data, encoding="utf-8")


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

    # TODO check if file was updated
    output, returncode = run_command(f"docker compose -f {path} up --force-recreate --build -d")
    logging.debug(f"docker compose up output: {output} returncode: {returncode}")

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

    if not re.compile(r"active \(mounted\)").search(output):
        error = f"ZFS-{pool_name}-{data_set_name} is not up with output: {output} returncode: {returncode}"
        raise ValueError(error)

    logging.info(f"ZFS-{pool_name}-{data_set_name} is up")


def jeeves_jr_update() -> None:
    """Updates jeeves jr"""
    working_dir = "/ZFS/Main/Docker/jeeves-jr"

    check_zfs(pool_name="Main", data_set_name="Docker")

    create_env_file(
        env_var_data=f"TUNNEL_TOKEN={environ['TUNNEL_TOKEN']}\n",
        env_path=Path(working_dir) / "cloudflare_tunnel.env",
    )

    docker_compose_up(path=f"{working_dir}/docker-compose.yml")


def jeeves_update() -> None:
    """Updates jeeves jr"""
    working_dir = "/ZFS/Media/Docker/Docker/jeeves"

    pools_and_datasets = (
        ("Media", ("Docker", "DataBases-Influxdb", "DataBases-Postgres")),
        ("Storage", ("Main", "Plex")),
        ("Torenting", ("QbitVPN", "Qbit")),
    )

    for pool, datasets in pools_and_datasets:
        for dataset in datasets:
            check_zfs(pool_name=pool, data_set_name=dataset)

    create_env_file(
        env_path=Path(working_dir) / Path("postgres") / "postgres.env",
        env_var_data=(
            f"POSTGRES_USER={environ['POSTGRES_USER']}\n"
            f"POSTGRES_PASSWORD={environ['POSTGRES_PASSWORD']}\n"
            "POSTGRES_DB=primary\n"
            'POSTGRES_INITDB_ARGS="--auth-host=scram-sha-256"\n'
        ),
    )
    create_env_file(
        env_path=Path(working_dir) / Path("web") / "cloudflare_tunnel.env",
        env_var_data=f"TUNNEL_TOKEN={environ['TUNNEL_TOKEN']}\n",
    )
    create_env_file(
        env_path=Path(working_dir) / Path("internal") / "qbitvpn.env",
        env_var_data=(
            f"PUID=998\n"
            f"PGID=100\n"
            "VPN_ENABLED=yes\n"
            f"VPN_USER={environ['PIA_USERNAME']}\n"
            f"VPN_PASS={environ['PIA_PASSWORD']}\n"
            "VPN_PROV=pia\n"
            "VPN_CLIENT=openvpn\n"
            "STRICT_PORT_FORWARD=yes\n"
            "ENABLE_PRIVOXY=yes\n"
            f"LAN_NETWORK={environ['LAN_NETWORK']}/24\n"
            "NAME_SERVERS=1.1.1.1,8.8.8.8,8.8.4.4\n"
            "UMASK=000\n"
            "DEBUG=false\n"
            "DELUGE_DAEMON_LOG_LEVEL=debug\n"
            "DELUGE_WEB_LOG_LEVEL=debug\n"
        ),
    )

    compose_files = (
        "endlessh/docker-compose.yml",
        "freshrss/docker-compose.yml",
        "influxdb/docker-compose.yml",
        "internal/docker-compose.yml",
        "postgres/docker-compose.yml",
        "sccache/docker-compose.yml",
        "web/docker-compose.yml",
    )

    for compose_file in compose_files:
        docker_compose_up(path=f"{working_dir}/{compose_file}")


def main() -> None:
    """Main"""
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[logging.FileHandler("debug.log"), logging.StreamHandler()],
    )

    parser = argparse.ArgumentParser(description="Docker Update")
    parser.add_argument("--machine_name", help="Machine name", required=True, type=str)

    args = parser.parse_args()

    machine_name: str = args.machine_name

    logging.info(f"Starting docker update for {machine_name}")

    machine_jobs = {
        "jeeves-jr": jeeves_jr_update,
        "jeeves": jeeves_update,
    }

    machine_job = machine_jobs.get(machine_name)

    logging.debug(f"{machine_job=}")

    if machine_job is None:
        error = f"'{machine_name}' is invalid or not supported"
        raise ValueError(error)

    machine_job()

    logging.info(f"docker update succeeded for {machine_name}")


if __name__ == "__main__":
    main()
