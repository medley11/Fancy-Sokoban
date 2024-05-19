import tkinter as tk
from tkinter import messagebox, filedialog
from typing import Callable
from model import SokobanModel, Tile, Entity
from a2_support import *
from a3_support import *

class FancyGameView(AbstractGrid):
    """Abstract view for a game grid with maze tiles, entities, and a player."""
    def __init__(self, master: tk.Frame | tk.Tk, dimensions: tuple[int, int]
                 , size: tuple[int, int], **kwargs) -> None:
        """
        Initialize a FancyGameView instance.

        Args:
            master (tk.Frame or tk.Tk): The parent frame or Tk root window.
            dimensions (tuple[int, int]): A tuple containing the dimensions 
            (rows, columns) of the grid.
            size (tuple[int, int]): A tuple containing the size (width, 
            height) of the grid cells.
            **kwargs: Additional keyword arguments to pass to the parent class
            constructor.
        """
        super().__init__(master, dimensions, size, **kwargs)
        self._cache = {}

    def display(self, maze: Grid, entities: Entities, player_position: 
                Position ):
        """
        Display the game grid with maze tiles, entities, and player position.

        Args:
            maze (Grid): The grid representing the game maze.
            entities (Entities): A dictionary of entities and their positions.
            player_position (Position): The current position of the player.
        """
        self.clear() # Clears the game view before recreating the new view
        for i, row in enumerate(maze):
            for j, tile in enumerate(row):
                midpoint = self.get_midpoint((i, j))

                # If there's a tile at this location, render it
                if tile.get_type() == FLOOR:
                    tile_image = get_image("images/Floor.png",
                                                 self.get_cell_size(),
                                                 self._cache)
                else: 
                    tile_image = get_image(f"images/{tile}.png",
                                                 self.get_cell_size(),
                                                 self._cache)
                self.create_image(midpoint, image=tile_image)

                # If there's an entity at this location, render it
                if (i, j) in entities:
                    entity = entities[(i, j)].get_type()
                    entity_image = get_image(f"images/{entity}.png",
                                             self.get_cell_size(),
                                             self._cache)
                    # Display the entity image on top of the tile image
                    self.create_image(midpoint, image=entity_image)

                    # Display the crate strength in text
                    if entity == CRATE:
                        self.create_text((midpoint[0], midpoint[1]-15),
                                         text=\
                                         f"{entities[(i, j)].get_strength()}",
                                         font=CRATE_FONT)
                # If there's a player at this location, render it
                if (i,j) == player_position:
                    self.create_image(self.get_midpoint(player_position),
                                      image= get_image("images/P.png",
                                                       self.get_cell_size(),
                                                       self._cache))

class FancyStatsView(AbstractGrid):
    """Abstract view for displaying player statistics in a grid format."""
    DIMENSIONS = (3,3)
    SIZE = (MAZE_SIZE+SHOP_WIDTH, STATS_HEIGHT)
    def __init__(self, master: tk.Tk | tk.Frame) -> None:
        """
        Initialize a FancyStatsView instance.

        Args:
            master (tk.Tk or tk.Frame): The parent Tkinter root for this view
        """
        super().__init__(master, self.DIMENSIONS, self.SIZE)

    def draw_stats(self, moves_remaining: int, strength: int, 
                   money: int) -> None:
        """
        Draw and display player statistics on the grid.

        Args:
            moves_remaining (int): The number of moves left for the player.
            strength (int): The player's current strength value.
            money (int): The player's current amount of money.
        """
        self.clear() # Clears the view to update with new statistics
        self.create_text(self.get_midpoint((0,1)),
                         text="Player Stats",
                         font=TITLE_FONT)
        
        # Prepare the statistics text to display
        texts = [
            ["Moves remaining:", "Strength:", "Money:"],
            [f"{moves_remaining}", f"{strength}", f"${money}"]]
        # Loop to create and display the statistics text
        for i in range(1,3):
            for j in range(3):
                self.create_text(self.get_midpoint((i,j)),
                                 text=f"{texts[i-1][j]}")
    
class Shop(tk.Frame):
    """Abstract representation of a shop where players can buy items."""
    def __init__(self, master: tk.Frame) -> None:
        """
        Initialize a Shop instance.

        Args:
            master (tk.Frame): The parent frame in which the shop is placed.
        """
        super().__init__(master)
        self.master = master
        #Creates the main title 'Shop'
        self.pack(fill='x')
        title_label = tk.Label(self, text="Shop", font=TITLE_FONT)
        title_label.pack()

    def create_buyable_item( self, item: str, amount: int, 
                            callback: Callable[[], None]) -> None:
        """
        Create a new buyable item representation in the shop.

        Args:
            item (str): The item identifier ('S' for Strength, 'M' for Move, 
            'F' for Fancy).
            amount (int): The cost of the item.
            callback (Callable[[], None]): A function to execute when the 
            item is bought.
        """
        # Create a new item frame
        item_frame = tk.Frame(self)
        item_frame.pack()
        # Label containing the name of the item and cost
        if item == 'S':
            potion = 'Strength'
        elif item == 'M':
            potion = 'Move'
        elif item == 'F':
            potion = 'Fancy'
        item_label = tk.Label(item_frame, text=f"{potion} Potion: ${amount}")
        item_label.pack(side=tk.LEFT)
        # Button for buying the item
        buy_button = tk.Button(item_frame, text="Buy", command=callback)
        buy_button.pack(side=tk.RIGHT)

