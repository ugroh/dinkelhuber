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
    if hash(go_game1)==hash(go_game2):
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
    if hash(go_game1)==hash(go_game2):
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
    if hash(go_game1)==hash(go_game2):
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
    if hash(go_game1)!=hash(go_game2):
        print("catch trial success")
    else:
        print("catch trial failed")
if __name__=='__main__':
    test_symetry()