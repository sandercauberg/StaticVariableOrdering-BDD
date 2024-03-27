install:
	pip3 install -r requirements.txt
	./install_dd_cudd.sh

format:
	black ./

lint:
	flake8 --exclude=./venv/,./dd-*/ --max-line-length 88

test:
	pytest ./tests/

run:
	python main.py
