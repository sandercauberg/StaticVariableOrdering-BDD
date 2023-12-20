install:
	pip install -r requirements.txt

format:
	./venv/Scripts/black -l 80 ./

lint:
	./venv/Scripts/flake8 --exclude=./venv/

test:
	pytest ./tests/

run:
	python main.py
