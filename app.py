from api.app import create_app
from cryptography.fernet import Fernet

app = create_app({
    'SECRET_KEY': Fernet.generate_key(),
    'SQLALCHEMY_TRACK_MODIFICATIONS': False,
    'SQLALCHEMY_DATABASE_URI': 'sqlite:///db.sqlite',
})


@app.cli.command()
def initdb():
    """
        Initialize Database
    """
    from api.models import db
    db.create_all()


# @app.cli.command define Command-Line commands
# It's a part of Flask

@app.cli.command()
def generate():
    """
        Geenrate test DB for test
    """
    from api.models import Lottery, Classroom, User, db
    from werkzeug.security import generate_password_hash

    total_index = 4
    grades = [5, 6]

    def classloop(f):
        """
            execute function 'f' for all classes
            Args:
                f (function): the function to execute.
        """
        for grade in grades:
            for class_index in range(4):  # 0->A 1->B 2->C 3->D
                f(grade, class_index)

    def create_classrooms(grade, class_index):
        """
            create classroom object and add to Database
            Args:
                grade (int): set grade. 5 or 6
                class_index (int): set class_index. 0->A 1->B 2->C 3->D
        """
        room = Classroom(grade=grade, index=class_index)
        db.session.add(room)

    def create_lotteries(grade, class_index):
        """
            
        """
        room = Classroom.query.filter_by(
            grade=grade, index=class_index).first()
        for perf_index in range(total_index):
            lottery = Lottery(classroom_id=room.id, index=perf_index, done=False)
            db.session.add(lottery)

    classloop(create_classrooms)
    db.session.commit()
    classloop(create_lotteries)
    db.session.commit()

    def make_debug_user(name):
        """
            make debug user and add to Database(Should be deleted?)
            Args:
                name (int): name of debug user
            Return:
                uesr (User): created user instance
        """
        user = User(username=name, passhash=generate_password_hash(name))
        db.session.add(user)
        db.session.commit()
        return user


    make_debug_user('admin')
    for i in range(5):
        make_debug_user(f"example{i}")

    db.session.commit()
