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
	virtualenv venv --python=python3.11
	chmod +x $@

xboxdrv: /usr/bin/xboxdrv

/usr/bin/xboxdrv: 
	sudo apt-get install -y xboxdrv

ola: /etc/ola

/etc/ola: 
	sudo apt-get install -y ola

pip_requirements: $(ACTIVATE_BIN) requirements.txt
	. venv/bin/activate; PYTHONWARNINGS='ignore:DEPRECATION' pip install --no-cache-dir -r requirements.txt
	$(MAKE) patch_ola

patch_ola: venv/lib/python3.11/site-packages/ola/OlaClient.py
	@echo "Patching OLA for Python 3.11+ compatibility..."
	@if ! grep -q "frombytes" venv/lib/python3.11/site-packages/ola/OlaClient.py; then \
		sed -i 's/data\.fromstring(/data.frombytes(/g' venv/lib/python3.11/site-packages/ola/OlaClient.py && \
		sed -i 's/data\.tostring(/data.tobytes(/g' venv/lib/python3.11/site-packages/ola/OlaClient.py && \
		echo "OLA patched successfully for Python 3.11+ compatibility"; \
	else \
		echo "OLA already patched for Python 3.11+ compatibility"; \
	fi

freeze:
	pip freeze > requirements.txt
