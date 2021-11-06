import gamelib
import random
import math
from sys import maxsize

class AlgoStrategy(gamelib.AlgoCore):
    def __init__(self):
        super().__init__()
        seed = random.randrange(maxsize)
        random.seed(seed)
        gamelib.debug_write('Random seed: {}'.format(seed))

    def on_game_start(self, config):
        """ 
        Read in config and perform any initial setup here 
        """
        gamelib.debug_write('Configuring your custom algo strategy...')
        self.config = config
        global WALL, SUPPORT, TURRET, SCOUT, DEMOLISHER, INTERCEPTOR, MP, SP
        WALL = config["unitInformation"][0]["shorthand"]
        SUPPORT = config["unitInformation"][1]["shorthand"]
        TURRET = config["unitInformation"][2]["shorthand"]
        SCOUT = config["unitInformation"][3]["shorthand"]
        DEMOLISHER = config["unitInformation"][4]["shorthand"]
        INTERCEPTOR = config["unitInformation"][5]["shorthand"]
        MP = 1
        SP = 0
        self.focus = random.randrange(2)
        self.block = 1 - self.focus
        self.scored_on_locations = []

    def on_turn(self, turn_state):
        """
        This function is called every turn with the game state wrapper as
        an argument. The wrapper stores the state of the arena and has methods
        for querying its state, allocating your current resources as planned
        unit deployments, and transmitting your intended deployments to the
        game engine.
        """
        game_state = gamelib.GameState(self.config, turn_state)
        gamelib.debug_write('Performing turn {} of your custom algo strategy'.format(game_state.turn_number))
        game_state.suppress_warnings(True)  #Comment or remove this line to enable warnings.

        self.strategy(game_state)

        game_state.submit_turn()

    def strategy(self, game_state):
        self.build_defences(game_state)

        spawn_location_options = [[25, 11], [2, 11]]
        best_location = spawn_location_options[self.focus]
        

        if not game_state.contains_stationary_unit([5, 11]) or not game_state.contains_stationary_unit([22, 11]):
            if game_state.turn_number == 4:
                game_state.attempt_spawn(DEMOLISHER, best_location, 4)
            if game_state.get_resource(MP) >= 10 + math.log(game_state.turn_number + 1) and game_state.turn_number > 4:
                game_state.attempt_spawn(SCOUT, best_location, int(game_state.get_resource(MP)) - 6)
                game_state.attempt_spawn(DEMOLISHER, best_location, 2)
            

    def build_defences(self, game_state):
        primary_turret_locations = [[3, 12], [24, 12]]
        game_state.attempt_spawn(TURRET, primary_turret_locations)

        gap_locations = [[5, 11], [22, 11]]
        left_walls_alert = [[3, 12], [0, 13], [1, 13], [2, 13], [3, 13], [4, 12], [5, 11], [6, 11]]
        right_walls_alert = [[24, 12], [27, 13], [26, 13], [25, 13], [24, 13], [23, 12], [22, 11], [21, 11]]
        walls_alert = [left_walls_alert, right_walls_alert]
        broke = []

        if game_state.turn_number != 0:
            for wall in walls_alert[self.block]:
                if not game_state.contains_stationary_unit(wall):
                    broke.append(wall)
        
        if len(broke) != 0:
            game_state.attempt_remove(gap_locations[self.block])
            self.focus = self.block
            self.block = 1 - self.focus
            game_state.attempt_spawn(WALL, gap_locations[self.block])

        wall_locations = [[0, 13], [1, 13], [2, 13], [3, 13], [24, 13], [25, 13], [26, 13], [27, 13], [4, 12], [23, 12], [6, 11], [21, 11], [7, 10], [20, 10], [8, 9], [19, 9], [9, 8], [18, 8], [10, 7], [17, 7], [11, 6], [16, 6], [12, 5], [13, 5], [14, 5], [15, 5]]
        game_state.attempt_spawn(WALL, wall_locations)

        primary_defensive_wall_locations = [[3, 13], [24, 13], [4, 12], [23, 12]]
        game_state.attempt_upgrade(primary_defensive_wall_locations)

        if self.focus == 0:
            secondary_turret_location = [6, 10]
            game_state.attempt_spawn(TURRET, secondary_turret_location)
            secondary_defensive_wall_locations = [[6, 11], [7, 10]]
            game_state.attempt_upgrade(secondary_defensive_wall_locations)
        else:
            secondary_turret_location = [21, 10]
            game_state.attempt_spawn(TURRET, secondary_turret_location)
            secondary_defensive_wall_locations = [[21, 11], [20, 10]]
            game_state.attempt_upgrade(secondary_defensive_wall_locations)

        primary_support_locations = [[11, 7], [12, 7], [13, 7], [14, 7]]
        for support_location in primary_support_locations:
            if game_state.get_resource(SP) >= 6:
                game_state.attempt_spawn(SUPPORT, support_location)
                game_state.attempt_upgrade(support_location)

        if self.focus == 0:
            tertiary_turret_location = [[2, 12]]
            game_state.attempt_spawn(TURRET, tertiary_turret_location)
            tertiary_defensive_wall_locations = [[8, 9], [2, 13]]
            game_state.attempt_upgrade(tertiary_defensive_wall_locations)

        else:
            tertiary_turret_location = [[25, 12]]
            game_state.attempt_spawn(TURRET, tertiary_turret_location)
            tertiary_defensive_wall_locations = [[19, 9], [25, 13]]
            game_state.attempt_upgrade(tertiary_defensive_wall_locations)

        secondary_support_locations = [[15, 7], [16, 7]]
        for support_location in secondary_support_locations:
            if game_state.get_resource(SP) >= 6:
                game_state.attempt_spawn(SUPPORT, support_location)
                game_state.attempt_upgrade(support_location)
        
        if self.focus == 0:
            final_turret_locations = [[7, 9], [3, 11], [4, 11]]
            game_state.attempt_spawn(TURRET, final_turret_locations)
            remove_turret_locations = [[20, 9], [23, 11], [24, 11]]
            game_state.attempt_remove(remove_turret_locations)
        else:
            final_turret_locations = [[20, 9], [23, 11], [24, 11]]
            game_state.attempt_spawn(TURRET, final_turret_locations)
            remove_turret_locations = [[7, 9], [3, 11], [4, 11]]
            game_state.attempt_remove(remove_turret_locations)
        
        tertiary_support_locations = [[12, 6], [13, 6], [14, 6], [15, 6], [13, 8], [14, 8], [12, 8], [15, 8], [11, 8], [16, 8]]
        for support_location in tertiary_support_locations:
            if game_state.get_resource(SP) >= 6:
                game_state.attempt_spawn(SUPPORT, support_location)
                game_state.attempt_upgrade(support_location)

if __name__ == "__main__":
    algo = AlgoStrategy()
    algo.start()
