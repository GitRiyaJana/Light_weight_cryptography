# Makefile for the Toy Gimli Cipher

# Define the Python interpreter
PYTHON = python3

# --- Targets ---

.PHONY: all run test clean

all: test

run:
	@echo "Running the Toy Gimli Cipher example..."
	@$(PYTHON) Gimli_toy.py

test:
	@echo "Running test vectors..."
	@$(PYTHON) test_toy_gimli.py

clean:
	@echo "Cleaning up..."
	@rm -rf __pycache__
	@find . -name "*.pyc" -delete
