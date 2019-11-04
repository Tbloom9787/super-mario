from source import game_functions, level
from source import menu
from source import constants as c


def run():
    game = game_functions.Control()
    state_dict = {c.MAIN_MENU: menu.Menu(),
                  c.LOAD_SCREEN: menu.LoadScreen(),
                  c.LEVEL: level.Level(),
                  c.GAME_OVER: menu.GameOver(),
                  c.TIME_OUT: menu.TimeOut()}
    game.setup_states(state_dict, c.MAIN_MENU)
    game.main()


if __name__ == '__main__':
    run()
