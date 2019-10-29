#  Copyright (c) 2015-2018 Cisco Systems, Inc.
#  Copyright (c) 2018 Red Hat, Inc.
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to
#  deal in the Software without restriction, including without limitation the
#  rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
#  sell copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in
#  all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#  FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#  DEALINGS IN THE SOFTWARE.

import os
import pytest
import sh
import unittest

from molecule import logger
from molecule.test.conftest import run_command, change_dir_to
from molecule.test.functional.conftest import metadata_lint_update


LOG = logger.get_logger(__name__)

has_azure = pytest.mark.skipif(
    # TODO(ssbarnea): need to implement more practical azure availability test
    "AZURE_SECRET" not in os.environ,
    reason="Azure credentials not detected, skipping live tests.",
)


class AzureTest(unittest.TestCase):
    @pytest.fixture(autouse=True)
    def scenario(self, temp_dir):
        role_directory = os.path.join(temp_dir.strpath, "test-init")
        options = {"role_name": "test-init"}
        cmd = sh.molecule.bake("init", "role", **options)
        run_command(cmd)
        metadata_lint_update(role_directory)

        with change_dir_to(role_directory):
            molecule_directory = pytest.helpers.molecule_directory()
            scenario_directory = os.path.join(molecule_directory, "test-scenario")
            options = {
                "scenario_name": "test-scenario",
                "role_name": "test-init",
                "driver-name": "azure",
            }
            cmd = sh.molecule.bake("init", "scenario", **options)
            run_command(cmd)

            assert os.path.isdir(scenario_directory)
            yield

    def test_lint(self):
        cmd = sh.molecule.bake("lint", "-s", "test-scenario")
        run_command(cmd)

    @has_azure
    def test_destroy_first(self):
        cmd = sh.molecule.bake("destroy", "-s", "test-scenario")
        run_command(cmd)

    @has_azure
    def test_create(self):
        cmd = sh.molecule.bake("--destroy=never", "create", "-s", "test-scenario")
        run_command(cmd)

    @has_azure
    def test_converge(self, depends=["test_create"]):
        cmd = sh.molecule.bake("converge", "-s", "test-scenario")
        run_command(cmd)

    @has_azure
    def test_destroy_after_create(self, depends=["test_converge"]):
        cmd = sh.molecule.bake("destroy", "-s", "test-scenario")
        run_command(cmd)
