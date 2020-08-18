from go_game import Go_game,Rotater
import numpy as np

"""
        ###########
        #         #
        #         #
        #         #
        #         #
        #         #
        #         #
        #         #
        #         #
        #         #
        ###########
        """

def test_symetry():
    zobrist = np.load("zobrist.npy")
    rotater = Rotater(9)
    go_game1 = Go_game(rotater,zobrist,9)
    go_game2 = Go_game(rotater,zobrist,9)
    
    go_game1.set_pos_from_str(
        """
        ###########
        #   W     #
        #      B  #
        #         #
        #         #
        #    W    #
        #         #
        #         #
        # B       #
        #         #
        ###########
        """
    )
    go_game2.set_pos_from_str(
        """
        ###########
        #         #
        # B       #
        #         #
        #         #
        #    W    #
        #         #
        #         #
        #      B  #
        #   W     #
        ###########
        """
    )
    if go_game1.do_hash()==go_game2.do_hash():
        print("mirrory success")
    else:
        print("mirrory failed")
    go_game2.set_pos_from_str(
        """
        ###########
        #     W   #
        #  B      #
        #         #
        #         #
        #    W    #
        #         #
        #         #
        #       B #
        #         #
        ###########
        """
    )
    if go_game1.do_hash()==go_game2.do_hash():
        print("mirrory success")
    else:
        print("mirrory failed")
    go_game2.set_pos_from_str(
        """
        ###########
        #         #
        #         #
        #       B #
        #         #
        #    W    #
        #        W#
        #         #
        # B       #
        #         #
        ###########
        """
    )
    if go_game1.do_hash()==go_game2.do_hash():
        print("mirror_bl_tr success")
    else:
        print("mirror_bl_tr failed")
    go_game2.set_pos_from_str(
        """
        ###########
        #         #
        #       B #
        #         #
        #         #
        #    W    #
        #         #
        #         #
        # B       #
        #     W   #
        ###########
        """
    )
    if go_game1.do_hash()!=go_game2.do_hash():
        print("catch trial success")
    else:
        print("catch trial failed")
if __name__=='__main__':
    test_symetry()