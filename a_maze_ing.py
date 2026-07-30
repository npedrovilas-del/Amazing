import sys
from mazegen.config import load_config, ConfigError
from mazegen.generator import MazeGenerator, COLORS

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("The program should run with 1 argument: <file_name_config.txt>")
        sys.exit(1)
    try:
        config = load_config(sys.argv[1])
    except ConfigError as e:
        print(f"{e}")
        sys.exit(1)
    except ValueError as e:
        print(f"{sys.argv[1]} {e}")
        sys.exit(1)
    try:
        m2 = MazeGenerator(config["WIDTH"], config["HEIGHT"],
                           seed=config["SEED"])
        entry_x, entry_y = config["ENTRY"]
        m2.apply_42_pattern(config["ENTRY"], config["EXIT"])
        m2.generate(entry_x, entry_y)
        if not config["PERFECT"]:
            m2.add_loops(100)
        m2.write_output(config["OUTPUT_FILE"], config["ENTRY"],
                        config["EXIT"])
        entry_x, entry_y = config["ENTRY"]
        exit_x, exit_y = config["EXIT"]
        entry_cell = m2.grid[entry_y][entry_x]
        exit_cell = m2.grid[exit_y][exit_x]
        caminho = m2.bfs(entry_cell, exit_cell)
        m2.print_maze(config["ENTRY"], config["EXIT"], caminho)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
    mostrar_caminho = True
    while True:
        print("=== A-Maze-ing ===")
        print("1. Re-generate maze")
        print("2. Show/Hide path")
        print("3. Change colors")
        print("4. Launch MLX display")
        print("5. Quit")
        escolha = input("Choice? (1-5): ")
        if escolha == "1":
            try:
                config = load_config(sys.argv[1])
                m2 = MazeGenerator(config["WIDTH"], config["HEIGHT"],
                                   seed=config["SEED"])
                entry_x, entry_y = config["ENTRY"]
                m2.apply_42_pattern(config["ENTRY"], config["EXIT"])
                m2.generate(entry_x, entry_y)
                if not config["PERFECT"]:
                    m2.add_loops(100)
                m2.write_output(config["OUTPUT_FILE"], config["ENTRY"],
                                config["EXIT"])
                entry_x, entry_y = config["ENTRY"]
                exit_x, exit_y = config["EXIT"]
                entry_cell = m2.grid[entry_y][entry_x]
                exit_cell = m2.grid[exit_y][exit_x]
                caminho = m2.bfs(entry_cell, exit_cell)
                m2.print_maze(config["ENTRY"], config["EXIT"], caminho)
            except Exception as e:
                print(f"Error: {e}")
        elif escolha == "2":
            mostrar_caminho = not mostrar_caminho
            if mostrar_caminho:
                m2.print_maze(config["ENTRY"], config["EXIT"], caminho)
            else:
                m2.print_maze(config["ENTRY"], config["EXIT"], [])
        elif escolha == "3":
            print("1: Red  2: Green  3: Blue  4: Yellow  5: Cyan  6: White")
            cor_escolha = input("Escolhe uma cor: ")
            cor_atual = COLORS.get(cor_escolha, "37")
            args = (config["ENTRY"], config["EXIT"], caminho if
                    mostrar_caminho else [], cor_atual)
            m2.print_maze(*args)
        elif escolha == "4":
            import subprocess
            try:
                subprocess.Popen(["./mlx_display", config["OUTPUT_FILE"]])
            except FileNotFoundError:
                print("mlx_display not found. Compile: make mlx_display")
        elif escolha == "5":
            break
