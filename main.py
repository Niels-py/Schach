import pygame
import os
from typing import Tuple, List, Dict

pygame.init()

# Farben
BACKGROUND = (17, 17, 27)
BLACKFIELD = (30, 30, 46)
WHITEFIELD = (180, 190, 254)
RECTCOLOR = (235, 160, 172)
AUFGEBENFARBE = (205, 214, 244)
MOVEWHITE = (243, 139, 168)
MOVEBLACK = (249, 226, 175)
SCHACHWHITE = (243, 139, 168)
SCHACHBLACK = (116, 199, 236)
SIEGFONT = (205, 214, 244)
SIEGBACKGROUND = (49, 50, 68)
STEPCOLOR = (205, 214, 244)

BLINKDURATION = 50

WIDTH = 1000
HEIGHT = 1000

screen = pygame.display.set_mode([WIDTH, HEIGHT])
pygame.display.set_caption("Schach")

font = pygame.font.Font(None, 35)
big_font = pygame.font.Font(None, 50)

timer = pygame.time.Clock()
FPS = 60

# Ja Max, ich weis, dass ich englisch und deutsch vermische.
# es tut mir nicht leid, es war einfach einfacher
# ausserdem kenne ich die ganzen englischen Fachbegriffe fuer Schach nicht
board = [
    ["bt", "bs", "bl", "bk", "bd", "bl", "bs", "bt"],
    ["bb", "bb", "bb", "bb", "bb", "bb", "bb", "bb"],
    ["", "", "", "", "", "", "", ""],
    ["", "", "", "", "", "", "", ""],
    ["", "", "", "", "", "", "", ""],
    ["", "", "", "", "", "", "", ""],
    ["wb", "wb", "wb", "wb", "wb", "wb", "wb", "wb"],
    ["wt", "ws", "wl", "wk", "wd", "wl", "ws", "wt"],
]


def get_pos_by_color(color: str) -> List[Tuple[int, int]]:
    has_color: List[Tuple[int, int]] = []
    for y, row in enumerate(board):
        for x, piece in enumerate(row):
            if not piece == "" and piece[0] == color:
                has_color.append((x, y))

    return has_color


captured_pieces: List[str] = []

turn_step: int = 0
# which piece is selected
# bool is False if no piece selected
selection: List[int] = []
valid_moves: List[Tuple[int, int]] = []

# Bilder laden
white_images_map = pygame.image.load(os.path.join("./assets/WhitePieces.png"))
black_images_map = pygame.image.load(os.path.join("./assets/BlackPieces.png"))


def get_img(color: str, index: int, size: int) -> pygame.Surface:
    img = pygame.Surface((16, 16), pygame.SRCALPHA)
    if color == "w":
        img.blit(white_images_map, (0, 0), (index * 16, 0, 16, 16))
    elif color == "b":
        img.blit(black_images_map, (0, 0), (index * 16, 0, 16, 16))

    return pygame.transform.scale(img, (size, size))


piece_image: Dict[str, pygame.Surface] = {
    "wb": get_img("w", 0, 60),
    "ws": get_img("w", 1, 80),
    "wt": get_img("w", 2, 80),
    "wl": get_img("w", 3, 80),
    "wd": get_img("w", 4, 80),
    "wk": get_img("w", 5, 80),
    "bb": get_img("b", 0, 60),
    "bs": get_img("b", 1, 80),
    "bt": get_img("b", 2, 80),
    "bl": get_img("b", 3, 80),
    "bd": get_img("b", 4, 80),
    "bk": get_img("b", 5, 80),
}

piece_image_small: Dict[str, pygame.Surface] = {
    "wb": get_img("w", 0, 45),
    "ws": get_img("w", 1, 45),
    "wt": get_img("w", 2, 45),
    "wl": get_img("w", 3, 45),
    "wd": get_img("w", 4, 45),
    "wk": get_img("w", 5, 45),
    "bb": get_img("b", 0, 45),
    "bs": get_img("b", 1, 45),
    "bt": get_img("b", 2, 45),
    "bl": get_img("b", 3, 45),
    "bd": get_img("b", 4, 45),
    "bk": get_img("b", 5, 45),
}

# check variables/ Schach flashing counter
counter: int = 0  # fuer Animation wenn man im Schach steht
winner: str = ""
game_over: bool = False


