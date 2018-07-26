import json
import random
from secrets import token_urlsafe


max_public_id = 34991


encoder = "ACDEFGHJKLMNPRTWXY"


def encode_public_id(num_id):
    """
        make 4-letter ID from numeric ID
        Args:
            num_id (int): ID consisting of a number and 3 alphabets
        Return:
            str_id (str): encoded ID
    """
    def one_alpha(num):
        return encoder[num]

    def one_digit(num):
        return '9' if num == 5 else str(num + 3)

    latter_3_num = num_id // (18**3)
    letters = []
    for i in range(1, 4):
        data = num_id % (18**i) // 18**(i-1)
        letters = [data] + letters
        sub = data * (18**(i-1))
        num_id -= sub
    return one_digit(latter_3_num) + ''.join([one_alpha(n) for n in letters])


def decode_public_id(str_id):
    """
        make numeric ID from 4-letter ID
        Args:
            str_id (str): ID consisting of a number and 3 alphabets
        Return:
            num_id (int): numeric ID
    """
    def alpha2num(c):
        return encoder.find(c)

    def num2num(c):
        return 5 if c == '9' else int(c) - 3

    alphas = [alpha2num(c) for c in str_id[1:]]
    alphas.insert(0, num2num(str_id[0]))
    return sum([alphas[i] * 18**(3-i) for i in range(4)])


def find_public_id(ids, secret_id):
    """
        search for the public ID that corresponds to the given secret ID
        Args:
            ids (list): list of dictionaries that contains IDs
            secret_id (str): token (target)
        Return:
            public_id (str): 4-letter ID
    """
    for id_dict in ids:
        if id_dict["secret_id"] == secret_id:
            return id_dict["public_id"]


def find_secret_id(ids, public_id):
    """
        search for the secret ID that corresponds to the given public ID
        Args:
            ids (list): list of dictionaries that contains IDs
            secret_id (str): 4-letter ID (target)
        Return:
            public_id (str): token
    """
    for id_dict in ids:
        if id_dict["public_id"] == public_id:
            return id_dict["secret_id"]


def generate_ids(how_many):
    """
        generate a list of dictionaries that have a pair of
        secret ID and public ID
        return the generated IDs for the use in making
        QR codes
        Args:
            how_many (int): how many pairs of IDs are needed
        Return:
            secret_ids (list): all generated IDs
    """
    public_raw_ids = random.sample(range(max_public_id + 1), how_many)
    secret_ids = [token_urlsafe(24) for _ in range(how_many)]

    id_dicts = [{"secret_id": secret, "public_id": encode_public_id(public)}
                for (secret, public) in zip(secret_ids, public_raw_ids)]

    return id_dicts


def load_id_json_file(json_path):
    """
        load the JSON file and get the data inside
        all this function does is to call json.load(f)
        inside a with statement
        Args:
            json_path (str): where the target JSON file is
        Return:
            ID list (list): all the data found in the file
    """
    with open(json_path, 'r') as f:
        return json.load(f)
