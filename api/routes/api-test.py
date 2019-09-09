from jinja2 import Environment, FileSystemLoader


def encode_public_id(num_id):
    """
        make 4-letter ID from numeric ID
        Args:
            num_id (int): ID consisting of a number and 3 alphabets
        Return:
            str_id (str): encoded ID
    """
    encoder = "ACDEFGHJKLMNPRTWXY"

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


def gen_data():
    def public_id_generator(lottery, status):
        return map(encode_public_id, range(85))

    data = []
    for cl in ["5A", "5B"]:
        lottery_result = []
        for status in "won", "waiting":
            public_ids = list(sorted(public_id_generator(cl, status)))
            lottery_result.append({'status': status, 'winners': public_ids})

        data.append({'classroom': str(cl),
                     'statuses': lottery_result})

    env = Environment(loader=FileSystemLoader('./api/templates'))
    template = env.get_template('results.html')
    return template.render(lotteries=data)


if __name__ == '__main__':
    print(gen_data())
