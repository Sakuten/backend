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
    from api.models import Lottery, Classroom, db

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
