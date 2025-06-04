# Makefile to generate working environment for Ops

# used to determine arch for downloads
UNAME := $(shell uname | tr '[:upper:]' '[:lower:]')

# 
ACTIVATE_BIN := venv/bin/activate

install: all 

all: $(ACTIVATE_BIN) pip_requirements xboxdrv ola

clean:
	$(RM) -r venv
	find . -name "*.pyc" -exec $(RM) -rf {} \;

$(ACTIVATE_BIN):
	virtualenv venv --python=python3.9
	chmod +x $@

xboxdrv: /usr/bin/xboxdrv

/usr/bin/xboxdrv: 
	sudo apt-get install -y xboxdrv

ola: /etc/ola

/etc/ola: 
	sudo apt-get install -y ola

pip_requirements: $(ACTIVATE_BIN) requirements.txt
	. venv/bin/activate; PYTHONWARNINGS='ignore:DEPRECATION' pip install --no-cache-dir -r requirements.txt

freeze:
	pip freeze > requirements.txt
