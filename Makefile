install:
	pip3 install -r requirements.txt

install-kahypar:
	./install_mt-kahypar.sh

install-cudd:
	./install_dd_cudd.sh

format:
	black ./ --experimental-string-processing
	isort . --profile=black

lint:
	flake8 --exclude=./venv/,./dd-*/,/mt-kahypar/ --max-line-length 88 --ignore=E203,W503

test:
	pytest ./tests/

run:
	python main.py
