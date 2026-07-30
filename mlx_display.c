#include <mlx.h>
#include <X11/X.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>

#define CELL 40
#define WALL_W 3

typedef struct s_data
{
    void    *mlx;
    void    *win;
    void    *img;
    char    *buf;
    int     bpp;
    int     line;
    int     endian;
    int     w;
    int     h;
    int     ex;
    int     ey;
    int     sx;
    int     sy;
    char    **g;
}   t_data;

static int parse(const char *path, t_data *d)
{
    FILE    *f;
    char    line[1024];
    int     y;

    f = fopen(path, "r");
    if (!f) return 0;
    d->g = NULL;
    y = 0;
    while (fgets(line, sizeof(line), f))
    {
        line[strcspn(line, "\n")] = 0;
        if (strlen(line) == 0) break;
        d->g = realloc(d->g, (y + 1) * sizeof(char *));
        d->g[y] = strdup(line);
        if (y == 0) d->w = (int)strlen(line);
        y++;
    }
    d->h = y;
    fscanf(f, "%d,%d", &d->ex, &d->ey);
    fscanf(f, "%d,%d", &d->sx, &d->sy);
    fclose(f);
    return (d->w > 0 && d->h > 0);
}

static void put_pixel(t_data *d, int x, int y, int color)
{
    if (x < 0 || x >= d->w * CELL || y < 0 || y >= d->h * CELL)
        return;
    *(int *)(d->buf + y * d->line + x * (d->bpp / 8)) = color;
}

static void fill_rect(t_data *d, int x, int y, int w, int h, int color)
{
    int i, j;
    for (j = y; j < y + h; j++)
        for (i = x; i < x + w; i++)
            put_pixel(d, i, j, color);
}

static void draw_maze(t_data *d)
{
    int x, y;

    fill_rect(d, 0, 0, d->w * CELL, d->h * CELL, 0xF0F0F0);
    for (y = 0; y < d->h; y++)
    {
        for (x = 0; x < d->w; x++)
        {
            char h = d->g[y][x];
            int px = x * CELL;
            int py = y * CELL;
            if (h & 1) fill_rect(d, px, py, CELL, WALL_W, 0x222222);
            if (h & 2) fill_rect(d, px + CELL - WALL_W, py, WALL_W, CELL, 0x222222);
            if (h & 4) fill_rect(d, px, py + CELL - WALL_W, CELL, WALL_W, 0x222222);
            if (h & 8) fill_rect(d, px, py, WALL_W, CELL, 0x222222);
        }
    }
    fill_rect(d, d->ex * CELL + 8, d->ey * CELL + 8, CELL - 16, CELL - 16, 0x00DD00);
    fill_rect(d, d->sx * CELL + 8, d->sy * CELL + 8, CELL - 16, CELL - 16, 0xDD0000);
}

static int on_key(int key, t_data *d)
{
    (void)d;
    if (key == 0xff1b || key == 'q' || key == 'Q')
        exit(0);
    return 0;
}

static int on_close(t_data *d)
{
    (void)d;
    exit(0);
    return 0;
}

int main(int ac, char **av)
{
    t_data d;

    if (ac != 2)
    {
        fprintf(stderr, "Usage: %s <maze_output_file>\n", av[0]);
        fprintf(stderr, "Example: %s output.txt\n", av[0]);
        return 1;
    }
    if (!parse(av[1], &d))
    {
        fprintf(stderr, "Error reading %s\n", av[1]);
        return 1;
    }
    d.mlx = mlx_init();
    d.win = mlx_new_window(d.mlx, d.w * CELL, d.h * CELL, "A-Maze-ing");
    d.img = mlx_new_image(d.mlx, d.w * CELL, d.h * CELL);
    d.buf = mlx_get_data_addr(d.img, &d.bpp, &d.line, &d.endian);
    draw_maze(&d);
    mlx_put_image_to_window(d.mlx, d.win, d.img, 0, 0);
    mlx_hook(d.win, KeyPress, KeyPressMask, on_key, &d);
    mlx_hook(d.win, DestroyNotify, StructureNotifyMask, on_close, &d);
    mlx_loop(d.mlx);
    return 0;
}
