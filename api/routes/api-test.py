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
    data = []
    for cl in ['5A', '5B']:
        lottery_result = []
        for kind in ['visitor', 'student']:
            kind_result = []
            for status in ['win', 'waiting']:
                kind_result.append({
                    'status': status,
                    'winners': [encode_public_id(x) for x in range(85 if status == 'win' else 30)]
                })
            lottery_result.append({'kind': kind, 'status': kind_result})
        data.append({'classroom': cl, 'kinds': lottery_result})

    env = Environment(loader=FileSystemLoader('./api/templates'))
    template = env.get_template('results.html')
    return template.render(lotteries=data)


if __name__ == '__main__':
    print(gen_data())
