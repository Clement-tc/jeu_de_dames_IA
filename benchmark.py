from checker_model import CheckerModel
import tqdm
import time

number_games_to_test = 20
wins_player_1 = 0
wins_player_2 = 0


start_time = time.time()


for _ in tqdm.tqdm(range(number_games_to_test)):
	checker_model_object = CheckerModel()

	while True:
		checker_model_object.ia_move(model="random",number_of_games=25,depth=10)
		game_state = checker_model_object.check_game_state()
		if game_state == "draw_game":
			break
		
		elif game_state == 1:
			wins_player_1 +=1
			break


		checker_model_object.ia_move(model="minimax",depth_minimax=3)
		game_state = checker_model_object.check_game_state()
		if game_state == "draw_game":
			break
		
		elif game_state == -1:
			wins_player_2 +=1
			break

print("--- %s seconds ---" % (time.time() - start_time))
print(f"player 1  wins {wins_player_1}")
print(f"player 2  wins {wins_player_2}")
print(f"draws {number_games_to_test - wins_player_1 - wins_player_2}")

vs_array=["random","minimax depth=3","minimax depth=4","minimax depth=5","minimax depth=6","monte_carlo number_of_games=10,depth=10"]
dimention=[""]