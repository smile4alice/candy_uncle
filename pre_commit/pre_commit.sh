black --config pre_commit/black.cfg .
isort --settings pre_commit/isort.cfg .
flake8 --config pre_commit/flake8.cfg .
mypy --config-file pre_commit/mypy.cfg .
