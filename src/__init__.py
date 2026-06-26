"""Compatibility namespace for legacy imports.

Canonical method implementations live under the `methods` package. This `src`
package is retained so historical scripts that import `src.*` continue to run.
"""

from methods import *  # noqa: F401,F403
