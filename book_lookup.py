import numpy as np

class Book_lookupper():
    def __init__(self,book,settings):
        self.all_book = book
        self.settings = settings
        self.book = self.create_set_book()

    def change_settings(self,settings):
        self.settings = settings
        self.book = self.create_set_book()

    def merge_books(self,books):
        keys = set(sum([list(book.keys()) for book in books], []))
        new_book = dict()
        for key in keys:        
            white_wins = 0
            black_wins = 0
            rating = None
            num_games = 0
            for book in books:
                if key in book:
                    white_wins += book[key][0]
                    black_wins += book[key][1]
                    inner_games = book[key][0]+book[key][1]
                    num_games+=inner_games
                    if rating is None:
                        rating = book[key][2]
                    else:
                        rating = (rating + (inner_games/num_games)*book[key][2])/(1+(inner_games/num_games))
            new_book[key] = np.array([white_wins, black_wins, rating])
        return new_book

    def create_set_book(self):
        cur_books = [self.all_book]
        for setting in self.settings:
            new_layer = []
            for book in cur_books:
                for ok_val in setting:
                    new_layer.append(book[ok_val])
            cur_books = new_layer
        return self.merge_books(cur_books)

    def lookup_games(self,moves_with_hash):
        moves_with_data = []
        for move,myhash in moves_with_hash:
            if myhash in self.book:
                entry = self.book[myhash]
                moves_with_data.append({
                    "move":move,
                    "black_wins":entry[0],
                    "white_wins":entry[1],
                    "rating":entry[2]
                })
        return moves_with_data