install:
	pip install -r requirements.txt

format:
	./venv/Scripts/black -l 80 main.py

lint:
	./venv/Scripts/flake8 main.py

run:
	python main.py
