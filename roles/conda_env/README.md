conda\_env
=========

Creates a conda environment at the specified prefix.

Requirements
------------

Assumes conda is already installed.

Role Variables
--------------

Available variables are listed below, along with default values (see `defaults/main.yml`).

```
conda_env_conda_dir: /opt/miniconda3
conda_env_escalate: false
conda_env_exe: conda
conda_env_update_if_present: false
```
- `conda_env_conda_dir` should point to the directory of your conda installation.
- `conda_env_escalate` states whether the commands should be run as root.
- `conda_env_exe` is the of your conda executable, this is typically `conda`.
- `conda_env_update_if_present` states the behavior when a conda environment with the same name/prefix exists. `true` if we want to update it else throw an error.

The following variables do not have default values are required by the role.
```
conda_env_environment: <path/to/environment.yml>
conda_env_pip_requirements: <path/to/requirements.txt>
conda_env_prefix: <path/to/conda/environment/prefix>
```
- `conda_env_environment` should point to an `environment.yml` file containing dependencies that need to be installed via `conda`.
- `conda_env_pip_requirements` should point to a `requirements.txt` file containing dependencies that need to be installed via `pip`.
- `conda_env_prefix` should point to path in which the conda environment should be installed.

The following variables (see `vars/main.yml`) are derived from the default variables.
```
conda_env_action_command: "{% if conda_env_update_if_present %}update{% else %}create{% endif %}"
conda_env_bin_dir: "{{ conda_env_conda_dir }}/bin"
conda_env_conda_bin: "{{ conda_env_bin_dir }}/{{ conda_env_exe }}"
conda_env_dest_environment: "{{ conda_env_env_yamls }}/{{ conda_env_prefix | basename }}-{{ conda_env_environment | basename }}"
conda_env_env_yamls: "{{ conda_env_conda_dir }}/env-yamls"
conda_env_pip_bin: "{{ conda_env_prefix }}/bin/pip"
```
- `conda_env_action_command` is either `create` or `update` based on the value of `conda_env_update_if_present`.
- `conda_env_bin_dir` points to the `bin` directory in the conda installation.
- `conda_env_conda_bin` is the absolute path to the `conda` executable.
- `conda_env_dest_environment` points to the location on the host to where the `environment.yml` will be copied.
- `conda_env_env_yamls` is the directory which will store a copy of the `environment.yml`
- `conda_env_pip_bin` is the absolute path to the `pip` executable. This allows us to `pip` install directly into the `conda_env_prefix` without having to activate the environment first.

Dependencies
------------

None.

Example Playbook
----------------

```
- hosts: all
  roles:
    - role: conda_env
      conda_env_conda_dir: /path/to/miniconda3
      conda_env_environment: "{{ playbook_dir }}/environment.yml"
      conda_env_pip_requirements: "{{ playbook_dir }}/requirements.txt"
      conda_env_prefix: /path/to/env/prefix
```

License
-------

Apache-2.0
