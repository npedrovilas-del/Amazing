#include <mlx.h>
#include <X11/X.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <time.h>
#include <sys/stat.h>

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
    int     entry_x;
    int     entry_y;
    int     exit_x;
    int     exit_y;
    int     cell;
    int     wall_w;
    char    **g;
    char    **path;
    char    *filepath;
    long    mtime_sec;
    long    mtime_nsec;
    int     show_path;
    char    *show_path_file;
    int     wall_color;
    char    *color_file;
}   t_data;

static void put_pixel(t_data *d, int x, int y, int color)
{
    if (x < 0 || x >= d->w * d->cell || y < 0 || y >= d->h * d->cell)
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

static void free_maze_data(t_data *d)
{
    if (d->g)
    {
        for (int i = 0; i < d->h; i++)
            free(d->g[i]);
        free(d->g);
        d->g = NULL;
    }
    if (d->path)
    {
        for (int i = 0; i < d->h; i++)
            free(d->path[i]);
        free(d->path);
        d->path = NULL;
    }
}

static void parse(const char *path, t_data *d)
{
    FILE    *f;
    char    line[1024];
    int     y;

    free_maze_data(d);
    f = fopen(path, "r");
    if (!f) return;
    y = 0;
    while (fgets(line, sizeof(line), f))
    {
        line[strcspn(line, "\n")] = 0;
        if (strlen(line) == 0) break;
        d->g = realloc(d->g, (y + 1) * sizeof(char *));
        d->g[y] = strdup(line);
        for (char *p = d->g[y]; *p; p++)
            *p = (*p >= 'A') ? *p - 'A' + 10 : *p - '0';
        if (y == 0) d->w = (int)strlen(line);
        y++;
    }
    d->h = y;
    fgets(line, sizeof(line), f);
    sscanf(line, "%d,%d", &d->entry_x, &d->entry_y);
    fgets(line, sizeof(line), f);
    sscanf(line, "%d,%d", &d->exit_x, &d->exit_y);

    d->path = calloc(d->h, sizeof(char *));
    for (int i = 0; i < d->h; i++)
        d->path[i] = calloc(d->w, 1);

    if (fgets(line, sizeof(line), f))
    {
        line[strcspn(line, "\n")] = 0;
        int x = d->entry_x, yy = d->entry_y;
        if (x >= 0 && x < d->w && yy >= 0 && yy < d->h)
            d->path[yy][x] = 1;
        for (char *p = line; *p; p++)
        {
            if (*p == 'E' && x + 1 < d->w) x++;
            else if (*p == 'W' && x - 1 >= 0) x--;
            else if (*p == 'S' && yy + 1 < d->h) yy++;
            else if (*p == 'N' && yy - 1 >= 0) yy--;
            d->path[yy][x] = 1;
        }
    }

    fclose(f);

    if (!d->filepath)
        d->filepath = strdup(path);
}

static void draw_final(t_data *d)
{
    int x, y;

    for (y = 0; y < d->h; y++)
    {
        for (x = 0; x < d->w; x++)
        {
            int px = x * d->cell;
            int py = y * d->cell;

            if (x == d->entry_x && y == d->entry_y)
            {
                fill_rect(d, px + d->cell / 8, py + d->cell / 8,
                          d->cell * 3 / 4, d->cell * 3 / 4, 0x00AA00);
                mlx_string_put(d->mlx, d->win, px + d->cell / 6,
                               py + d->cell * 7 / 20, 0xFFFFFF, "EN");
            }
            else if (x == d->exit_x && y == d->exit_y)
            {
                fill_rect(d, px + d->cell / 8, py + d->cell / 8,
                          d->cell * 3 / 4, d->cell * 3 / 4, 0xAA0000);
                mlx_string_put(d->mlx, d->win, px + d->cell / 6,
                               py + d->cell * 7 / 20, 0xFFFFFF, "EX");
            }
            else if (d->show_path && d->path[y][x])
            {
                fill_rect(d, px + d->cell / 6, py + d->cell / 6,
                          d->cell * 2 / 3, d->cell * 2 / 3, 0xCCCC00);
                mlx_string_put(d->mlx, d->win, px + d->cell * 7 / 20,
                               py + d->cell * 7 / 20, 0x000000, "*");
            }
        }
    }
}

static void render_maze(t_data *d)
{
    int x, y;

    fill_rect(d, 0, 0, d->w * d->cell, d->h * d->cell, 0x111111);
    for (y = 0; y < d->h; y++)
    {
        for (x = 0; x < d->w; x++)
        {
            int h = d->g[y][x];
            int px = x * d->cell;
            int py = y * d->cell;
            if (h == 15)
                fill_rect(d, px, py, d->cell, d->cell, 0x2D0050);
            else
            {
                fill_rect(d, px + 2, py + 2, d->cell - 4, d->cell - 4, 0x1A1A2E);
                if (h & 1) fill_rect(d, px, py, d->cell, d->wall_w, d->wall_color);
                if (h & 2) fill_rect(d, px + d->cell - d->wall_w, py, d->wall_w, d->cell, d->wall_color);
                if (h & 4) fill_rect(d, px, py + d->cell - d->wall_w, d->cell, d->wall_w, d->wall_color);
                if (h & 8) fill_rect(d, px, py, d->wall_w, d->cell, d->wall_color);
            }
        }
    }
    draw_final(d);
    mlx_put_image_to_window(d->mlx, d->win, d->img, 0, 0);
}

static int check_show_path(t_data *d)
{
    FILE *f = fopen(d->show_path_file, "r");
    if (!f) return 0;
    char c = fgetc(f);
    int new_val = (c == '1');
    fclose(f);
    if (new_val != d->show_path)
    {
        d->show_path = new_val;
        return 1;
    }
    return 0;
}

static const int g_wall_colors[] = {0, 0xCC5555, 0x55CC55, 0x5555CC,
                                    0xCCCC55, 0x55CCCC, 0xCCCCCC};

static int check_color(t_data *d)
{
    FILE *f = fopen(d->color_file, "r");
    if (!f) return 0;
    int c = fgetc(f);
    fclose(f);
    int idx = (c >= '1' && c <= '6') ? c - '0' : 0;
    if (g_wall_colors[idx] && g_wall_colors[idx] != d->wall_color)
    {
        d->wall_color = g_wall_colors[idx];
        return 1;
    }
    return 0;
}

static int check_reload(void *param)
{
    t_data *d = param;
    struct stat st;

    if (stat(d->filepath, &st) == 0
        && (st.st_mtim.tv_sec != d->mtime_sec
            || st.st_mtim.tv_nsec != d->mtime_nsec))
    {
        long sec = st.st_mtim.tv_sec;
        long nsec = st.st_mtim.tv_nsec;
        parse(d->filepath, d);
        if (d->g)
        {
            d->mtime_sec = sec;
            d->mtime_nsec = nsec;
            render_maze(d);
        }
        return 0;
    }
    int need = 0;
    if (d->show_path_file && check_show_path(d)) need = 1;
    if (d->color_file && check_color(d)) need = 1;
    if (need) render_maze(d);
    {
        struct timespec ts = {0, 30000000};
        nanosleep(&ts, NULL);
    }
    return 0;
}

static void animate_generation(t_data *d)
{
    int x, y;
    struct timespec ts = {0, 15000000};

    fill_rect(d, 0, 0, d->w * d->cell, d->h * d->cell, 0x111111);
    mlx_put_image_to_window(d->mlx, d->win, d->img, 0, 0);

    for (y = 0; y < d->h; y++)
    {
        for (x = 0; x < d->w; x++)
        {
            int h = d->g[y][x];
            int px = x * d->cell;
            int py = y * d->cell;

            fill_rect(d, px + 2, py + 2, d->cell - 4, d->cell - 4, 0x336699);
            mlx_put_image_to_window(d->mlx, d->win, d->img, 0, 0);
            nanosleep(&ts, NULL);

            if (h == 15)
            {
                fill_rect(d, px, py, d->cell, d->cell, 0x2D0050);
            }
            else
            {
                fill_rect(d, px + 2, py + 2, d->cell - 4, d->cell - 4, 0x1A1A2E);
                if (h & 1) fill_rect(d, px, py, d->cell, d->wall_w, d->wall_color);
                if (h & 2) fill_rect(d, px + d->cell - d->wall_w, py, d->wall_w, d->cell, d->wall_color);
                if (h & 4) fill_rect(d, px, py + d->cell - d->wall_w, d->cell, d->wall_w, d->wall_color);
                if (h & 8) fill_rect(d, px, py, d->wall_w, d->cell, d->wall_color);
            }
        }
    }

    draw_final(d);
    mlx_put_image_to_window(d->mlx, d->win, d->img, 0, 0);
}

static int on_key(int key, void *param)
{
    t_data *d = param;
    if (key == 0xff1b || key == 'q' || key == 'Q')
        exit(0);
    if (key >= '1' && key <= '6')
    {
        int c = g_wall_colors[key - '0'];
        if (c && c != d->wall_color)
        {
            d->wall_color = c;
            render_maze(d);
        }
    }
    return 0;
}

static int on_close(void *param)
{
    (void)param;
    exit(0);
    return 0;
}

int main(int ac, char **av)
{
    t_data d;

    if (ac != 2)
    {
        fprintf(stderr, "Usage: %s <maze_output_file>\n", av[0]);
        return 1;
    }
    memset(&d, 0, sizeof(d));
    parse(av[1], &d);
    if (d.w <= 0 || d.h <= 0)
    {
        fprintf(stderr, "Error reading %s\n", av[1]);
        return 1;
    }
    {
        struct stat st;
        if (stat(av[1], &st) == 0)
        {
            d.mtime_sec = st.st_mtim.tv_sec;
            d.mtime_nsec = st.st_mtim.tv_nsec;
        }
    }
    d.show_path = 1;
    d.show_path_file = NULL;
    d.wall_color = 0xAAAAAA;
    d.color_file = NULL;
    {
        int sw, sh;
        d.mlx = mlx_init();
        mlx_get_screen_size(d.mlx, &sw, &sh);
        int mw = sw * 4 / 5;
        int mh = sh * 4 / 5;
        int cw = mw / d.w;
        int ch = mh / d.h;
        d.cell = (cw < ch) ? cw : ch;
        if (d.cell < 8)  d.cell = 8;
        if (d.cell > 64) d.cell = 64;
        d.wall_w = (d.cell > 20) ? d.cell / 12 : 2;
    }
    {
        const char *sfx = ".show";
        d.show_path_file = malloc(strlen(av[1]) + strlen(sfx) + 1);
        sprintf(d.show_path_file, "%s%s", av[1], sfx);
        check_show_path(&d);
    }
    {
        const char *sfx = ".color";
        d.color_file = malloc(strlen(av[1]) + strlen(sfx) + 1);
        sprintf(d.color_file, "%s%s", av[1], sfx);
        check_color(&d);
    }
    d.win = mlx_new_window(d.mlx, d.w * d.cell, d.h * d.cell, "A-Maze-ing");
    d.img = mlx_new_image(d.mlx, d.w * d.cell, d.h * d.cell);
    d.buf = mlx_get_data_addr(d.img, &d.bpp, &d.line, &d.endian);

    animate_generation(&d);

    mlx_hook(d.win, KeyPress, KeyPressMask, (int (*)())on_key, &d);
    mlx_hook(d.win, DestroyNotify, StructureNotifyMask, (int (*)())on_close, &d);
    mlx_loop_hook(d.mlx, (int (*)())check_reload, &d);
    mlx_loop(d.mlx);
    return 0;
}
