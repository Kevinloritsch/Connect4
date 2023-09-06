import numpy as np
import pygame
import sys
import math
import random

BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)

ROW_COUNT = 6
COL_COUNT = 7

# Whose Turn?
PLAYER = 0
AI = 1
turn = random.randint(PLAYER, AI) #Random who starts

PLAYER_PIECE = 1
AI_PIECE = 2

WINDOW_LENGTH = 4 #How wide space is to check (4 bc connect 4)

SQUARESIZE = 100 #pixels

HEIGHT = (ROW_COUNT + 1) * SQUARESIZE
WIDTH = COL_COUNT * SQUARESIZE

RADIUS = int(SQUARESIZE / 2 - 5)

def create_board():
    board = np.zeros((ROW_COUNT, COL_COUNT)) #defines a 2D array of 6x7 filled with zeroes
    return board

def drop_piece(board, row, col, piece):
    board[row][col] = piece

def is_valid_location(board, col):
    return board[ROW_COUNT - 1][col]==0 #If top row is empty, can put a piece there

def get_valid_locations(board):
    valid_locations = []
    for col in range(COL_COUNT):
        if is_valid_location(board, col):
            valid_locations.append(col)
    return valid_locations

def get_next_open_row(board, col):
    for r in range(ROW_COUNT):
        if board[r][col]==0: #counts bottom up
            return r
        
def print_board(board):
    print(np.flip(board, 0)) #upside down so looks right

def winning_move(board, piece):
    #manually checking every detail

    #horizontal
    for c in range(COL_COUNT -3): #you cant win with only 3 on the right
        for r in range(ROW_COUNT):
            if board[r][c] == piece and board[r][c+1] == piece and board[r][c+2] == piece and board[r][c+3] == piece:
                return True
    #vertical
    for c in range(COL_COUNT):
        for r in range(ROW_COUNT - 3):
            if board[r][c] == piece and board[r+1][c] == piece and board[r+2][c] == piece and board[r+3][c] == piece:
                return True
            
    #positive slope diagonal
    for c in range(COL_COUNT - 3):
        for r in range(ROW_COUNT - 3):
            if board[r][c] == piece and board[r+1][c+1] == piece and board[r+2][c+2] == piece and board[r+3][c+3] == piece:
                return True

    #negative slope diagonal
    for c in range(COL_COUNT - 3):
        for r in range(3, ROW_COUNT):#checking top down
            if board[r][c] == piece and board[r-1][c+1] == piece and board[r-2][c+2] == piece and board[r-3][c+3] == piece:
                return True
            
def draw_board(board):
    for c in range(COL_COUNT):
        for r in range(ROW_COUNT):
            pygame.draw.rect(screen, BLUE, (c*SQUARESIZE, (r+1)*SQUARESIZE, SQUARESIZE, SQUARESIZE)) #draw rect on screen, color blue (defined aboce), (x, y, height, width)
            pygame.draw.circle(screen, BLACK, (c*SQUARESIZE + SQUARESIZE/2, (r+1)*SQUARESIZE + SQUARESIZE/2), RADIUS) #draw circle on screen, black color (defined above), (position of the center, radius)
    #can't flip upside down like did before... separate loop so circles don't draw on top of eachother
    for c in range(COL_COUNT):
        for r in range(ROW_COUNT):
            if(board[r][c] == PLAYER_PIECE):
                pygame.draw.circle(screen, RED, (c*SQUARESIZE + SQUARESIZE/2, HEIGHT - (r+1)*SQUARESIZE + SQUARESIZE/2), RADIUS)
            elif(board[r][c] == AI_PIECE):
                pygame.draw.circle(screen, YELLOW, (c*SQUARESIZE + SQUARESIZE/2, HEIGHT - (r+1)*SQUARESIZE + SQUARESIZE/2), RADIUS)
            
