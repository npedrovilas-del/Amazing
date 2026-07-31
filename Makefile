NAME = mlx_display
SRC = mlx_display.c
PY_SRC = a_maze_ing.py
CONFIG = config.txt
CFLAGS = -Wall -Wextra -Werror -Wno-cast-function-type -Iminilibx_linux
LDFLAGS = -Lminilibx_linux -lmlx -lX11 -lXext -lm -lz

VENV = .venv/bin
PY := $(shell test -x $(VENV)/python && echo $(VENV)/python || echo python3)
PIP := $(shell test -x $(VENV)/pip && echo $(VENV)/pip || echo python3 -m pip)

all: run

run:
	$(PY) $(PY_SRC) $(CONFIG)

install:
	$(PIP) install -e '.[dev]'

build:
	$(PY) -m build

lint:
	$(PY) -m flake8 $(PY_SRC) mazegen
	$(PY) -m mypy $(PY_SRC) mazegen

lint-strict:
	$(PY) -m flake8 $(PY_SRC) mazegen
	$(PY) -m mypy --strict $(PY_SRC) mazegen

mlx: $(SRC)
	$(CC) $(CFLAGS) $(SRC) $(LDFLAGS) -o $(NAME)

$(NAME): mlx

clean:
	rm -f $(NAME)
	rm -rf __pycache__ .mypy_cache mazegen/__pycache__ dist build *.egg-info

fclean: clean

re: clean all

.PHONY: all run install debug build lint lint-strict mlx clean fclean re
