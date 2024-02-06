install:
	pip install -r requirements.txt

format:
	./venv/Scripts/black ./

lint:
	./venv/Scripts/flake8 --exclude=./venv/ --max-line-length 88

test:
	pytest ./tests/

run:
	python main.py
