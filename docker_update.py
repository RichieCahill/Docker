"""test"""
import logging
from os import getenv
from pathlib import Path
from subprocess import run


def create_env_file() -> None:
    """Create env file"""
    env_path = Path("./cloudflare_tunnel.env")

    env_path.write_text(
        data=f"TUNNEL_TOKEN={getenv('JEEVES_JR_TUNNEL_TOKEN')}",
        encoding="utf-8",
    )


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

    create_env_file()

    # TODO(Richie): if zfs is up

    # TODO(Richie): argparser for machine name

    # docker_compose_up()


if __name__ == "__main__":
    main()