# Board malen
def draw_board():
    for i in range(64):
        column = i % 8
        row = i // 8
        if (row + column) % 2 == 0:
            pygame.draw.rect(screen, BLACKFIELD, [column * 100, row * 100, 100, 100])
        else:
            pygame.draw.rect(screen, WHITEFIELD, [column * 100, row * 100, 100, 100])

    # turnstep anzeigen
    status_text = [
        "Weiss: Wähle Figur!",
        "Weiss: Bewege Figur!",
        "Schwarz: Wähle Figur!",
        "Schwarz: Bewege Figur!",
    ]

    screen.blit(big_font.render(status_text[turn_step], True, STEPCOLOR), (20, 820))
    pygame.draw.rect(screen, RECTCOLOR, [800, 0, 200, 900], 5)
    pygame.draw.rect(screen, RECTCOLOR, [0, 800, 1000, 100], 5)
    screen.blit(big_font.render("Aufgeben", True, AUFGEBENFARBE), (810, 830))


# Figuren und Auswahl
def draw_pieces():
    for y, row in enumerate(board):
        for x, piece in enumerate(row):
            if piece == "":
                continue

            img = piece_image[piece]
            margin = 20 if piece[1] == "b" else 10

            screen.blit(
                img,
                (x * 100 + margin, y * 100 + margin),
            )


def draw_selected():
    if not selection == []:
        color = board[selection[0]][selection[1]][0]
        pygame.draw.rect(
            screen,
            color,
            (
                selection[0] * 100 + 1,
                selection[1] * 100 + 1,
                100,
                100,
            ),
            4,
        )


def check_options(color) -> List[Tuple[int, int]]:
    moves_list = []
    for y, row in enumerate(board):
        for x, piece in enumerate(row):
            if not piece == "" and piece[0] == color:
                match piece[1]:
                    case "b":
                        moves_list.extend(check_pawn((x, y), color))
                    case "t":
                        moves_list.extend(check_rook((x, y), color))
                    case "s":
                        moves_list.extend(check_knight((x, y), color))
                    case "l":
                        moves_list.extend(check_bishop((x, y), color))
                    case "d":
                        moves_list.extend(check_queen((x, y), color))
                    case "k":
                        moves_list.extend(check_king((x, y), color))

    return moves_list


def check_king(position, color) -> List[Tuple[int, int]]:
    moves_list = []

    # piece with same color
    friends_list = get_pos_by_color(color)

    targets = [(1, 0), (1, 1), (1, -1), (-1, 0), (-1, 1), (-1, -1), (0, 1), (0, -1)]
    for i in range(8):
        target = (position[0] + targets[i][0], position[1] + targets[i][1])
        if target not in friends_list and 0 <= target[0] <= 7 and 0 <= target[1] <= 7:
            moves_list.append(target)
    return moves_list


def check_queen(position, color) -> List[Tuple[int, int]]:
    moves_list = check_bishop(position, color)
    second_list = check_rook(position, color)
    return moves_list + second_list


def check_bishop(position, color) -> List[Tuple[int, int]]:
    moves_list = []

    enemies_color: str = "b" if color == "w" else "w"
    friends_list = get_pos_by_color(color)
    enemies_list = get_pos_by_color(enemies_color)

    for i in range(4):
        path = True
        chain = 1
        if i == 0:
            x = 1
            y = -1
        elif i == 1:
            x = -1
            y = -1
        elif i == 2:
            x = 1
            y = 1
        else:
            x = -1
            y = 1
        while path:
            if (
                (position[0] + (chain * x), position[1] + (chain * y))
                not in friends_list
                and 0 <= position[0] + (chain * x) <= 7
                and 0 <= position[1] + (chain * y) <= 7
            ):
                moves_list.append(
                    (position[0] + (chain * x), position[1] + (chain * y))
                )
                if (
                    position[0] + (chain * x),
                    position[1] + (chain * y),
                ) in enemies_list:
                    path = False
                chain += 1
            else:
                path = False
    return moves_list


def check_rook(position, color) -> List[Tuple[int, int]]:
    moves_list = []

    enemies_color = "b" if color == "w" else "w"
    friends_list = get_pos_by_color(color)
    enemies_list = get_pos_by_color(enemies_color)

    for i in range(4):
        path = True
        chain = 1
        if i == 0:
            x = 0
            y = 1
        elif i == 1:
            x = 0
            y = -1
        elif i == 2:
            x = 1
            y = 0
        else:
            x = -1
            y = 0
        while path:
            if (
                (position[0] + (chain * x), position[1] + (chain * y))
                not in friends_list
                and 0 <= position[0] + (chain * x) <= 7
                and 0 <= position[1] + (chain * y) <= 7
            ):
                moves_list.append(
                    (position[0] + (chain * x), position[1] + (chain * y))
                )
                if (
                    position[0] + (chain * x),
                    position[1] + (chain * y),
                ) in enemies_list:
                    path = False
                chain += 1
            else:
                path = False
    return moves_list


