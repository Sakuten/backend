from api.app import create_app

app = create_app({
    'SECRET_KEY': 'secret',
    'ENABLE_SIGNUP': False,
    'SQLALCHEMY_TRACK_MODIFICATIONS': False,
    'SQLALCHEMY_DATABASE_URI': 'sqlite:///db.sqlite',
})


@app.cli.command()
def initdb():
    from api.models import db
    db.create_all()

@app.cli.command()
def generate():
    from api.models import Lottery, Classroom, User, OAuth2Client, db
    from werkzeug.security import generate_password_hash, gen_salt

    total_index=4
    grades=[5,6]

    def classloop(f):
        for grade in grades:
            for class_index in range(4): # 0->A 1->B 2->C 3->D
                f(grade, class_index)

    def create_classrooms(grade, class_index):
        room = Classroom(grade=grade, index=class_index)
        db.session.add(room)

    def create_lotteries(grade, class_index):
        room = Classroom.query.filter_by(grade=grade, index=class_index).first()
        for perf_index in range(total_index):
            lottery = Lottery(classroom_id=room.id, index=perf_index)
            db.session.add(lottery)

    classloop(create_classrooms)
    db.session.commit()
    classloop(create_lotteries)
    db.session.commit()

    def make_debug_user(name):
        user = User(username=name, passhash=generate_password_hash(name))
        db.session.add(user)
        return user

    def make_client(user, scope):
        options = {'client_name': 'client', 'client_uri': 'http://localhost:5000', 'scope': scope, 'redirect_uri': 'http://localhost:5000/auth', 'grant_type': 'authorization_code\r\npassword', 'response_type': 'code', 'token_endpoint_auth_method': 'client_secret_basic'}
        client = OAuth2Client(**options)
        client.user_id = user.id
        client.client_id = gen_salt(24)
        if client.token_endpoint_auth_method == 'none':
            client.client_secret = ''
        else:
            client.client_secret = gen_salt(48)
        db.session.add(client)
        return (client.client_id, client.client_secret)

    admin = make_debug_user('admin')
    print(f"admin: {make_client(admin, 'draw')}")
    for i in range(5):
        example = make_debug_user(f"example{i}")
        print(f"example{i}: {make_client(example, 'apply')}")

    db.session.commit()
