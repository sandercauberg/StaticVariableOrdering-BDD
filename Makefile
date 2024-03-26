ifeq ($(OS),Windows_NT)
    PATH := ./venv/Scripts
else
    PATH := ./venv/bin
endif

install:
	pip install -r requirements.txt
	./install_dd_cudd.sh

format:
	$(PATH)/black ./

lint:
	$(PATH)/flake8 --exclude=./venv/ --max-line-length 88

test:
	pytest ./tests/

run:
	python main.py
