# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = """
---
module: conda
short_description: Manage Python library dependencies via conda
description:
     - "Manage Python library dependencies via conda."
author: "liyier90 (@liyier90)"
options:
  name:
    description:
      - The name of a Python library to install.
      - This needs to be a list containing version specifiers.
    type: list
    elements: str
    required: true
  channel:
    description:
      - An optional list of conda package channels.
    type: list
    elements: str
  prefix:
    description:
      - An optional path to a conda directory to install into.
    type: path
  executable:
    description:
      - Full path to the conda executable.
    type: path
"""

EXAMPLES = """
- name: Install multiple Python packages via conda
  conda:
    name:
      - numpy==1.23.4
      - scipy==1.13.0
    channel:
      - conda-forge
    prefix: /path/to/conda/prefix
    executable: /path/to/conda
"""

RETURN = """
cmd:
  description: conda command used by the module
  returned: success
  type: str
  sample: pip2 install ansible six
name:
  description: list of Python modules targeted by conda
  returned: success
  type: list
  sample: ['numpy==1.23.4', 'scipy==1.13.0']
prefix:
  description: Path to the conda prefix
  returned: success, if a conda prefix path was provided
  type: str
  sample: "/path/to/prefix"
"""

import json
import os.path
import shutil
import traceback

from ansible.module_utils.basic import AnsibleModule, missing_required_lib
from ansible.module_utils.common.text.converters import to_native

PACKAGING_IMP_ERR = None
HAS_PACKAGING = False
try:
    from packaging.requirements import Requirement

    HAS_PACKAGING = True
except Exception:
    HAS_PACKAGING = False
    PACKAGING_IMP_ERR = traceback.format_exc()


class CondaExecutableNotFoundError(Exception):
    """Error raised when the Conda executable was not found."""

    def __init__(self):
        super().__init__("Conda executable not found.")


def run_module():
    module = AnsibleModule(
        argument_spec=dict(
            name=dict(type="list", elements="str", required=True),
            channel=dict(type="list", elements="str"),
            prefix=dict(type="path"),
            executable=dict(type="path"),
        ),
        supports_check_mode=True,
    )

    if not HAS_PACKAGING:
        module.fail_json(
            msg=missing_required_lib("packaging"), exception=PACKAGING_IMP_ERR
        )

    name = module.params["name"]
    channel = module.params["channel"]
    prefix = module.params["prefix"]

    err = ""
    out = ""

    if prefix is not None and not os.path.exists(prefix):
        module.fail_json(msg=f"Conda prefix ({prefix}) not found.")

    conda = _get_conda(module.params["executable"])
    cmd = conda + ["install", "-y", "--json"]

    if channel is not None:
        for chn in channel:
            cmd.extend(["-c", chn])

    if prefix is not None:
        cmd.extend(["-p", prefix])

    if name:
        packages = [Requirement(pkg) for pkg in name]
        cmd.extend(to_native(pkg) for pkg in packages)

    if module.check_mode:
        pkg_cmd, out_conda, err_conda = _get_packages(module, conda, prefix)
        out += out_conda
        err += err_conda

        changed = False
        if name:
            installed_packages = json.loads(out_conda)
            for package in packages:
                is_present = _is_present(package, installed_packages)
                if not is_present:
                    changed = True
                    break

        module.exit_json(changed=changed, cmd=pkg_cmd, stdout=out, stderr=err)

    rc, out_conda, err_conda = module.run_command(cmd)
    out += out_conda
    err += err_conda
    if rc != 0:
        module.fail_json(cmd=cmd, msg=f"stdout: {out}\nstderr: {err}")

    changed = (
        json.loads(out_conda).get("message", "")
        != "All requested packages already installed."
    )

    module.exit_json(
        changed=changed,
        cmd=cmd,
        name=name,
        prefix=prefix,
        stdout=out,
        stderr=err,
    )


def main():
    run_module()


def _get_conda(executable):
    """If `executable` is not None, checks whether it points to a valid file
    and returns it if this is the case. Otherwise tries to find the `conda`
    executable in the path. Calls `fail_json` if either of these fail.
    """
    if executable is None:
        conda = shutil.which("conda")
        if conda is not None:
            return [conda]
    else:
        if os.path.isfile(executable):
            return [executable]

    raise CondaExecutableNotFoundError()


def _get_packages(module, conda, prefix):
    cmd = conda + ["list", "--json"]
    if prefix is not None:
        cmd.extend(["-p", prefix])
    rc, out, err = module.run_command(cmd)
    return " ".join(cmd), out, err


def _is_present(req, installed_pkgs):
    for pkg in installed_pkgs:
        if req.name == pkg["name"] and req.specifier.contains(pkg["version"]):
            return True
    return False


if __name__ == "__main__":
    main()
