import json
import random
from secrets import token_urlsafe


max_public_id = 34991   # 6 ([3-79]) * 18 ([AC-HJ-NPRTW-Y]) * 18 * 18


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
        letters.insert(0, data)
        sub = data * (18**(i-1))
        num_id -= sub
    return one_digit(latter_3_num) + ''.join(one_alpha(n) for n in letters)


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
    return sum(alphas[i] * 18**(3-i) for i in range(4))


def generate_ids(for_admin, for_checkers, for_students, for_visitors):
    """
        generate a list of dictionaries that have a pair of
        secret ID and public ID
        return the generated IDs for the use in making
        QR codes
        Args:
            for_admin (int): number of IDs for admin
            for_checkers (int): number of IDs for
            for_students (int): number of IDs for
            for_visitors (int): number of IDs for
        Return:
            secret_ids (list): all generated IDs
    """
    public_raw_ids = random.sample(
        range(max_public_id + 1),
        for_admin + for_checkers + for_students + for_visitors)

    def given_auth_kind(num, auth, kind):
        nonlocal public_raw_ids
        public_ids = public_raw_ids[:num]
        public_raw_ids = public_raw_ids[num:]
        secret_ids = [token_urlsafe(24) for _ in range(num)]
        return [{
                "secret_id": secret,
                "public_id": encode_public_id(public),
                "authority": auth,
                "kind": kind
                }
                for (secret, public) in zip(secret_ids, public_ids)]

    return ( given_auth_kind(for_admin, "admin", "admin")           # noqa
           + given_auth_kind(for_checkers, "checker", "checker")    # noqa
           + given_auth_kind(for_students, "normal", "student")     # noqa
           + given_auth_kind(for_visitors, "normal", "visitor")     # noqa
           )                                                        # noqa


def save_id_json_file(json_path, id_dicts):
    """
        create a new JSON file and save the given IDs
        Args:
            json_path (str): where to create a JSON file
    """
    with open(json_path, 'w') as f:
        json.dump(id_dicts, f, indent=4)


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
