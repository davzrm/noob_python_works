# !python3 

# Tic Tac Toe
# Backend with numpy
# Frontend with Tkinter

import numpy as np 
import pyinputplus as pyp
import logging 
import tkinter as tk
import tkinter.font as font
from enum import Enum

LOGGING_FORMAT = "{levelname} At line number {lineno} -> {message}"
logging.basicConfig(level=logging.DEBUG, format=LOGGING_FORMAT, style="{")
logging.disable(logging.CRITICAL)

class Player(Enum): 
    PLAYER_1 = 1
    PLAYER_2 = -1


class A:
    def __init__(self) -> None:
        self.board = np.zeros((3,3)) 
        logging.debug(f"Shape of board is { self.board.shape }")

    def player_move(self, player_value, coord): 
        self.board[coord] = player_value

    def is_game_end(self, player_value): 
        player_vector = [ player_value ] * 3
        winning_value = 3 * player_value ** 2
        ## Check if player has won
        dot_row_values = self.board @ player_vector
        dot_column_values = self.board.T @ player_vector
        dot_diagonal_values = np.stack((self.board.diagonal(), np.fliplr(self.board).diagonal())) @ player_vector
        logging.debug(f"The win table: \n{np.concatenate((dot_row_values,  dot_column_values, dot_diagonal_values ))}" )
        logging.debug(f"Winning value: {winning_value}" )
        is_win = np.any(  np.concatenate((dot_row_values,  dot_column_values, dot_diagonal_values )) == winning_value) 
        ## Check if game has ended
        is_end = True if is_win else np.all(self.board)
        return is_end, is_win
    
    def reset(self): 
        self.board = np.zeros((3,3)) 


BUTTON_KEY = "button" 
LABEL_KEY = "label"
START_TEXT = "Click anywhere to begin!"
ROOT_WIDTH = 300
ROOT_HEIGHT = 400
class B: 
    def __init__(self, board_holder: A, gui_root) -> None:
        self.board_holder = board_holder
        self.root = gui_root
        self.gui_lookup = {}
        self.players = [Player.PLAYER_1, Player.PLAYER_2]
        self.player_symbol_lookup = {
            self.players[0] : ("Player 1", "O" ), 
            self.players[1] : ("Player 2", "X" ), 
        }
        self.round_counter = 0
        self.current_player = self.players[0]
        self._init_gui()

    def _set_current_player(self, reset=False): 
        """
        Decision for which player is based on (self.round_counter % 2)
        
            Parameters:
                reset (bool): If True, will assign self.round_counter to 0
        """
        self.round_counter = self.round_counter + 1 if reset is False else 0
        self.current_player = self.players[self.round_counter % 2]

    def _init_gui(self): 
        board_shape = self.board_holder.board.shape
        self.root.title("EZ Tic-Tac-Toe")
        root_width = ROOT_WIDTH
        root_height = ROOT_HEIGHT
        self.root.geometry(f"{root_width}x{root_height}")
        ## creating buttons and label
        logging.debug(f"width and height of buttons are both equal to {round(root_width/3)}")
        buttons = [tk.Button(self.root, width=round(root_width/3), height=round(root_width/3), text="-", font=font.Font(size=20)) 
                    for _ in range(board_shape[0] * board_shape[1])]
        self.gui_lookup.setdefault(BUTTON_KEY, buttons)
        logging.debug(f"GUI buttons: {buttons}")
        label_header = tk.Button(self.root, text=START_TEXT)
        self.gui_lookup.setdefault(LABEL_KEY, label_header)
        ## rendering the board
        for i in range(board_shape[0]):
            self.root.rowconfigure(i, weight=1)
            self.root.columnconfigure(i, weight=1)
            for j in range(board_shape[1]):
                button_index = i * board_shape[0] + j
                button = buttons[button_index]
                button["command"] = lambda i=i, j=j, index=button_index:self._button_clicked(i, j, buttons[index])
                button.grid(row=i, column=j, sticky=tk.NSEW)
                logging.debug(f"Button at {i},{j}: {button}")
        label_header.grid(row=board_shape[0], columnspan=board_shape[1], sticky=tk.NSEW)
        self.root.mainloop()

    def _button_clicked(self, axis_0, axis_1, button): 
        self.board_holder.player_move(self.current_player.value, (axis_0,axis_1))
        player_symbol = self.player_symbol_lookup[self.current_player][1]
        button.config(text=f"{player_symbol}", state=tk.DISABLED)
        is_end, is_win = self.board_holder.is_game_end(self.current_player.value)
        self._check_end(is_end, is_win)

    def _check_end(self, is_end, is_win): 
        label = self.gui_lookup[LABEL_KEY]
        label_text = ""
        if is_end: 
            for button in self.gui_lookup[BUTTON_KEY]: 
                button["state"] = tk.DISABLED
            player_name = self.player_symbol_lookup[self.current_player][0]
            label_text = ( 
                f"{player_name} wins! Click here to play again!" 
                if is_win
                else f"Draw! Click here to play again!"
            )
            label["command"] = self._reset_game
        else: 
            self._set_current_player()
            player_name = self.player_symbol_lookup[self.current_player][0]
            label_text = f"{player_name}'s turn"
        label["text"] = label_text

    def _reset_game(self):
        self._set_current_player(True)
        self.board_holder.reset()
        for button in self.gui_lookup[BUTTON_KEY]: 
            button.config(text="-", state=tk.NORMAL)
        self.gui_lookup[LABEL_KEY].config(command=None, text=START_TEXT)

if __name__ == "__main__": 
    root = tk.Tk()
    game = B(A(), root)
