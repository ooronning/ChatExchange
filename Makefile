default: test run-example

run-example: install-dependencies
	python examples/chat.py

test: install-dev-dependencies
	python -m pytest

install-dependencies:
	# This also creates a link to `chatexchange/` in the Python
	# environment, which is neccessary for the other files to be
	# able to find it.
	rm -rf src/*.egg-info
	pip install -e .

install-dev-dependencies:
	# This also creates a link to `chatexchange/` in the Python
	# environment, which is neccessary for the other files to be
	# able to find it.
	rm -rf src/*.egg-info
	pip install -e .[dev]

clean:
	rm -rf src/*.egg-info
	find . -type f -name '*.pyc' -delete
	find . -type d -name '__pycache__' -delete
