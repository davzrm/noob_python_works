#!python3 
## Whack-that-mole 

import logging
import numpy as np
import tkinter as tk
import time
import threading
from enum import Enum
from math import floor

LOGGING_FORMAT = "{levelname} at line {lineno} --> {message}"
logging.basicConfig(level=logging.DEBUG, format=LOGGING_FORMAT, style="{")
# logging.disable(logging.DEBUG)
logging.disable(logging.INFO)


class A(Enum): 
    OPEN = 1
    CLOSE = 0 


DIMENSION_COUNT = 2
class B: 
    """Grid logic"""
    def __init__(self) -> None:
        self.grid_length = 3
        self.grid = None
        self.reset(self.grid_length)

    def get_random_coordinates(self, count):
        random_coords = np.random.randint(0, self.grid_length, (count, DIMENSION_COUNT))
        random_coords = np.unique(random_coords, axis=0)
        logging.info(f"Random coordinates: \n{random_coords}")
        return random_coords

    def update(self, to_state:A, coords): 
        ## coords adjusted for numpy coordinate indexing
        adj_coords = tuple(np.array(coords).T)
        self.grid[adj_coords] = to_state.value
        logging.debug(f"Grid now:\n{self.grid}")
    
    def calculate_outcome(self, coords): 
        """
        return: (score, penalty)
        """
        adj_coords = tuple(np.array(coords).T)
        score = np.count_nonzero( self.grid[adj_coords] == A.CLOSE.value)
        penalty = np.count_nonzero( self.grid[adj_coords] == A.OPEN.value)
        logging.debug(f"Score +{score}, Life -{penalty}")
        return score, penalty

    def reset(self, grid_length): 
        self.grid_length = grid_length
        self.grid = np.zeros((self.grid_length, ) * DIMENSION_COUNT)


class C(Enum): 
    """
    DIFFICULTY
    Values represent grid length
    """
    NOOB = 3
    EZ = 5
    CASUAL = 7
    PRO = 11

    def length(self): 
        diff_lookup = {
            C.NOOB : 3, 
            C.EZ : 5, 
            C.CASUAL : 7, 
            C.PRO : 11, 
        }
        return diff_lookup[self]

    def max_mole_count(self): 
        diff_lookup = {
            C.NOOB : 1, 
            C.EZ : 2, 
            C.CASUAL : 3, 
            C.PRO : 5, 
        }
        return diff_lookup[self]

    def timer_change_rate(self): 
        diff_lookup = {
            C.NOOB : 0.05,
            C.EZ : 0.07,
            C.CASUAL : 0.1, 
            C.PRO : 0.15,
        }
        return diff_lookup[self]


