import json
import pickle
import subprocess


def unsafe_shell(command: str) -> None:
    # ruleid: secureflow.no-shell-true
    subprocess.run(command, shell=True, check=True)


def safe_process(arguments: list[str]) -> None:
    # ok: secureflow.no-shell-true
    subprocess.run(arguments, check=True)


def unsafe_deserialization(payload: bytes):
    # ruleid: secureflow.no-pickle-deserialization
    return pickle.loads(payload)


def safe_deserialization(payload: str):
    # ok: secureflow.no-pickle-deserialization
    return json.loads(payload)