class FancySokobanView():
    """Graphical view for an Extra Fancy Sokoban game with a game view, 
    stats view, and shop view."""
    def __init__(self, master: tk.Tk, dimensions: tuple[int, int], 
                 size: tuple[int,int]) -> None:
        """
        Initialize a FancySokobanView instance.

        Args:
            master (tk.Tk): The Tkinter root window.
            dimensions (tuple[int, int]): A tuple containing the dimensions 
            (rows, columns) of the game grid.
            size (tuple[int, int]): A tuple containing the size (width, 
            height) of the game grid cells.
        """
        self._master = master
        self._master.title("Extra Fancy Sokoban")

        #Initialise the game view, stats view, and shop view
        self._frame = tk.Frame(master) #To pack the game and shop view
        self._view = FancyGameView(self._frame, dimensions, size)
        self._stats = FancyStatsView(master)
        self._shop = Shop(self._frame)
        
        #Create the banner for the game
        banner = tk.Label(master, 
                          image = get_image('images/banner.png', 
                                            [MAZE_SIZE + SHOP_WIDTH, 
                                             BANNER_HEIGHT], 
                                             self._view._cache))
        #Packs the widgets into the window in the right order
        banner.pack(side=tk.TOP)
        self._view.pack(side=tk.LEFT)
        self._shop.pack(side=tk.RIGHT, anchor=tk.N)
        self._frame.pack(side=tk.TOP)
        self._stats.pack(side=tk.TOP)
        
    def display_game(self, maze: Grid, entities: Entities, 
                     player_position: Position) -> None:
        """
        Display the game grid with maze tiles, entities, and player position.

        Args:
            maze (Grid): The grid representing the game maze.
            entities (Entities): A dictionary of entities and their positions.
            player_position (Position): The current position of the player.
        """
        self._view.display(maze, entities, player_position)

    def display_stats(self, moves: int, strength: int, money: int) -> None:
        """
        Display player statistics in the stats view.

        Args:
            moves (int): The number of moves remaining for the player.
            strength (int): The player's current strength value.
            money (int): The player's current amount of money.
        """
        self._stats.draw_stats(moves, strength, money)

    def create_shop_items(self, 
                          shop_items: dict[str, int], 
                          button_callback: Callable[[str], None] 
                          | None = None ) -> None:
        """
        Create buyable items in the shop view.

        Args:
            shop_items (dict[str, int]): A dictionary of item identifiers 
            and their prices.
            button_callback (Callable[[str], None] | None): A callback 
            function to execute when items are bought.
        """
        for item, price in shop_items.items():
            # Create a callback function using a lambda
            callback_function = lambda item=item: button_callback(item)
            # Create the item in the shop with the callback
            self._shop.create_buyable_item(item, price, callback_function)

class ExtraFancySokoban(): 
    """The main class for the Extra Fancy Sokoban game, combining the model 
    and view."""
    def __init__(self, root: tk.Tk, maze_file: str) -> None:
        """
        Initialize the ExtraFancySokoban instance.

        Args:
            root (tk.Tk): The Tkinter root window.
            maze_file (str): The file containing the maze layout.
        """
        # Initializes the model and the view
        self.root = root
        self._model = SokobanModel(maze_file)
        self._view = FancySokobanView(root, self._model.get_dimensions(),
                                      [MAZE_SIZE, MAZE_SIZE])
        # Creates the initial game state
        self.redraw()
        self._view.create_shop_items(self._model.get_shop_items(),
                                     button_callback=self.buy_item_redraw)
        # Binds keypresses to a function
        root.bind("<KeyPress>", self.handle_keypress)

    def buy_item_redraw(self, item:str):
        """
        Handle buying an item and redraw the game view.

        Args:
            item (str): The item identifier to purchase.
        """
        if self._model.attempt_purchase(item):
           self.redraw()
           
    def redraw(self) -> None:
        """Redraw the game view and display updated stat information."""
        self._view.display_game(self._model.get_maze(),
                                self._model.get_entities(),
                                self._model.get_player_position())
        self._view.display_stats(self._model.get_player_moves_remaining(),
                                 self._model.get_player_strength(),
                                 self._model.get_player_money())
       
    def handle_keypress(self, event: tk.Event) -> None:       
        """
        Handle keypress events for player movement and game actions.

        Args:
            event (tk.Event): The keypress event.
        """
        if event.keysym: # Takes the key pressed and runs it through the model
            if self._model.attempt_move(event.keysym): # Confirms if it's valid
                self.redraw()
                self.root.update() # Ensures redraw is implemented

       #Checks if player has won, and if they want to play again
        if self._model.has_won() == True:
            if messagebox.askyesno('Play again?','You won! Play again?'):
                self._model.reset() # resets the game state
                self.redraw()
            else:
                self.root.destroy() #terminates gracefully
       #Checks if player has lost, and if they want to play again
        elif self._model.get_player_moves_remaining() == 0 and \
             self._model.has_won() == False:
            if messagebox.askyesno('Play again?', 'You lost! Play again?'):
                self._model.reset() # resets the game state
                self.redraw()
            else:
                self.root.destroy() #terminates gracefully
   
def play_game(root: tk.Tk, maze_file: str) -> None:
    """
    Start and play the Extra Fancy Sokoban game.

    Args:
        root (tk.Tk): The Tkinter root window for the game.
        maze_file (str): The path to the maze layout file.
    """
    controller = ExtraFancySokoban(root, maze_file)
    root.mainloop()
    return

def main() -> None:
    """Initializes the game by creating a Tkinter root window and starts 
    the game within the maze file."""
    root = tk.Tk()
    play_game(root, maze_file = 'maze_files/maze4.txt')


if __name__ == "__main__":
    main()