MASTER_TITLE = "Whack-ez-mole"
TITLE_FRAME_KEY = "frame_1"
GRID_FRAME_KEY = "frame_2"
GRID_BUTTONS_KEY = "grid_buttons"
GRID_LABEL_KEY = "grid_label"
GAME_OVER_WINDOW_KEY = "frame_3"
GAME_OVER_LABEL_KEY = "frame_3_label"
SETTINGS_WINDOW_KEY = "frame_4"
class D: 
    """GUI"""
    def __init__(self, master) -> None:
        self.master = master
        self.grid_length = 3
        self.widget_lookup = {}
        self.difficulty_setting = tk.IntVar()
        self.life_setting = tk.IntVar()
        self.score = 0
        self._init_gui()

    def _init_gui(self): 
        self.master.title(MASTER_TITLE)
        self.widget_lookup.setdefault(TITLE_FRAME_KEY, self._create_title_frame())
        self.widget_lookup.setdefault(GAME_OVER_WINDOW_KEY, self._create_game_over_window())
        self.widget_lookup.setdefault(SETTINGS_WINDOW_KEY, self._create_settings_window())
        title_frame = self.widget_lookup[TITLE_FRAME_KEY]
        title_frame.pack(expand=True)

    # I
    ## Frame 1 functionality
    def _create_title_frame(self): 
        title_frame = tk.Frame(self.master)
        new_game_button = tk.Button(title_frame, text="New game") 
        new_game_button = tk.Button(title_frame, text="New game", 
                                        command=self._begin_game)
        settings_button = tk.Button(title_frame, text="Settings", command=lambda: self._reveal_window(SETTINGS_WINDOW_KEY))
        exit_button = tk.Button(title_frame, text="Exit", command=self.master.destroy)
        ## Rendering widgets
        new_game_button.grid(row=0, column=0, sticky=tk.NSEW)
        settings_button.grid(row=1, column=0, sticky=tk.NSEW)
        exit_button.grid(row=2, column=0, sticky=tk.NSEW)
        return title_frame

    def reset_grid_GUI(self, grid_length): 
        self.widget_lookup[TITLE_FRAME_KEY].pack_forget()
        self.grid_length = grid_length
        self._create_grid_frame().pack(expand=True)
    # I END

    # II
    ## Frame 2 functionality
    def _create_grid_frame(self): 
        ## Remove old grid
        existing_grid = self.widget_lookup.get(GRID_FRAME_KEY, None)
        if existing_grid is not None: 
            existing_grid.destroy()
        grid_frame = tk.Frame(self.master)
        life_score_label = tk.Label(grid_frame)
        grid_buttons = [tk.Button(grid_frame, width=7, height=3) for _ in range(self.grid_length * self.grid_length)]
        self.widget_lookup.update({GRID_FRAME_KEY: grid_frame})
        self.widget_lookup.update({ GRID_LABEL_KEY: life_score_label })
        self.widget_lookup.update({ GRID_BUTTONS_KEY: grid_buttons })
        ## Rendering widgets
        self.update_grid_label(self.life_setting.get(), 0)
        life_score_label.grid(row=0, column=0, columnspan=self.grid_length)
        for button_index, button in enumerate(grid_buttons): 
            grid_row = floor(button_index / self.grid_length)
            grid_col = button_index % self.grid_length
            button["command"] = lambda i=grid_row, j=grid_col:E.dispatch_update(A.CLOSE, (( i,j ),))
            button.grid(row=grid_row+1, column=grid_col, sticky=tk.NSEW)
        return grid_frame

    def update_grid_label(self, life, score): 
        self.widget_lookup[GRID_LABEL_KEY]["text"] = f"Life: {life}{' ':3}Score: {score}"

    def update_grid_button(self, to_state:A, coords): 
        for i, j in coords: 
            logging.info(f"{to_state} button coords at: {i},{j}")
            button_index = i * self.grid_length + j
            self.widget_lookup[GRID_BUTTONS_KEY][button_index]["text"] = "pika" if to_state.value else ""

    def grid_game_over(self, score): 
        for button in self.widget_lookup[GRID_BUTTONS_KEY]:
            button.config(state="disabled", bg="grey")
        self._reveal_window(GAME_OVER_WINDOW_KEY)
        label_text = (
            f"Game over!\n"
            f"Final Score: {score}"
        )
        self.widget_lookup[GAME_OVER_LABEL_KEY]["text"] = label_text
    # II END

    # III
    ## Frame 3 functionality
    def _create_game_over_window(self): 
        game_over_frame = self._create_window()
        label_text = (
            f"Game over!\n"
            f"Final Score: number_undefined"
        )
        label = tk.Label(game_over_frame, text=label_text)
        self.widget_lookup.setdefault(GAME_OVER_LABEL_KEY, label)
        play_again_button = tk.Button(game_over_frame, text="Play again!", command=self._to_play_again)
        title_button = tk.Button(game_over_frame, text="Return to main menu", command=lambda: self._to_play_again(False))
        ## Rendering widgets
        label.grid(row=0, column=0, sticky=tk.NSEW)
        play_again_button.grid(row=1, column=0, sticky=tk.NSEW)
        title_button.grid(row=2, column=0, sticky=tk.NSEW)
        return game_over_frame.master

    def _to_play_again(self, yes=True):
        self._withdraw_window(GAME_OVER_WINDOW_KEY)
        if yes: 
            self._begin_game()
        else: 
            self.widget_lookup[GRID_FRAME_KEY].pack_forget()
            self.widget_lookup[TITLE_FRAME_KEY].pack(expand=True)
    # III END

    # IV
    ## Frame 4 functionality
    def _create_settings_window(self): 
        settings_frame = self._create_window()
        difficulty_label = tk.Label(settings_frame, text="Difficulty:")
        self.difficulty_setting.set(C.EZ.value)
        difficulty_radio_buttons = [ 
            tk.Radiobutton(settings_frame, variable=self.difficulty_setting, 
                            value=radio_enum.value, text=radio_enum.name.capitalize()) 
                for radio_enum in C]
        difficulty_radio_buttons[0].select()
        self.life_setting.set(3)
        life_label = tk.Label(settings_frame, text="Life:")
        life_spinner = tk.Spinbox(settings_frame, width=5, from_=1, to=9, textvariable=self.life_setting)
        save_settings_button = tk.Button(settings_frame, text="Save", 
                                            command=self._save_settings)
        ## Rendering widgets
        grid_row = 0
        difficulty_label.grid(row=grid_row, column=0, sticky=tk.W)
        grid_row += 1
        for radio in difficulty_radio_buttons:
            radio.grid(row=grid_row, column=0, sticky=tk.W)
            grid_row += 1
        life_label.grid(row=grid_row, column=0, sticky=tk.W)
        life_spinner.grid(row=grid_row, column=1)
        grid_row += 1
        save_settings_button.grid(row=grid_row, column=0, columnspan=2, sticky=tk.NSEW)
        return settings_frame.master

    def _save_settings(self): 
        self._withdraw_window(SETTINGS_WINDOW_KEY)
        
    def _get_difficulty_setting_value(self): 
        d = self.difficulty_setting.get()
        logging.info(f"difficulty -> value: {d}, name: {C(d).name}")
        return d

    def get_life_setting_value(self): 
        return self.life_setting.get()
    # IV END

    def _create_window(self): 
        """
        Creates a new toplevel. 
        Returns a frame
        """
        window = tk.Toplevel(self.master)
        window.protocol("WM_DELETE_WINDOW", lambda: None)
        window.withdraw()
        frame = tk.Frame(window)
        frame.pack(expand=True)
        return frame

    def _reveal_window(self, key): 
        self.widget_lookup[key].deiconify()
    
    def _withdraw_window(self, key): 
        self.widget_lookup[key].withdraw()
    
    def _begin_game(self):  
            E.dispatch_reset(self._get_difficulty_setting_value())

    def draw_GUI(self):
        self.master.mainloop()


