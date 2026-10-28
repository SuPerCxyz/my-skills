# Unit Tests for privsep Entry Points

Use this file only when unit tests touch functions decorated with a privsep entrypoint and fail because the helper process would be started. It explains the test-side handling pattern.

## Problem 问题现象

Functions decorated with `@cinder.privsep.sys_admin_pctxt.entrypoint` cannot be called directly in unit tests:

```
Exception: You have attempted to start a privsep helper.
This is not allowed in the gate.
```

## Solution: Disable client_mode 测试侧处理

Set `client_mode = False` on the privsep context so the entrypoint calls the inner function directly:

```python
from unittest import mock

from cinder import privsep
from cinder.privsep import cgroup
from cinder.tests.unit import test


class CgroupFunctionTestCase(test.TestCase):

    def setUp(self):
        super(CgroupFunctionTestCase, self).setUp()
        self._orig_client_mode = privsep.sys_admin_pctxt.client_mode
        privsep.sys_admin_pctxt.client_mode = False

    def tearDown(self):
        privsep.sys_admin_pctxt.client_mode = self._orig_client_mode
        super(CgroupFunctionTestCase, self).tearDown()

    def test_cgroup_create_v2(self):
        with mock.patch.object(cgroup.os.path, 'isfile', return_value=True):
            with mock.patch.object(cgroup.processutils, 'execute') as ex:
                cgroup.cgroup_create('mygroup')
                ex.assert_called_once_with('cgcreate', '-g', 'io:mygroup')
```

This pattern:
1. Saves original `client_mode` in `setUp`
2. Sets `client_mode = False` so entrypoint bypasses the daemon
3. Restores original value in `tearDown`
4. Mock `os.path.isfile` to control v1/v2 branch selection
5. Mock `processutils.execute` to verify the correct command
