# -*- encoding: utf-8 -*-
# Bookapp v0.1.0
# A library management app.
# Copyright © 2016, Chris Warrick.
# See /LICENSE for licensing information.

"""
Start CLI interface.

:Copyright: © 2016, Chris Warrick.
:License: BSD (see /LICENSE).
"""

import sys
from bookapp.cli import cli_main
__all__ = ()

if __name__ == '__main__':
    sys.exit(cli_main())