class E:
    """EVENT HANDLERS"""
    update_listeners = []
    reset_liseners = []

    @classmethod
    def register_update_listener(cls, callable): 
        cls.update_listeners.append(callable)

    @classmethod
    def dispatch_update(cls, to_state: A, coords): 
        logging.debug(f"{to_state.name} coords: {coords}")
        for listener in cls.update_listeners: 
            listener(to_state, coords)

    @classmethod
    def register_reset_listener(cls, callable): 
        cls.reset_liseners.append(callable)

    @classmethod
    def dispatch_reset(cls, settings): 
        logging.debug(f"New game with difficulty settings at: {settings}")
        for listener in cls.reset_liseners:
            listener(settings)
            

class F: 
    def __init__(self, root_gui) -> None:
        self.grid = B()
        self.GUI = D(root_gui)
        self.score = 0 
        self.life = 0 
        E.register_reset_listener(self.reset_timer)
        E.register_reset_listener(self.grid.reset)
        E.register_reset_listener(self.GUI.reset_grid_GUI)
        E.register_update_listener(self.grid.update)
        E.register_update_listener(self.GUI.update_grid_button)
        self.is_game_over = False
        self.GUI.draw_GUI()

    def reset_timer(self, difficulty_settings_value): 
        difficulty = C(difficulty_settings_value)
        max_random_count = difficulty.max_mole_count()
        timer_change_rate = difficulty.timer_change_rate()
        self.score = 0
        self.life = self.GUI.get_life_setting_value()
        self.is_game_over = False
        logging.info(f"new game -> difficulty:{difficulty.name}")
        thread = threading.Thread(target=self._timer_logic, args=(max_random_count, timer_change_rate))
        thread.start()

    def _timer_logic(self, count, time_adj): 
        logging.info(f"timer started: count:{count}, rate:-{time_adj}")
        period = 3 + time_adj
        while not self.is_game_over: 
            time.sleep(1)
            coords = self.grid.get_random_coordinates(count)
            E.dispatch_update(A.OPEN, coords)
            time.sleep(period)
            period = max(1, period - time_adj)
            score, penalty = self.grid.calculate_outcome(coords)
            E.dispatch_update(A.CLOSE, coords)
            self.life = 0 if self.life <= penalty else self.life - penalty 
            self.score += score 
            self.GUI.update_grid_label(self.life, self.score)
            if self.life <= 0: 
                self._game_over()

    def _game_over(self): 
        self.is_game_over = True
        self.GUI.grid_game_over(self.score)


if __name__ == "__main__": 
    root = tk.Tk()
    f = F(root)
        