def check_pawn(position, color) -> List[Tuple[int, int]]:
    moves_list = []

    enemies_color = "b" if color == "w" else "w"
    friends_list = get_pos_by_color(color)
    enemies_list = get_pos_by_color(enemies_color)

    if color == "b":
        # nach vorne bewegen
        if (
            (position[0], position[1] + 1) not in friends_list
            and (position[0], position[1] + 1) not in enemies_list
            and position[1] < 7
        ):
            moves_list.append((position[0], position[1] + 1))
            # nach vorne bewegen am anfang
            if (
                (position[0], position[1] + 2) not in friends_list
                and (position[0], position[1] + 2) not in enemies_list
                and position[1] == 1
            ):
                moves_list.append((position[0], position[1] + 2))
        # nach rechts unten schlagen
        if (position[0] + 1, position[1] + 1) in enemies_list:
            moves_list.append((position[0] + 1, position[1] + 1))
        # nach links unten schlagen
        if (position[0] - 1, position[1] + 1) in enemies_list:
            moves_list.append((position[0] - 1, position[1] + 1))
    else:
        # nach vorne bewegen
        if (
            (position[0], position[1] - 1) not in friends_list
            and (position[0], position[1] - 1) not in enemies_list
            and position[1] > 0
        ):
            moves_list.append((position[0], position[1] - 1))
            # nach vorne bewegen am anfang
            if (
                (position[0], position[1] - 2) not in friends_list
                and (position[0], position[1] - 2) not in enemies_list
                and position[1] == 6
            ):
                moves_list.append((position[0], position[1] - 2))
        # nach rechts oben schlagen
        if (position[0] + 1, position[1] - 1) in enemies_list:
            moves_list.append((position[0] + 1, position[1] - 1))
        # nach links oben schlagen
        if (position[0] - 1, position[1] - 1) in enemies_list:
            moves_list.append((position[0] - 1, position[1] - 1))
    return moves_list


def check_knight(position, color) -> List[Tuple[int, int]]:
    moves_list = []

    friends_list = get_pos_by_color(color)

    targets = [(1, 2), (1, -2), (2, 1), (2, -1), (-1, 2), (-1, -2), (-2, 1), (-2, -1)]
    for i in range(8):
        target = (position[0] + targets[i][0], position[1] + targets[i][1])
        if target not in friends_list and 0 <= target[0] <= 7 and 0 <= target[1] <= 7:
            moves_list.append(target)
    return moves_list


def check_valid_moves() -> List[Tuple[int, int]]:
    piece = board[selection[1]][selection[0]]
    valid_options = []
    color = piece[0]

    match piece[1]:
        case "b":
            valid_options.extend(check_pawn((selection[0], selection[1]), color))
        case "t":
            valid_options.extend(check_rook((selection[0], selection[1]), color))
        case "s":
            valid_options.extend(check_knight((selection[0], selection[1]), color))
        case "l":
            valid_options.extend(check_bishop((selection[0], selection[1]), color))
        case "d":
            valid_options.extend(check_queen((selection[0], selection[1]), color))
        case "k":
            valid_options.extend(check_king((selection[0], selection[1]), color))
    return valid_options


# draw possible moves
def draw_valid(moves):
    if turn_step == 1:
        color = MOVEWHITE
    elif turn_step == 3:
        color = MOVEBLACK
    else:
        raise Exception("draw_valid() on wrong turn")
    for i in range(len(moves)):
        pygame.draw.circle(
            screen, color, (moves[i][0] * 100 + 50, moves[i][1] * 100 + 50), 8
        )


# draw captured pieces on the right
def draw_captured():
    white_index = 0
    black_index = 0
    for piece in captured_pieces:
        if piece[0] == "w":
            x_pos = 825
            screen.blit(piece_image_small[piece], (x_pos, 5 + 50 * white_index))
            white_index += 1
        elif piece[0] == "b":
            x_pos = 925
            screen.blit(piece_image_small[piece], (x_pos, 5 + 50 * black_index))
            black_index += 1


