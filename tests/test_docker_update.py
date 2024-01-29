"""Tests for the docker_update script."""

from os import environ
from pathlib import Path
from subprocess import CompletedProcess
from unittest.mock import patch

import pytest

from scripts.docker_update import check_zfs, create_env_file, docker_compose_up, jeeves_jr_update, main, run_command


def test_create_env_file(tmp_path: Path) -> None:
    """Test create_env_file"""
    env_var_data = {"VAR1": "value1", "VAR2": "value2", "VAR3": "value3"}
    env_path = tmp_path / "test.env"

    create_env_file(env_var_data, env_path)

    assert env_path.exists()
    assert env_path.read_text() == "VAR1=value1\nVAR2=value2\nVAR3=value3\n"


def test_run_command() -> None:
    """Test run_command"""
    with patch("scripts.docker_update.run") as mock_run:
        command = "ls -l"
        stdout = "output"
        returncode = 0
        mock_run.return_value = CompletedProcess(args=command.split(), stdout=stdout, returncode=returncode)

        output, code = run_command(command)

        assert output == stdout
        assert code == returncode


def test_docker_compose_up_success() -> None:
    """Test docker_compose_up when docker compose up succeeds"""
    path = "/path/to/docker-compose.yml"
    command = f"docker compose -f {path} up --force-recreate --build -d"
    output = "output"
    returncode = 0

    with (
        patch("scripts.docker_update.run_command") as mock_run_command,
        patch("scripts.docker_update.logging") as mock_logging,
    ):
        mock_run_command.return_value = (output, returncode)

        docker_compose_up(path)

        mock_run_command.assert_called_once_with(command)

        mock_logging.debug.assert_called_once_with(f"docker compose up output: {output} returncode: {returncode}")
        mock_logging.info.assert_called_with("docker compose succeeded")


def test_docker_compose_up_failure() -> None:
    """Test docker_compose_up when docker compose up fails"""
    path = "/path/to/docker-compose.yml"
    command = f"docker compose -f {path} up --force-recreate --build -d"
    output = "error output"
    returncode = 1

    with (
        patch("scripts.docker_update.run_command") as mock_run_command,
        patch("scripts.docker_update.logging") as mock_logging,
    ):
        mock_run_command.return_value = (output, returncode)

        with pytest.raises(ValueError, match="docker compose up failed with return code: 1 and output: error output"):
            docker_compose_up(path)

        mock_run_command.assert_called_once_with(command)
        mock_logging.info.assert_called_once_with(f"Running docker compose up with path: {path}")
        mock_logging.debug.assert_called_once_with(f"docker compose up output: {output} returncode: {returncode}")


def test_check_zfs_success() -> None:
    """Test check_zfs when ZFS data set is up"""
    pool_name = "my_pool"
    data_set_name = "my_data_set"
    command = f"systemctl status ZFS-{pool_name}-{data_set_name}.mount"
    output = "active (mounted)"
    returncode = 0

    with (
        patch("scripts.docker_update.run_command") as mock_run_command,
        patch("scripts.docker_update.logging") as mock_logging,
    ):
        mock_run_command.return_value = (output, returncode)

        check_zfs(pool_name, data_set_name)

        mock_run_command.assert_called_once_with(command)
        mock_logging.info.assert_called_with(f"ZFS-{pool_name}-{data_set_name} is up")


def test_check_zfs_failure_not_up() -> None:
    """Test check_zfs when ZFS data set is not up"""
    pool_name = "my_pool"
    data_set_name = "my_data_set"
    command = f"systemctl status ZFS-{pool_name}-{data_set_name}.mount"
    output = "inactive"
    returncode = 0

    with (
        patch("scripts.docker_update.run_command") as mock_run_command,
        patch("scripts.docker_update.logging") as mock_logging,
    ):
        mock_run_command.return_value = (output, returncode)

        with pytest.raises(ValueError, match=f"ZFS-{pool_name}-{data_set_name} is not up with output: {output}"):
            check_zfs(pool_name, data_set_name)

        mock_run_command.assert_called_once_with(command)
        mock_logging.info.assert_called_once_with(f"Checking if ZFS-{pool_name}-{data_set_name} is up")


