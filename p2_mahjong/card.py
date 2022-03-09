class MahjongCard(object):

    info = {'type':  ['dots', 'bamboo', 'characters'],
            'trait': ['1', '2', '3', '4', '5', '6', '7', '8', '9']
            }

    def __init__(self, runtime_id, card_id=0, user_id=-1):
        """ Initialize the class of MahjongCard

        Args:
            card_id (int): The config_id of card
            user_id (int): Belong to which player, generated when the dealer deals card
        """
        self.runtime_id = runtime_id
        self.card_id = card_id
        self.user_id = user_id
        self.type = None
        self.trait = None

    def set_user_id(self, user_id):
        self.user_id = user_id

    def get_user_id(self):
        return self.user_id

    def set_card_id(self, card_id):
        self.card_id = card_id

    def get_card_id(self):
        return self.card_id

    def get_str(self):
        """ Get the string representation of card

        Return:
            (str): The string of card's color and trait
        """
        return self.type + "-" + self.trait