# SCHACH check
def draw_check():
    for y, row in enumerate(board):
        for x, piece in enumerate(row):
            if piece == "wk" and (x, y) in black_options:
                if counter < BLINKDURATION / 2:
                    pygame.draw.rect(
                        screen,
                        SCHACHWHITE,
                        [
                            x * 100 + 1,
                            y * 100 + 1,
                            100,
                            100,
                        ],
                        5,
                    )
            elif piece == "bk" and (x, y) in white_options:
                if counter < BLINKDURATION / 2:
                    pygame.draw.rect(
                        screen,
                        SCHACHBLACK,
                        [
                            x * 100 + 1,
                            y * 100 + 1,
                            100,
                            100,
                        ],
                        5,
                    )


# draws the small 'verloren' popup if someone wins
def draw_game_over():
    pygame.draw.rect(screen, SIEGBACKGROUND, [200, 200, 400, 70])

    screen.blit(
        font.render(
            "Weiss hat gewonnen!" if winner == "w" else "Schwarz hat gewonnen!",
            True,
            SIEGFONT,
        ),
        (210, 210),
    )
    screen.blit(font.render("ENTER zum nochmal spielen.", True, SIEGFONT), (210, 240))



# game loop
run = True
while run:
    timer.tick(FPS)
    if counter < BLINKDURATION:
        counter += 1
    else:
        counter = 0
    screen.fill(BACKGROUND)

    # init check_options (filter dict to get only white or black thingis)
    white_options = check_options("w")
    black_options = check_options("b")

    # draw stuff
    draw_board()
    draw_pieces()
    draw_captured()
    draw_check()

    if not selection == []:
        valid_moves = check_valid_moves()
        draw_valid(valid_moves)

    # event loop
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and not game_over:
            # get square under mouse
            mx_pos = event.pos[0] // 100
            my_pos = event.pos[1] // 100
            m_pos = (mx_pos, my_pos)

            match turn_step:
                case 0:
                    if m_pos in get_pos_by_color("w"):
                        selection = [mx_pos, my_pos]
                        turn_step = 1
                case 1:
                    if m_pos in valid_moves and selection:
                        piece: str = board[selection[1]][selection[0]]

                        # if you click on black piece
                        if m_pos in get_pos_by_color("b"):
                            black_piece = board[my_pos][mx_pos]
                            if black_piece == "bk":
                                winner = "w"

                            # add black piece to captured
                            captured_pieces.append(black_piece)

                        # moving the piece to new position
                        board[selection[1]][selection[0]] = ""
                        board[my_pos][mx_pos] = piece

                        turn_step = 2
                        selection = []
                    else:
                        # if you select different white piece
                        if m_pos in get_pos_by_color("w"):
                            selection = [mx_pos, my_pos]

                case 2:
                    if m_pos in get_pos_by_color("b"):
                        selection = [mx_pos, my_pos]
                        turn_step = 3
                case 3:
                    if m_pos in valid_moves and selection:
                        piece: str = board[selection[1]][selection[0]]

                        # if you click on white piece
                        if m_pos in get_pos_by_color("w"):
                            white_piece = board[my_pos][mx_pos]
                            if white_piece == "wk":
                                winner = "b"

                            # add white piece to captured
                            captured_pieces.append(white_piece)

                        # moving the piece to new position
                        board[selection[1]][selection[0]] = ""
                        board[my_pos][mx_pos] = piece

                        turn_step = 0
                        selection = []
                    else:
                        # if you select different white piece
                        if m_pos in get_pos_by_color("b"):
                            selection = [mx_pos, my_pos]

            # aufgeben
            if m_pos == (8, 8) or m_pos == (9, 8):
                winner = "b" if turn_step < 2 else "w"

        if event.type == pygame.KEYDOWN and game_over:
            if event.key == pygame.K_RETURN:
                game_over = False
                winner = ""

                board = [
                    ["bt", "bs", "bl", "bk", "bd", "bl", "bs", "bt"],
                    ["bb", "bb", "bb", "bb", "bb", "bb", "bb", "bb"],
                    ["", "", "", "", "", "", "", ""],
                    ["", "", "", "", "", "", "", ""],
                    ["", "", "", "", "", "", "", ""],
                    ["", "", "", "", "", "", "", ""],
                    ["wb", "wb", "wb", "wb", "wb", "wb", "wb", "wb"],
                    ["wt", "ws", "wl", "wk", "wd", "wl", "ws", "wt"],
                ]

                captured_pieces: List[str] = []
                turn_step: int = 0
                selection: List[int] = []
                valid_moves: List[Tuple[int, int]] = []

                # init check_options (filter dict to get only white or black thingis)
                white_options = check_options("w")
                black_options = check_options("b")

    if winner != "":
        game_over = True
        draw_game_over()

    pygame.display.flip()

pygame.quit()
