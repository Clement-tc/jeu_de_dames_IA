from checker_model import CheckerModel
from piece import Piece
import tqdm
import math
import time 


avg_array=[]
dimentions_to_test=[7,8,9,10]
rows_filling=[1,2]
list_depth=[2,3,4,5]
number_games_to_test = 100
wins_player_1 = 0
wins_player_2 = 0

for depth in list_depth:
    avg_array.append([[],[]])
    for rows in rows_filling:
        for dimention in dimentions_to_test:
            start_time = time.time()
            for _ in tqdm.tqdm(range(number_games_to_test)):

                ROWS=int(dimention)
                COLS=int(dimention)
                FILLED_ROWS=int(rows)

                checker_model_object = CheckerModel()

                while True:

                    checker_model_object.ia_move(model="random")
                    game_state = checker_model_object.check_game_state()
                    if game_state == "draw_game":
                        break
                    
                    elif game_state == 1:
                        wins_player_1 +=1
                        break


                    checker_model_object.ia_move(model="minimax",depth_minimax=depth)
                    game_state = checker_model_object.check_game_state()
                    if game_state == "draw_game":
                        break
                    
                    elif game_state == -1:
                        wins_player_2 +=1
                        break
            number_of_pieces=0
            for row in range(rows):
                for dim in range(dimention):
                    if (row*dimention+dim) % 2 != 0:
                        number_of_pieces+=1

            avg_time=(time.time() - start_time)/number_games_to_test
            avg_array[depth-list_depth[0]][0].append(avg_time)
            avg_array[depth-list_depth[0]][1].append(number_of_pieces)
print(avg_array)
print("--- %s seconds ---" % (time.time() - start_time))
print(f"player 1  wins {wins_player_1}")
print(f"player 2  wins {wins_player_2}")
print(f"draws {number_games_to_test - wins_player_1 - wins_player_2}")