def test_jeeves_jr_update_success() -> None:
    """Test jeeves_jr_update when all steps succeed"""
    with (
        patch("scripts.docker_update.check_zfs") as mock_check_zfs,
        patch("scripts.docker_update.create_env_file") as mock_create_env_file,
        patch("scripts.docker_update.docker_compose_up") as mock_docker_compose_up,
    ):
        environ["TUNNEL_TOKEN"] = "test_token"  # noqa: S105 fake token
        jeeves_jr_update()

        mock_check_zfs.assert_called_once_with(pool_name="Main", data_set_name="Docker")

        env_path = Path("/ZFS/Main/Docker/jeeves-jr/cloudflare_tunnel.env")
        env_var_data = {"TUNNEL_TOKEN": "test_token"}
        mock_create_env_file.assert_called_once_with(env_var_data=env_var_data, env_path=env_path)

        mock_docker_compose_up.assert_called_once_with(path="/ZFS/Main/Docker/jeeves-jr/docker-compose.yml")


def test_jeeves_jr_update_check_zfs_failure() -> None:
    """Test jeeves_jr_update when check_zfs fails"""
    with patch("scripts.docker_update.check_zfs") as mock_check_zfs:
        mock_check_zfs.side_effect = ValueError("ZFS data set is not up")

        with pytest.raises(ValueError, match="ZFS data set is not up"):
            jeeves_jr_update()

        mock_check_zfs.assert_called_once_with(pool_name="Main", data_set_name="Docker")


def test_jeeves_jr_update_create_env_file_failure() -> None:
    """Test jeeves_jr_update when create_env_file fails"""
    with (
        patch("scripts.docker_update.check_zfs"),
        patch("scripts.docker_update.create_env_file") as mock_create_env_file,
    ):
        environ["TUNNEL_TOKEN"] = "test_token"  # noqa: S105 fake token
        mock_create_env_file.side_effect = Exception("Failed to create env file")

        with pytest.raises(Exception, match="Failed to create env file"):
            jeeves_jr_update()

        mock_create_env_file.assert_called_once()


def test_jeeves_jr_update_docker_compose_up_failure() -> None:
    """Test jeeves_jr_update when docker_compose_up fails"""
    with (
        patch("scripts.docker_update.check_zfs"),
        patch("scripts.docker_update.create_env_file"),
        patch("scripts.docker_update.docker_compose_up") as mock_docker_compose_up,
    ):
        environ["TUNNEL_TOKEN"] = "test_token"  # noqa: S105 fake token

        mock_docker_compose_up.side_effect = ValueError("docker-compose up failed")

        with pytest.raises(ValueError, match="docker-compose up failed"):
            jeeves_jr_update()

        mock_docker_compose_up.assert_called_once()


def test_main_valid_machine_name() -> None:
    """Test main function with a valid machine name"""
    machine_name = "jeeves-jr"

    with (
        patch("scripts.docker_update.jeeves_jr_update") as mock_jeeves_jr_update,
        patch("sys.argv", ["main", "--machine_name", machine_name]),
        patch("scripts.docker_update.logging") as mock_logging,
    ):
        main()

        mock_jeeves_jr_update.assert_called_once()
        mock_logging.info.assert_called_with(f"docker update succeeded for {machine_name}")


def test_main_invalid_machine_name() -> None:
    """Test main function with an invalid machine name"""
    with (
        patch("sys.argv", ["main", "--machine_name", "monkey-d-luffy"]),
        pytest.raises(ValueError, match="'monkey-d-luffy' is invalid or not supported"),
    ):
        main()
