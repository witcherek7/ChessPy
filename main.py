import chess
import chess.engine

x_label = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
y_label = ['1', '2', '3', '4', '5', '6', '7', '8']

desc = ['Uppercase - WHITE',
        'Lowercase - BLACK',
        'K - King',
        'Q - Queen',
        'R - Rook',
        'B - Bishop',
        'K - Knight',
        'P - Pawn']


board = chess.Board()

def print_board(board, message):
    print("--------------------------------------------------------")
    print(f"    Turn: {turn}\n")
    text_part = 0 
    text = board.board_fen()
    text = text.split('/')
    print("   ", end='')
    for label in x_label:
        if label == 'H':
            print(label, end='\n\n')
        else:
            print(label, end=' ')
    for label in reversed(y_label):
        # for x in range(0, 17):
        #     if(x == 16):
        #         print("–", end="\n")
        #     else:
        #         print("–", end="")
        print(label, end=' ')
        for letter in text[text_part]:
            if(letter.isdigit()):
                for nothing in range (0, int(letter)):
                    print("| ", end='')
            else:
                print(f"|{letter}",end='')
        print(f'|     {desc[text_part]}', end = '')
        print("\n",end='')    
        text_part = text_part + 1

    print('\n')
    print(f"Info: {message}")
    message = ''
    print('\n')

def print_help():
    print("TO BE DONE")


message = ''
while True:
    print_board(board,message)
    player_input = input('command>>')
    try:
        chess_input = chess.Move.from_uci(player_input)
    except:
        message = f"Bad input '{player_input}'"
        continue
    if(player_input == 'help'):
        print_help()
        continue
    elif(chess_input in board.legal_moves):
       
        board.push(chess_input)
        if(board.is_checkmate()):
            print(f"{turn} wins!")
            exit()
        else:
            message = f"Move done by {turn} '{player_input}', "
        if(turn =='WHITE'):
            turn ='BLACK'
        else:
            turn = 'WHITE'
        
        
    else:
        message = f"Illegal move '{player_input}'"
        

