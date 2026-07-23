"""Legacy release-packaging entrypoint.

The maintained reproducible release is this repository itself. This command is
kept only to reproduce the older allowlisted packaging snapshot.
"""

from legacy.prepare_release_repository import *  # noqa: F401,F403


if __name__ == "__main__":
    main()
