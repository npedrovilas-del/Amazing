NAME = mlx_display
SRC = mlx_display.c
CFLAGS = -Wall -Wextra -Werror
LDFLAGS = -lmlx -lX11 -lXext

all: $(NAME)

$(NAME): $(SRC)
	cc $(CFLAGS) $(SRC) $(LDFLAGS) -o $(NAME)

clean:
	rm -f $(NAME)

fclean: clean

re: clean all

.PHONY: all clean fclean re