# Minimax
def evaluate_window(window, piece): #just to cleanup
    score = 0
    opp_piece = PLAYER_PIECE
    if piece == PLAYER_PIECE:
        opp_piece = AI_PIECE

    if window.count(piece) == 4:#kinda redundant bc base case
        score += 100
    elif window.count(piece) == 3 and window.count(0) == 1:
        score += 10
    elif window.count(piece) == 2 and window.count(0) == 2:
        score += 5


    if window.count(opp_piece) == 3 and window.count(0) == 1:
        score -= 80 #can't have 4, bc then they already won
        # this says if theyre 1 away from winning, stop at all costs
        # its running the imaginary scenario right? so if its like, hey your opponent has 3 in a row with an open, thats a red flag. we dont want to leave that open
    if window.count(opp_piece) == 2 and window.count(0) == 2:
        score -= 8
    #these last two say if you go somewhere that leaves this open, that isn't good
    return score


def score_position(board, piece):

    score = 0 #minimax calc
    #very small for neg numbers

    #Horizontal Win Con
    for r in range(ROW_COUNT):
        row_array = [int(i) for i in list(board[r,:])] #i want every column in this row (gives the whole row)
        for c in range(COL_COUNT - 3):
            window = row_array[c:c+WINDOW_LENGTH] #checking 4 pieces horizontally
            score += evaluate_window(window, piece)

    #Vertical Win Con
    for c in range(COL_COUNT):
        col_array = [int(i) for i in list(board[:,c])] #i want every row in this column (gives the whole column)
        for r in range(ROW_COUNT - 3):
            window = col_array[r:r+WINDOW_LENGTH]
            score += evaluate_window(window, piece)

    #Positive Slope Diagonal Win Con
    for r in range(ROW_COUNT - 3):
        for c in range(COL_COUNT - 3):
            window = [board[r+i][c+i] for i in range(WINDOW_LENGTH)] # Window_length is 4. takes "bottom right" of diagonal, then goes up diagonally (both are +i)
            score += evaluate_window(window, piece)
    
    #Negative Slop Diagonal Win Con
    for r in range(ROW_COUNT - 3):
        for c in range(COL_COUNT - 3):
            window = [board[r+3-i][c+i] for i in range(WINDOW_LENGTH)] # Window_length is 4. takes "top right" of diagonal, then goes down diagonally (both are +i). the +3 is saying hey we're starting in the top and going down. c is so different from r bc we're changing the slope of only one to change the slope of the entire line
            score += evaluate_window(window, piece)

    return score

def pick_best_move(board, piece):

    valid_locations = get_valid_locations(board)
    best_score = -10000
    best_col = 0

    for col in valid_locations: #this checks by col, not row
        row = get_next_open_row(board, col)
        temp_board = board.copy() #copy makes new place in memory
        drop_piece(temp_board, row, col, piece) #to the ai, this is the current board state
        score = score_position(temp_board, piece) #we dropped the temp piece, now we're checking if it did good
        #it will always go with the leftmost did good if all are equal
        #this is because it puts a piece in each row, then checks how well that went. it goes left to right
        #doesnt matter how you win, so it goes numerical
        #but they might not all be equal. lets say we have blank blank yellow yellow blank
        #if we go in the first blank, thats a score of 10 (one window of 3)
        #but the other two blanks give a score of 20 (two possible windows of 3)
        #so itll do the leftmost blank with a score of 20

        # little preference to middle
        if col == 3:
            score += 1
        if score > best_score:
            best_score = score
            best_col = col
    print(best_score)

    return best_col

def is_terminal_node(board): #gameover conditions
    return winning_move(board, PLAYER_PIECE) or winning_move(board, AI_PIECE) or len(get_valid_locations(board)) == 0 #one piece won or board is filled


