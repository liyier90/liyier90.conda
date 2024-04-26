from __future__ import absolute_import, division, print_function

__metaclass__ = type
import json

import pytest

from plugins.modules import conda

pytestmark = pytest.mark.usefixtures("patch_ansible_module")


@pytest.mark.parametrize(
    "patch_ansible_module", [{"name": "six"}], indirect=["patch_ansible_module"]
)
def test_fail_when_conda_absent(mocker, capfd):
    mock_which = mocker.patch("shutil.which")
    mock_which.return_value = None

    with pytest.raises(SystemExit):
        conda.main()

    out, err = capfd.readouterr()
    results = json.loads(out)
    assert results["failed"]
    assert "Conda executable not found." in results["msg"]
