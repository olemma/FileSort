# FileSort

## Development
Use Pipenv to setup - because libtorrent and some other
system-dependencies of deluge, you'll need to install deluge's dependencies on your system directly.

Then run
```shell script
pipenv --python=/path/to/python3.6 --site-packages
pipenv install --dev
```

## Testing
```
pipenv run python -m pytest
```
