import numpy as np

class Rotater():
    def __init__(self,size):
        self.rot90 = np.empty((size,size),dtype=np.int32).tolist()
        self.transpose = np.empty_like(self.rot90).tolist()
        self.mirrorx = np.empty_like(self.rot90).tolist()
        self.mirrory = np.empty_like(self.rot90).tolist()
        for row in range(size):
            for col in range(size):
                self.rot90[row][col] = (size-col-1,row)
                self.transpose[row][col] = (col,row)
                self.mirrorx[row][col] = (size-row-1,col)
                self.mirrory[row][col] = (row,size-col-1)
        self.rot180 = self.apply_symetry(self.rot90,self.rot90)
        self.rot270 = self.apply_symetry(self.rot180,self.rot90)
        self.mirror_bl_tr = self.apply_symetry(self.transpose,self.rot180)
        self.symetries = (self.rot90,self.rot180,self.rot270,self.mirrorx,self.mirrory,self.transpose,self.mirror_bl_tr)
    def apply_symetry(self,pos,sym):
        newpos = np.empty_like(pos)
        if type(pos) == list:
            newpos = list(newpos)
        for row,symrow in enumerate(sym):
            for col,target in enumerate(symrow):
                newpos[row][col] = pos[target[0]][target[1]]
        return newpos
    def apply_all_syms(self,pos):
        all_pos = [pos]
        for sym in self.symetries:
            newp0 = self.apply_symetry(pos[0],sym)
            newp1 = self.apply_symetry(pos[1],sym)
            all_pos.append([newp0,newp1])
        return all_pos
class Go_game():
    def __init__(self,rotater:Rotater,zobrist,size=9):
        self.size = size
        self.rotater = rotater
        self.zobrist = zobrist
        self.reset()
    def reset(self):
        self.position = [np.zeros((self.size,self.size),dtype=bool),np.zeros((self.size,self.size),dtype=bool)]
        self.onturn = False
    def set_pos_from_str(self,strpos):
        strpos = "\n".join([x.strip() for x in strpos.splitlines() if len(x.strip()) > 0])
        strpos = strpos.replace("#","")
        strpos = "\n".join(list(filter(lambda x:len(x)>0, strpos.splitlines())))
        for row,line in enumerate(strpos.splitlines()):
            for col,symbol in enumerate(line):
                self.position[0][row][col] = True if symbol=="B" else False
                self.position[1][row][col] = True if symbol=="W" else False

    def make_move(self,move):
        if move:
            self.position[self.onturn][move] = True
            self.remove_dead_stones(move)
        self.onturn = not self.onturn
    def remove_dead_stones(self,move):
        def check_if_dead(current,alreadys,mycolor):
            alreadys.add(current)
            check_squares = [(current[0]+1,current[1]),(current[0]-1,current[1]),(current[0],current[1]+1),(current[0],current[1]-1)]
            for square in check_squares:
                if square[0]<0 or square[1]<0 or square[0]>=self.size or square[1]>=self.size or square in alreadys:
                    continue
                elif self.position[not mycolor][square]:
                    continue
                elif self.position[mycolor][square]:
                    res = check_if_dead(square,alreadys,mycolor)
                    if not res:
                        return False
                    alreadys.update(res)
                else:
                    return False
            return alreadys
        interest_squares = [move,(move[0]+1,move[1]),(move[0]-1,move[1]),(move[0],move[1]+1),(move[0]+1,move[1]-1)]
        dead_stones = set()
        laters = set()
        for square in interest_squares:
            if square[0]<0 or square[1]<0 or square[0]>=self.size or square[1]>=self.size or square in dead_stones:
                continue
            if self.position[self.onturn][square]:
                laters.add(square)
            elif not self.position[not self.onturn][square]:
                continue
            whats_dead = check_if_dead(square,set(),not self.onturn)
            if whats_dead:
                dead_stones.update(whats_dead)
        for stone in dead_stones:
            self.position[not self.onturn][stone] = False
        dead_stones = set()
        for square in laters:
            whats_dead = check_if_dead(square,set(),self.onturn)
            if whats_dead:
                dead_stones.update(whats_dead)
        for stone in dead_stones:
            self.position[self.onturn][stone] = False
    def __repr__(self):
        out_str = ""
        out_str+="#"*(self.size+2)+"\n"
        for row in range(self.size):
            out_str+="#"
            for col in range(self.size):
                if self.position[0][row][col]:
                    out_str+="B"
                elif self.position[1][row][col]:
                    out_str+="W"
                else:
                    out_str+=" "
            out_str+="#\n"
        out_str+="#"*(self.size+2)
        return out_str
    def __hash__(self):
        def hash_without_sym(pos):
            out = 0
            for row in range(self.size):
                for col in range(self.size):
                    if pos[0][row][col]:
                        out^=self.zobrist[0][row][col]
                    elif pos[1][row][col]:
                        out^=self.zobrist[1][row][col]
            out^=self.zobrist[2][0][int(self.onturn)]
            return out
        all_pos = self.rotater.apply_all_syms(self.position)
        minhash = np.inf
        for pos in all_pos:
            ahash = hash_without_sym(pos)
            if ahash < minhash:
                minhash = ahash
        return int(minhash)

def play_go(game):
    print(game)
    while 1:
        move = input("Enter your move")
        move = tuple(reversed([int(x)-1 for x in move.split(",")]))
        game.make_move(move)
        print(game)

if __name__ == "__main__":
    game = Go_game()
    play_go(game)