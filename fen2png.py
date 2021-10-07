from PIL import Image
import os

PIECES = "RBNQKPrbnqkp"
PIECES_DICT = {i: ("b" if i.islower() else "w") + i.lower() for i in PIECES}
ICONS = "resources/pieces/"

def is_int(val):
    """
    checks if a string represents an integer
    :param val: single str charachter, e.g. 's'.
    """
    try:
        val = int(val)
        return True
    except ValueError:
        return False


class DrawBoard:
    def __init__(self, fen, theme, square_size=40):
        self.dir = os.getcwd() + '/'
        self.fen = fen.split()[0]
        self.theme = theme
        self.square_size = square_size
        self.piece_size = (square_size, square_size)
        self.board_size = (square_size * 8, square_size * 8)
        self.output = Image.open(self.dir + ICONS + theme + '/board.png').resize(self.board_size)

    def _get_piece_positions(self):
        board = [["" for _ in range(8)] for _ in range(8)]
        positions = self.fen.split('/')
        for i, rank in enumerate(positions):
            j = 0
            for square in rank:
                if is_int(square):
                    j += int(square)
                    continue
                board[i][j] = square
                j += 1

        return board

    def _insert_piece(self, coordinate, piece):
        piece_img = Image.open(self.dir + ICONS + self.theme + '/' + PIECES_DICT.get(piece) + '.png')
        piece_img = piece_img.resize(self.piece_size)
        X = coordinate[1] * self.square_size
        Y = coordinate[0] * self.square_size
        self.output.paste(piece_img, (X, Y), piece_img)

    def _add_pieces(self):
        positions = self._get_piece_positions()
        for i in range(8):
            for j in range(8):
                if positions[i][j]:
                    self._insert_piece((i, j), positions[i][j])

    def save_board(self, out_path):
        self._add_pieces()
        if '.png' not in out_path:
            out_path += '.png'
        try:
            self.output.save(out_path)
        except FileNotFoundError:
            new_folder = '/'.join(out_path.split('/')[:-1])
            os.system('mkdir {}'.format(new_folder))
            self.output.save(out_path)
