from config_file import *
from utils import is_in_bound

from move import Move
from piece import Piece


import numpy
import math

import copy
from itertools import product
import random



class CheckerModel:
	# detection du chemin le plus long
	# créer un fonction qui va permettre l'intégration du bot qui pourra prendre le role du joueur 2:
		# MiniMax 
		# MonteCarlo
		# Neural Network

	def __init__(self, checker_grid=None,custom_ROWS=ROWS,custom_filled_row=FILLED_ROWS):
		global ROWS
		global COLS
		global FILLED_ROWS
		ROWS=custom_ROWS
		COLS=custom_ROWS
		FILLED_ROWS=custom_filled_row


		if checker_grid is None:
			self.create_grid()

		else:
			self.checker_grid = checker_grid
		self.turn = 1 # 1 : pour le joueur 1 et -1 pour le joueur 2

		self.dict_of_possible_moves = self.get_possible_moves()

		self.history = []


	def create_grid(self):

		self.checker_grid = [[0 for _ in range(COLS)] for _ in range(ROWS)]


		for row in range(0, ROWS):
			for col in range(0, COLS):
				if (row + col) % 2 == 0:
					self.checker_grid[row][col]= math.nan

		for row in range(0, ROWS):
			for col in range(0, COLS):
				if (row + col) % 2 != 0:
					if row < FILLED_ROWS: # joueur 2
						self.checker_grid[row][col] = Piece(row, col, player=-1)

					elif row > ROWS - FILLED_ROWS - 1: # joueur 2
						self.checker_grid[row][col] = Piece(row, col, player=1)




	def move_piece(self, selected_piece_position, move_position):
		self.history.append(copy.deepcopy(self.checker_grid))
		
		row_selection, col_selection = selected_piece_position

		
		current_piece = self.checker_grid[row_selection][col_selection]

		current_piece.row, current_piece.col = move_position

		if (self.turn == 1 and current_piece.row == 0) or (self.turn == -1 and current_piece.row == ROWS -1):
			current_piece.become_king()

		self.checker_grid[row_selection][col_selection] = 0
		self.checker_grid[current_piece.row][current_piece.col] = current_piece


		for possible_move_object in self.dict_of_possible_moves[selected_piece_position]:
			if possible_move_object.get_final_position() == move_position:
				
				for piece_position_to_attact in possible_move_object.list_attacked_enemy_pieces:
					row_to_attack, col_to_attack = piece_position_to_attact
					self.checker_grid[row_to_attack][col_to_attack] = 0
		
		self.turn = -1 if self.turn==1 else 1
		self.dict_of_possible_moves = self.get_possible_moves()



	def undo_last_action(self):
		if self.history:
			self.checker_grid = self.history[-1]
			self.history = self.history[:-1]
			self.turn = -1 if self.turn==1 else 1
			self.dict_of_possible_moves = self.get_possible_moves()



	def get_cell_state(self, row, col):
		"""
		3 cas :
			- la cellule est vide                                      : accessible
			- la cellule est prise avec une pièce du joueur en cours   : inacessible
			- la cellule est prise avec une pièce du joueur adverse	   : on devra observer l'état des cellules en haut à droite/gauche de celle-ci
		"""
		if not is_in_bound(row, col):
			return "out_of_bound" # rien à faire
		
		elif self.checker_grid[row][col] == 0:
			return "accessible" # déplacement simple
		
		elif type(self.checker_grid[row][col]) == Piece:
			piece = self.checker_grid[row][col]
			
			if piece.player == self.turn:
				return "not_accessible" # rien à faire
			
			else : 
				return "enemy" # là ou on va gérer l'attaque d'une pièce adverse



	def get_possible_moves(self):
		dict_of_all_moves = dict()

		for row, col in product(range(0, ROWS), range(0, COLS)):
			if type(self.checker_grid[row][col]) == Piece:

				current_piece = self.checker_grid[row][col]

				if current_piece.player == self.turn:

					depth, all_moves_for_current_piece = self.get_possible_moves_for_current_piece(current_piece, depth=0, all_moves_for_current_piece=[])
					dict_of_all_moves[(row, col)] = depth, all_moves_for_current_piece


		dict_of_possible_moves = {}
		max_depth = 0

		for piece, (depth, possible_moves_for_current_piece) in dict_of_all_moves.items():
			if not possible_moves_for_current_piece:
				pass

			elif depth > max_depth:
				max_depth = depth
				dict_of_possible_moves = {piece : possible_moves_for_current_piece}
			
			elif depth == max_depth:
				dict_of_possible_moves[piece] = possible_moves_for_current_piece
		


		return dict_of_possible_moves



	def get_possible_moves_for_current_piece(self, current_piece, depth, all_moves_for_current_piece):

		row, col = current_piece.row, current_piece.col

		cells_to_check = current_piece.get_cells_to_check()


		for row_to_check, col_to_check in cells_to_check:
			
			stop_verify = False
			for row_to_verify in range(row, row_to_check, 1 if row_to_check > row else -1):
				for col_to_verify in range(col, col_to_check, 1 if col_to_check > col else -1):
					if type(self.checker_grid[row_to_verify][col_to_verify]) == Piece and row_to_verify != row and col_to_verify != col:
						stop_verify = True
			

			if stop_verify:
				pass

			else:
				cell_state =  self.get_cell_state(row_to_check, col_to_check)

				# déplacement simple
				if cell_state == "accessible" and depth == 0 and (row_to_check - row != self.turn or current_piece.king):
					move_object = Move(initial_piece_position = (row, col),\
										 list_piece_positions = [(row_to_check, col_to_check)],\
										 list_attacked_enemy_pieces = [])

					all_moves_for_current_piece.append(move_object)
				


				# déplacement en profondeur
				elif cell_state == "enemy":
					row_arrival = row_to_check + 1 if row_to_check  > row else row_to_check -1
					col_arrival = col_to_check + 1 if col_to_check  > col else col_to_check -1


					if self.get_cell_state(row_arrival, col_arrival) == "accessible" :

						attacked_piece = self.checker_grid[row_to_check][col_to_check]

						self.checker_grid[row][col] = 0
						self.checker_grid[row_to_check][col_to_check] = 0
						self.checker_grid[row_arrival][col_arrival] = current_piece
						current_piece.row, current_piece.col = row_arrival, col_arrival

						if depth == 0 :
							move_object = Move(initial_piece_position = (row, col),\
												 list_piece_positions = [(row_arrival, col_arrival)],\
												 list_attacked_enemy_pieces = [(row_to_check, col_to_check)])
							all_moves_for_current_piece.append(move_object)
						
						else:
							if depth <= all_moves_for_current_piece[-1].get_depth():
								current_move_object = all_moves_for_current_piece[-1].extract_common_deplacement(extraction_depth=depth)
								all_moves_for_current_piece.append(current_move_object)


							all_moves_for_current_piece[-1].update_move(new_piece_position=(row_arrival, col_arrival),\
																		new_attacked_enemy_piece=(row_to_check, col_to_check))


						self.get_possible_moves_for_current_piece(current_piece, depth+1, all_moves_for_current_piece)

						current_piece.row, current_piece.col = row, col
						self.checker_grid[row][col] = current_piece
						self.checker_grid[row_to_check][col_to_check] = attacked_piece
						self.checker_grid[row_arrival][col_arrival] = 0


		max_depth = 0
		possible_moves = []

		for current_move in all_moves_for_current_piece:
			current_move_depth = current_move.get_depth()
			
			if current_move_depth > max_depth:
				max_depth = current_move_depth
				possible_moves = [current_move]
			
			elif current_move_depth == max_depth:
				possible_moves.append(current_move)


		return max_depth, possible_moves



	def ia_move(self, model, depth_minimax = 3, to_maximise = False ,number_of_games=20,depth=10):
		if model == "random":
			selected_piece_position, move_position = self.random_model_predict()
			self.move_piece(selected_piece_position, move_position)
			
		elif model == "minimax":
			best_selected_piece_position, best_move_position = self.minimax_model_predict(depth_minimax, to_maximise=self.turn==1)
			self.move_piece(best_selected_piece_position, best_move_position)

		elif model=="monte_carlo":
			best_selected_piece_position, best_move_position = self.monte_carlo_model_predict(number_of_games=number_of_games,depth=depth,agent_turn=-self.turn)
			self.move_piece(best_selected_piece_position, best_move_position)

	def monte_carlo_model_predict(self,number_of_games,depth,agent_turn):

		best_score = best_score = float("inf") if agent_turn==1 else -float("inf")
		best_selected_piece_position, best_move_position = None, None

		possible_actions = []
		for selected_piece_position, moves in self.dict_of_possible_moves.items():
			for move in moves:
				possible_actions.append((selected_piece_position, move.get_final_position()))

		for possible_action in possible_actions:

			self.move_piece(*possible_action)
			
			score = self.monte_carlo(number_of_games=number_of_games,depth=depth,agent_turn=agent_turn)
			if agent_turn==1 and score <= best_score:
				best_score = score 
				best_selected_piece_position, best_move_position = possible_action
			if agent_turn==-1 and score >= best_score:

				best_score = score 
				best_selected_piece_position, best_move_position = possible_action

			self.undo_last_action()

		return best_selected_piece_position, best_move_position
	
	def monte_carlo(self,number_of_games,depth,agent_turn):
		sum_score=0
		for number_of_games_index in range(number_of_games):
			winedown=depth
			for depth_index in range(depth):
				game_state = self.game_score()
				if(game_state==0 or game_state==10.5 or game_state==-10.5):
					winedown=depth_index
					break
				selected_piece_position, move_position = self.random_model_predict()
				self.move_piece(selected_piece_position, move_position)

			sum_score+=self.game_score()
			for depth_index in range(winedown):
				self.undo_last_action()

		return sum_score

	def mini_carlos_model_predict(self, depth_minimax, to_maximise):
		best_score = -float("inf") if to_maximise else float("inf")
		best_selected_piece_position, best_move_position = None, None

		possible_actions = []
		for selected_piece_position, moves in self.dict_of_possible_moves.items():
			for move in moves:
				possible_actions.append((selected_piece_position, move.get_final_position()))

		for possible_action in possible_actions:

			self.move_piece(*possible_action)
			
			score = self.minimax(agent_turn=self.turn==-1, depth = depth_minimax, to_maximise = to_maximise)
			if to_maximise:
				if score >= best_score:
					best_score = score
					best_selected_piece_position, best_move_position = possible_action
			else:
				if score <= best_score:
					best_score = score 
					best_selected_piece_position, best_move_position = possible_action

			self.undo_last_action()

		return best_selected_piece_position, best_move_position

		return best_selected_piece_position, best_move_position
	
	def mini_carlos(self, agent_turn, depth, to_maximise, alpha=-float('inf'), beta=float('inf')):
		game_state = self.check_game_state()
		if game_state == "draw_game":
			return 0
	
		elif game_state == 1:
			return float("inf")

		elif game_state == -1:
			return -float("inf")

		elif game_state == "game_in_progress":
			if depth == 0: 
				return monte_carlo(self,10,5,agent_turn)

			else :
				if to_maximise:
					best_score = -float("inf") if robot_turn else float("inf")
				else:
					best_score = float("inf") if robot_turn else - float("inf")

				possible_actions = []
				for selected_piece_position, moves in self.dict_of_possible_moves.items():
					for move in moves:
						possible_actions.append((selected_piece_position, move.get_final_position()))


				for possible_action in possible_actions:
					self.move_piece(*possible_action)
					score = self.minimax(robot_turn=not robot_turn, depth=depth-1, to_maximise=to_maximise, alpha=alpha, beta=beta)
					if to_maximise:
						best_score = max(score, best_score) if robot_turn else min(score, best_score)
					else:
						best_score = min(score, best_score) if robot_turn else max(score, best_score)

					self.undo_last_action()
					
					if to_maximise and robot_turn or not (to_maximise or robot_turn):
							if best_score >= beta:
								break
							alpha = max(beta, best_score)

					elif to_maximise and not robot_turn or not to_maximise and robot_turn:
							if alpha >= best_score:
								break
							beta = min(alpha, best_score)

				return best_score

		return sum_score
	def game_score(self):
		game_state = self.check_game_state()
		if game_state == "draw_game":
			return 0
	
		elif game_state == 1:
			return 10.5 #replace by the number of pieces of a player depending on the map size

		elif game_state == -1:
			return -10.5

		elif game_state == "game_in_progress":
			return CheckerModel.evaluate_grid(self.checker_grid)

		


	def minimax_model_predict(self, depth_minimax, to_maximise):
		best_score = -float("inf") if to_maximise else float("inf")
		best_selected_piece_position, best_move_position = None, None

		possible_actions = []
		for selected_piece_position, moves in self.dict_of_possible_moves.items():
			for move in moves:
				possible_actions.append((selected_piece_position, move.get_final_position()))

		for possible_action in possible_actions:

			self.move_piece(*possible_action)
			
			score = self.minimax(robot_turn=self.turn==-1, depth = depth_minimax, to_maximise = to_maximise)
			if to_maximise:
				if score >= best_score:
					best_score = score
					best_selected_piece_position, best_move_position = possible_action
			else:
				if score <= best_score:
					best_score = score 
					best_selected_piece_position, best_move_position = possible_action

			self.undo_last_action()

		return best_selected_piece_position, best_move_position
	

	def minimax(self, robot_turn, depth, to_maximise, alpha=-float('inf'), beta=float('inf')):
		game_state = self.check_game_state()
		if game_state == "draw_game":
			return 0
	
		elif game_state == 1:
			return float("inf")

		elif game_state == -1:
			return -float("inf")

		elif game_state == "game_in_progress":
			if depth == 0: 
				return CheckerModel.evaluate_grid(self.checker_grid)

			else :
				if to_maximise:
					best_score = -float("inf") if robot_turn else float("inf")
				else:
					best_score = float("inf") if robot_turn else - float("inf")

				possible_actions = []
				for selected_piece_position, moves in self.dict_of_possible_moves.items():
					for move in moves:
						possible_actions.append((selected_piece_position, move.get_final_position()))


				for possible_action in possible_actions:
					self.move_piece(*possible_action)
					score = self.minimax(robot_turn=not robot_turn, depth=depth-1, to_maximise=to_maximise, alpha=alpha, beta=beta)
					if to_maximise:
						best_score = max(score, best_score) if robot_turn else min(score, best_score)
					else:
						best_score = min(score, best_score) if robot_turn else max(score, best_score)

					self.undo_last_action()
					
					if to_maximise and robot_turn or not (to_maximise or robot_turn):
							if best_score >= beta:
								break
							alpha = max(beta, best_score)

					elif to_maximise and not robot_turn or not to_maximise and robot_turn:
							if alpha >= best_score:
								break
							beta = min(alpha, best_score)

				return best_score


	def random_model_predict(self):

		selected_piece_position = random.choice(list(self.dict_of_possible_moves.keys()))
		move = random.choice(self.dict_of_possible_moves[selected_piece_position])

		move_position = move.get_final_position()

		return selected_piece_position, move_position



	@staticmethod
	def evaluate_grid(checker_grid, king_value=5):
		score = 0
		for row in range(0, ROWS):
			for col in range(0, COLS):
				if type(checker_grid[row][col]) == Piece:
					current_piece = checker_grid[row][col]
					score += current_piece.player * (king_value if current_piece.king else 1)
		return score



	def check_game_state(self):
		if len(self.history) >= 25:
			draw_game = True
			game_evaluation = CheckerModel.evaluate_grid(self.history[-25:])
			for checker_grid in self.history[-24:]:
				if CheckerModel.evaluate_grid(checker_grid) != game_evaluation:
					draw_game = False

			if draw_game:
				return "draw_game"
		
		if not self.dict_of_possible_moves.keys(): # si une personne doit et ne peut jouer alors elle a perdu
			return 1 if self.turn == -1 else -1
		

		else:
			return "game_in_progress"