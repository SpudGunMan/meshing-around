# Install Mesh Bot

Python 3.11+ is required. From the checkout root:

```sh
bash bootstrap.sh
bash launch.sh --check
bash launch.sh
```

`bootstrap.sh` creates or refreshes `venv/` and installs the new runtime's radio
dependencies. It does not install original feature dependencies, copy legacy
data, or configure services. `launch.sh` runs `mesh_bot.py` with any supplied
arguments and preserves its exit status.

The default `bot.toml` selects console transport. To use a radio, select TCP with
`hostname` and optional `port`, or serial with `device`. See
[docs/plugins.md](docs/plugins.md) for the configuration and plugin contract.

```sh
venv/bin/python mesh_bot.py --config /path/to/local.toml
venv/bin/python -m unittest discover -s tests -v
```

The original install and service scripts are archived under `integration/` and
are not used for this runtime.