def minimax(board, depth, alpha, beta, maximizingPlayer, piece):
    opp_piece = PLAYER_PIECE
    if piece == PLAYER_PIECE:
        opp_piece = AI_PIECE
    valid_locations = get_valid_locations(board)
    is_terminal = is_terminal_node(board) #false if not over
    if depth == 0 or is_terminal:
        if is_terminal:
            if winning_move(board, AI_PIECE):
                return (None, 10000000) # it doesn't return a col value, all is same format
            elif winning_move(board, PLAYER_PIECE):
                return (None, -10000000)
            else:
                return (None, 0) #this is the tie
        else:
            return (None, score_position(board, piece))
        
    if maximizingPlayer: #the player we want to help or "maximize"
        value = - math.inf
        column = random.choice(valid_locations)
        for col in valid_locations:
            row = get_next_open_row(board, col)
            temp_board = board.copy()
            drop_piece(temp_board, row, col, piece)
            new_score = minimax(temp_board, depth - 1, alpha, beta, False, piece)[1] #the false says next time minimize it
            # the [1] is saying only look at the value (score) being returned
            if new_score > value:
                value = new_score
                column = col

            alpha = max(alpha, value) #these three lines make it go way faster
            if alpha >= beta:
                break

        return column, value
    else: #minimizing player, the player we're hurting
        value = math.inf
        column = random.choice(valid_locations)
        for col in valid_locations:
            row = get_next_open_row(board, col)
            temp_board = board.copy()
            drop_piece(temp_board, row, col, opp_piece)
            new_score = minimax(temp_board, depth - 1, alpha, beta, True, piece)[1] #the true says next time maximize it
            if new_score < value:
                value = new_score
                column = col
            beta = min(beta, value)
            if alpha >= beta:
                break
        return column, value

#How Kevin thinks the minimax works
#It's recursion, so first off theres a base case. We're checking three things: 1/2, did someone win? Well then don't recurse anymore. Is the game over and its a tie? don't recurse
#If it's a tie, that's not something anybody wants. If AI wins, thats good, If I win, that's bad. Adjust accordingly
#Then what it does, is it recursively places pieces in all the possible spaces depth number of times
#once depth is 0, it checks the score of where everything is
#it then alternates between picking the best move for the ai, and the best move for the player
#this is what the lower if else does and the True / False
#it then places its piece, thinking we both make the next 4 optimal moves


board = create_board()
game_over = False


pygame.init() #initialize pygame

size = (WIDTH, HEIGHT)
screen = pygame.display.set_mode(size) #choose screen size


myfont = pygame.font.SysFont("monospace", 75)#declaring a font for later
pygame.display.update()
while not game_over:
     #we actually see what we did
    pygame.display.update()

    for event in pygame.event.get(): #everytime you cmove mouse or lick or touch a key
        
        if event.type == pygame.QUIT:
            sys.exit() #shut down properly

        if event.type == pygame.MOUSEMOTION:
            pygame.draw.rect(screen, BLACK, (0, 0, WIDTH, SQUARESIZE)) #cover old circles
            posx = event.pos[0]
            pygame.draw.circle(screen, RED, (posx, int(SQUARESIZE/2)), RADIUS)

        if event.type == pygame.MOUSEBUTTONDOWN:
            #print(event.pos.x)
            #Ask for P1 input
            if turn == PLAYER:
                posx = event.pos[0]
                col = int(math.floor(posx / SQUARESIZE)) #divided by 100, rounded to nearest int by floor. int does nothing, just to check if floor gives an error
                #col, minimax_score = minimax(board, 5, -math.inf, math.inf, True, PLAYER_PIECE)
                #print(col)
                if(is_valid_location(board, col)):
                    row = get_next_open_row(board, col)
                    drop_piece(board, row, col, PLAYER_PIECE)
                    draw_board(board)
                    pygame.display.update()
                    turn = AI

                    if(winning_move(board, PLAYER_PIECE)):
                        label = myfont.render("Red Wins!", 1, RED)
                        pygame.draw.rect(screen, BLACK, (0, 0, WIDTH, SQUARESIZE))
                        screen.blit(label, (40,10))
                        game_over = True
                

    #AI Makes Move
    if turn == AI and not game_over: #Gameover so it doesnt go if P1 has won
        #col = random.randint(0, COL_COUNT - 1)
        #col = pick_best_move(board, AI_PIECE)
        col, minimax_score = minimax(board, 5, -math.inf, math.inf, True, AI_PIECE)
        # print(minimax_score)

        if(is_valid_location(board, col)):
            row = get_next_open_row(board, col)
            #pygame.time.wait(500)
            drop_piece(board, row, col, AI_PIECE)
            turn = PLAYER

            if(winning_move(board, AI_PIECE)):
                label = myfont.render("Yellow Wins!", 1, YELLOW)
                pygame.draw.rect(screen, BLACK, (0, 0, WIDTH, SQUARESIZE))
                screen.blit(label, (40,10))
                game_over = True
        
            
    draw_board(board)
    pygame.display.update()
    if game_over:
        pygame.time.wait(2500) #not close immediatly