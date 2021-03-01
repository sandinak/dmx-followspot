# Makefile to generate working environment for Ops

# used to determine arch for downloads
UNAME := $(shell uname | tr '[:upper:]' '[:lower:]')

# 
ACTIVATE_BIN := venv/bin/activate

install: all 

all: $(ACTIVATE_BIN) pip_requirements 

clean:
	$(RM) -r venv
	find . -name "*.pyc" -exec $(RM) -rf {} \;

$(ACTIVATE_BIN):
	virtualenv venv --python=python3
	chmod +x $@

pip_requirements: $(ACTIVATE_BIN) requirements.txt
	. venv/bin/activate; PYTHONWARNINGS='ignore:DEPRECATION' pip install --no-cache-dir -r requirements.txt

freeze:
	pip freeze > requirements.txt
