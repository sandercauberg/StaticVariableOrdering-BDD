install:
	pip install -r requirements.txt

format:
	./venv/Scripts/black -l 80 ./

lint:
	./venv/Scripts/flake8 --exclude=./venv/ --max-line-length 80

test:
	pytest ./tests/

run:
	python main.py
