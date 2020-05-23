
import PIL, random, os, shutil

class Winner(Exception):
    pass

class Tie(Exception):
    pass

class InvalidMove(Exception):
    pass

class TicTacToe:
    def __init__(self, player1, player2):
        # Készítsen másolatot a mezőről a cache mappába,
        # majd megnyitjuk módosításra
        self.file = f"cache/ttt_{player1.guild.id}.png"
        shutil.copy("assets/tictactoe/grid.png", self.file)
        self.image = PIL.Image.open(self.file)

        # Válasszon véletlenszerűen ki kapja a karaktert és ki következik
        self.turn = random.choice(["x","o"])
        if bool(random.getrandbits(1)):
            self.players = {"x": player1, "o": player2}
        else:
            self.players = {"o": player1, "x": player2}

        # Mezők számoláshoz
        self.fields = ["","","","","","","","",""]

    def __del__(self):
        # Zárja le a képet, majd törölje azt a cache mappából
        self.image.close()
        try:
            os.remove(self.file)
        except PermissionError:
            print(f"Nem lehetett eltávolítani a {self.file}.")

    def is_board_full(self):
        return "" not in self.fields

    def is_field_free(self, field):
        return self.fields[field] == ""

    def move(self, field):
        if (0 <= field <= 8) and self.is_field_free(field):
            # Helyezze le a jelet
            self.fields[field] = self.turn

            # Kiderítjük hogy nyert-e a menet
            f, p = self.is_winner(self.fields, self.turn)
            
            # Tegye a jelet is a képre
            poses = {
                0: (24,24), 1: (114,24), 2: (204,24),
                3: (24,114), 4: (114,114), 5: (204,114),
                6: (24,204), 7: (114,204), 8: (204,204)
            }
            li = PIL.Image.open(f"assets/tictactoe/{self.turn}.png")
            self.image.paste(li, poses[field])
            li.close()

            # Ha nyert, helyezze le a vonalat hogy hol
            if f != False:
                c = PIL.Image.open(f"assets/tictactoe/{f}.png")
                if f in ("v","h"):
                    self.image.paste(c,p)
                else:
                    self.image.paste(c,p,c)
                c.close()

            # Mentse a képet
            self.image.save(self.file)

            # Forduljon a menet
            self.turn = "x" if self.turn == "o" else "o"

            if f != False:
                raise Winner
            elif self.is_board_full():
                raise Tie
        else:
            raise InvalidMove

    def get_board_copy(self):
        fields=[]
        for field in self.fields:
            fields.append(field)
        return fields

    def get_move_from_list(self, moves):
        fields=[]
        for i in moves:
            if self.is_field_free(i):
                fields.append(i)
        return random.choice(fields) if len(fields) != 0 else None

    def get_computer_move(self, stoopid_mode=True):
        if stoopid_mode:
            fields = [f for f in range(0,9) if self.is_field_free(f)]
            return random.choice(fields)
        else:
            # Megnézzük azt ki áll nyerésre most...
            bl, pl = ("x","o") if self.players["x"].bot else ("o","x")

            for field in range(0,9):
                board = self.get_board_copy()
                if board[field] == "":
                    # Derítsük ki hogy a bot nyerésre áll-e, ha igen tegyen
                    board[field] = bl
                    i,p = self.is_winner(board,bl)
                    if i != False:
                        return field

                    # Ha viszont játékos áll nyerésre, csapjon le rá
                    board[field] = pl
                    i,p = self.is_winner(board,pl)
                    if i != False:
                        return field

            # Foglaljon helyet valamely szélére
            field = self.get_move_from_list([0,2,6,8])
            if field != None:
                return field

            # Foglalja le a középső mezőt, ha szabad
            if self.is_field_free(4):
                return 4

            # Ha továbbra sincs hely, mozogjon keresztben
            return self.get_move_from_list([1,3,5,7])

    def is_winner(self, f, l):
        if (f[0] == l and f[1] == l and f[2] == l): return "h", (20,57)
        elif (f[3] == l and f[4] == l and f[5] == l): return "h", (20,147)
        elif (f[6] == l and f[7] == l and f[8] == l): return "h", (20,237)
        elif (f[0] == l and f[3] == l and f[6] == l): return "v", (57,20)
        elif (f[1] == l and f[4] == l and f[7] == l): return "v", (147,20)
        elif (f[2] == l and f[5] == l and f[8] == l): return "v", (237,20)
        elif (f[0] == l and f[4] == l and f[8] == l): return "l", (0,0)
        elif (f[2] == l and f[4] == l and f[6] == l): return "r", (0,0)
        else: return False, False
