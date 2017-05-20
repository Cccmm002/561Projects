# USC CSCI 561 Spring 2017 Project 1
# Copyright 2017 Cccmm002


BoardScores = [[99, -8, 8, 6, 6, 8, -8, 99], [-8, -24, -4, -3, -3, -4, -24, -8],
               [8, -4, 7, 4, 4, 7, -4, 8], [6, -3, 4, 0, 0, 4, -3, 6],
               [6, -3, 4, 0, 0, 4, -3, 6], [8, -4, 7, 4, 4, 7, -4, 8],
               [-8, -24, -4, -3, -3, -4, -24, -8], [99, -8, 8, 6, 6, 8, -8, 99]]

logging = []


class Board:    # 1 means black, -1 means white
    def __init__(self):
        self.board = [[0 for col in range(8)] for row in range(8)]

    def set(self, cap, num, x):  # x: True: X; False: O
        self.board[cap][num] = 1 if x else -1

    def score(self, x_respect=True):
        s = 0
        for i in range(0, 8):
            for j in range(0, 8):
                s += self.board[i][j]*BoardScores[i][j]
        return s if x_respect else 0 - s

    def draw_string(self):
        res = ["" for r in range(8)]
        for i in range(0, 8):
            for j in range(0, 8):
                if self.board[j][i] == 1:
                    res[i] += 'X'
                elif self.board[j][i] == -1:
                    res[i] += 'O'
                else:
                    res[i] += '*'
        return '\n'.join(res)

    def copy(self):
        res = Board()
        for i in range(0, 8):
            res.board[i] = self.board[i][:]
        return res

    def get_piece(self, cap, num, n, direction):   # 0: left; 1: right; 2: up; 3: down; 4: upper-left
        if direction == 0:                         # 5: lower-left; 6: upper-right; 7: lower-right
            if cap - n < 0:
                return None
            else:
                return self.board[cap - n][num]
        elif direction == 1:
            if cap + n >= 8:
                return None
            else:
                return self.board[cap + n][num]
        elif direction == 2:
            if num - n < 0:
                return None
            else:
                return self.board[cap][num - n]
        elif direction == 3:
            if num + n >= 8:
                return None
            else:
                return self.board[cap][num + n]
        elif direction == 4:
            if cap - n < 0 or num - n < 0:
                return None
            else:
                return self.board[cap - n][num - n]
        elif direction == 5:
            if cap - n < 0 or num + n >= 8:
                return None
            else:
                return self.board[cap - n][num + n]
        elif direction == 6:
            if cap + n >= 8 or num - n < 0:
                return None
            else:
                return self.board[cap + n][num - n]
        elif direction == 7:
            if cap + n >= 8 or num + n >= 8:
                return None
            else:
                return self.board[cap + n][num + n]

    def set_piece(self, cap, num, n, direction, value):
        if direction == 0:
            if cap - n >= 0:
                self.board[cap - n][num] = value
        if direction == 1:
            if cap + n < 8:
                self.board[cap + n][num] = value
        if direction == 2:
            if num - n >= 0:
                self.board[cap][num - n] = value
        if direction == 3:
            if num + n < 8:
                self.board[cap][num + n] = value
        if direction == 4:
            if num - n >= 0 and cap - n >= 0:
                self.board[cap - n][num - n] = value
        if direction == 5:
            if num + n < 8 and cap - n >= 0:
                self.board[cap - n][num + n] = value
        if direction == 6:
            if num - n >= 0 and cap + n < 8:
                self.board[cap + n][num - n] = value
        if direction == 7:
            if num + n < 8 and cap + n < 8:
                self.board[cap + n][num + n] = value


def try_next(board, cap, num, color):  # color = 1 or -1
    if board.board[cap][num] == 1 or board.board[cap][num] == -1:
        return None
    res = None
    for direction in range(0, 8):
        surround = board.get_piece(cap, num, 1, direction)
        if surround is not None:
            if not surround == (0 - color):
                continue
            flag = True
            n = 1
            while flag:
                n += 1
                c = board.get_piece(cap, num, n, direction)
                if c is None:
                    break
                elif not (c == 1 or c == -1):
                    break
                elif c == color:
                    flag = False
            if not flag:
                if res is None:
                    res = board.copy()
                for r in range(0, n):
                    res.set_piece(cap, num, r, direction, color)
    return res


def get_name(cap, num):
    c = chr(ord('a') + cap)
    return c + str(num + 1)


def print_output(name, depth, value, alpha, beta):
    res = [name, str(depth), str(value), str(alpha), str(beta)]
    return res


def AlphaBeta(name, board, depth, target_depth, a, b, maximizingPlayer, x_respect, lastPassFlag = 0):
    global logging
    alpha = a
    beta = b
    if depth == target_depth or lastPassFlag == 2:
        score = board.score(x_respect=x_respect)
        logging.append(print_output(name, depth, score, alpha, beta))
        return score, board
    cur_color = 1 if maximizingPlayer == x_respect else -1
    v = float('-inf') if maximizingPlayer else float('inf')
    logging.append(print_output(name, depth, v, alpha, beta))
    candidate = board
    terminal = True
    exitloop = False
    for i in range(0, 8):
        for j in range(0, 8):
            if exitloop:
                break
            c = try_next(board, j, i, cur_color)
            if c is not None:
                terminal = False
                n = AlphaBeta(get_name(j, i), c, depth + 1, target_depth, alpha, beta, not maximizingPlayer, x_respect)[0]
                if maximizingPlayer:
                    if n > v:
                        v = n
                        candidate = c
                        if n < beta:
                            alpha = max(alpha, v)
                        else:
                            exitloop = True
                else:
                    if n < v:
                        v = n
                        candidate = c
                        if n > alpha:
                            beta = min(beta, v)
                        else:
                            exitloop = True
                if beta <= alpha:
                    exitloop = True
                logging.append(print_output(name, depth, v, alpha, beta))
    if terminal:  # Have to pass or terminate
        if lastPassFlag == 1:  # terminate
            v = AlphaBeta('pass', board, depth + 1, target_depth, alpha, beta, not maximizingPlayer, x_respect, lastPassFlag=2)[0]
        elif lastPassFlag == 0:  # pass
            v = AlphaBeta('pass', board, depth + 1, target_depth, alpha, beta, not maximizingPlayer, x_respect, lastPassFlag=1)[0]
        if maximizingPlayer:
            if v < beta:
                alpha = v
        else:
            if v > alpha:
                beta = v
        logging.append(print_output(name, depth, v, alpha, beta))
    return v, candidate


def main():
    file_name = 'input.txt'
    f = open(file_name, 'U')
    content = []
    for i in range(0, 10):
        content.append(f.readline().strip('\n').strip('\r'))
    f.close()
    player = content[0][0] == 'X'
    depth = int(content[1])
    start_board = Board()
    for i in range(2, 10):
        for j in range(0, 8):
            if content[i][j] == 'X':
                start_board.set(j, i - 2, True)
            elif content[i][j] == 'O':
                start_board.set(j, i - 2, False)
    global logging
    logging = []
    res = AlphaBeta('root', start_board, 0, depth, float('-inf'), float('inf'), True, player)[1]
    output_file = open('output.txt', 'w+')
    output_file.write(res.draw_string() + '\n')
    output_file.write("Node,Depth,Value,Alpha,Beta" + '\n')
    log = [','.join(i).replace('inf', 'Infinity') for i in logging]
    output_file.write('\n'.join(log))
    output_file.close()


if __name__ == '__main__':
    main()
