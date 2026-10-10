# Original implementation awaiting integration

This directory preserves the original mesh/pong bots, feature modules, scripts,
configuration template, assets, and documentation as reference for porting
features to the new plugin API. The original project README is saved as
[ORIGINAL_README.md](ORIGINAL_README.md).

These files are sidelined, not a supported runnable installation. Paths and
imports inside them describe the original layout and have deliberately not
been rewritten. No active launcher, container, or test command uses this code.
Use the original meshing-around project to run the original implementation.

Port features into paired `.py` / `.toml` files in `../plugins.d/`, using the
[plugin contract](../docs/plugins.md). New plugins must not import this directory
or depend on its global state. Move reusable behavior into the feature plugin
and use core services for transport, scheduling, policy, and storage.

Locally generated legacy data and configuration were moved here with the source
to preserve existing work. They are not committed and are not used by the new
runtime; its state remains in the root `data/core.db`.
