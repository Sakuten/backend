import json
import random
from secrets import token_urlsafe
# typehints imports {{{
from typing import List, Dict
# }}}


max_public_id = 34991   # 6 ([3-79]) * 18 ([AC-HJ-NPRTW-Y]) * 18 * 18


encoder = "ACDEFGHJKLMNPRTWXY"


def encode_public_id(num_id: int) -> str:
    """
        make 4-letter ID from numeric ID
        Args:
            num_id (int): ID consisting of a number and 3 alphabets
        Return:
            str_id (str): encoded ID
    """
    def one_alpha(num: int) -> str:
        return encoder[num]

    def one_digit(num: int) -> str:
        return '9' if num == 5 else str(num + 3)

    latter_3_num = num_id // (18**3)
    letters: List[int] = []
    for i in range(1, 4):
        data = num_id % (18**i) // 18**(i-1)
        letters.insert(0, data)
        sub = data * (18**(i-1))
        num_id -= sub
    return one_digit(latter_3_num) + ''.join(one_alpha(n) for n in letters)


def decode_public_id(str_id: str) -> int:
    """
        make numeric ID from 4-letter ID
        Args:
            str_id (str): ID consisting of a number and 3 alphabets
        Return:
            num_id (int): numeric ID
    """
    def alpha2num(c: str) -> int:
        return encoder.find(c)

    def num2num(c: str) -> int:
        return 5 if c == '9' else int(c) - 3

    alphas = [alpha2num(c) for c in str_id[1:]]
    alphas.insert(0, num2num(str_id[0]))
    return sum(alphas[i] * 18**(3-i) for i in range(4))


def generate_ids(how_many: int) -> List[Dict]:
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

    id_dicts = [{
                "secret_id": secret,
                "public_id": encode_public_id(public),
                "authority": "normal"   # normal user (not admin or staff)
                }
                for (secret, public) in zip(secret_ids, public_raw_ids)]

    return id_dicts


# TODO: Does id_dicts type 'Dict'?
def save_id_json_file(json_path: str, id_dicts: List[Dict]) -> None:
    """
        create a new JSON file and save the given IDs
        Args:
            json_path (str): where to create a JSON file
    """
    with open(json_path, 'w') as f:
        json.dump(id_dicts, f, indent=4)


def load_id_json_file(json_path: str) -> List:
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
