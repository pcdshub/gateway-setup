"""
Script to inspect and show the gateway configuration.
"""
from __future__ import annotations

from collections import defaultdict
import dataclasses
import pathlib
import prettytable
import subprocess


@dataclasses.dataclass(frozen=True, order=True)
class Gateway:
    """
    Information about one gateway. May be incomplete.
    """
    name: str
    pvlist: str | None
    launcher: str | None
    running_on: set[str]
    enabled_on: set[str]

    def combine_with(self, other: Gateway) -> Gateway:
        """
        Create a new Gateway info struct incorporating the new info.
        """
        if self.name != other.name:
            raise ValueError(
                "Can only combine gateways with matching names, "
                f"{self.name} != {other.name}"
            )
        return Gateway(
            name=self.name,
            pvlist=self.pvlist or other.pvlist,
            launcher=self.launcher or other.launcher,
            running_on=self.running_on.union(other.running_on),
            enabled_on=self.enabled_on.union(other.enabled_on),
        )


def combine_gatways(gateways: list[Gateway]) -> list[Gateway]:
    """
    Reduce a list of gateways by combining same-named gateways.

    This will create new gateways for combinations and use the
    same gateway object for gateways that do not get combined.
    """
    combined = []
    gws_by_name = defaultdict(list)
    for gw in gateways:
        gws_by_name[gw.name].append(gw)
    for gws in gws_by_name.values():
        if len(gws) == 1:
            combined.append(gws[0])
        else:
            this_combo = gws[0]
            for gw in gws[1:]:
                this_combo = this_combo.combine_with(gw)
            combined.append(this_combo)
    return combined


def get_configured_gateways(config_folder: str) -> list[Gateway]:
    """
    Get a list of gateways that have pvlist files.
    """
    configured_gateways = []
    for path in pathlib.Path(config_folder).glob("*.pvlist"):
        base_name = path.stem
        # First: the CA gateway
        configured_gateways.append(
            Gateway(
                name=base_name,
                pvlist=path.name,
                launcher=None,
                running_on=set(),
                enabled_on=set(),
            )
        )
        # Second: the PVA gateway
        configured_gateways.append(
            Gateway(
                name=f"pva-{base_name}",
                pvlist=path.name,
                launcher=None,
                running_on=set(),
                enabled_on=set(),
            )
        )
    return configured_gateways


def get_scripted_gateways(scripts_folder: str) -> list[Gateway]:
    """
    Get a list of gateways that have launcher scripts.
    """
    scripted_gateways = []
    # CA gateway scripts start with epicscagd- and have no file extension
    for path in pathlib.Path(scripts_folder).glob("epicscagd-*"):
        scripted_gateways.append(
            Gateway(
                name=path.stem.replace("epicscagd-", ""),
                pvlist=None,
                launcher=path.name,
                running_on=set(),
                enabled_on=set(),
            )
        )
    # PVA gateway scripts start with pvagw- and have a .sh file extension
    for path in pathlib.Path(scripts_folder).glob("pvagw-*.sh"):
        scripted_gateways.append(
            Gateway(
                name=path.stem.replace("pvagw-", "pva-"),
                pvlist=None,
                launcher=path.name,
                running_on=set(),
                enabled_on=set(),
            )
        )
    return scripted_gateways


def get_running_gateways(hostname: str) -> list[Gateway]:
    """
    Get a list of gateways that are running on a gateway host.
    """
    result = subprocess.run(
        ["ssh", hostname, "ps", "-C", "procServ", "-o", "command"],
        capture_output=True,
        check=True,
        universal_newlines=True,
    )
    gateways = []
    for num, line in enumerate(result.stdout.splitlines()):
        if "procServ" not in line:
            continue
        name = f"Unknown_line_{num}"
        pvlist = None
        tokens = line.split()
        for index, token in enumerate(tokens):
            if token == "--name":
                name = tokens[index + 1]
            if token == "-pvlist":
                pvlist = pathlib.Path(tokens[index + 1]).name
        gateways.append(
            Gateway(
                name=name,
                pvlist=pvlist,
                launcher=None,
                running_on={hostname},
                enabled_on=set(),
            )
        )
    return gateways


def get_enabled_gateways(hostname: str) -> list[Gateway]:
    """
    Get a list of gateways that are enabled for a gateway host.
    """
    result = subprocess.run(
        ["ssh", hostname, "systemctl", "list-unit-files"],
        capture_output=True,
        check=True,
        universal_newlines=True,
    )
    gateways = []
    for line in result.stdout.splitlines():
        if ".service" not in line:
            continue
        service, status = line.split()
        if status != "enabled":
            continue
        if "epicscagd" in service:
            gw = Gateway(
                name=service.split(".")[0].replace("epicscagd-", ""),
                pvlist=None,
                launcher=None,
                running_on=set(),
                enabled_on={hostname},
            )
        elif "pvagw" in service:
            gw = Gateway(
                name=service.split(".")[0].replace("pvagw-", "pva-"),
                pvlist=None,
                launcher=None,
                running_on=set(),
                enabled_on={hostname},
            )
        else:
            continue
        gateways.append(gw)
    return gateways


def main():
    gateways = get_configured_gateways("/cds/group/pcds/gateway/config")
    gateways += get_scripted_gateways("/cds/group/pcds/gateway/scripts")
    for host_num in range(1, 7):
        gateways += get_running_gateways(f"pscag0{host_num}")
        gateways += get_enabled_gateways(f"pscag0{host_num}")
    gateways = combine_gatways(gateways)
    table = prettytable.PrettyTable()
    table.field_names = [
        "name", "pvlist", "launcher", "running on", "enabled on",
    ]
    for gw in sorted(gateways):
        table.add_row([
            gw.name,
            gw.pvlist,
            gw.launcher,
            ", ".join(gw.running_on),
            ", ".join(gw.enabled_on),
        ])
    print(table)


if __name__ == "__main__":
    exit(main())
