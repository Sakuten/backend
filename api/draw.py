import random
from flask import current_app
from api.models import User, Application, db


class NobodyIsApplyingError(Exception):
    """
        The Exception that indicates nobody is applying to the lottery
    """
    pass


def draw_one(lottery):
    idx = lottery.id
    applications = Application.query.filter_by(lottery_id=idx).all()
    if len(applications) == 0:
        raise ValueError({"message": "Nobody is applying to this lottery"})
    try:
        winner_apps = random.sample(
            applications, current_app.config['WINNERS_NUM'])
    except ValueError:
        # if applications are less than WINNER_NUM, all applications are chosen
        winner_apps = applications
    for application in applications:
        application.status = "won" if application in winner_apps else "lose"
        db.session.add(application)

    lottery.done = True
    db.session.add(lottery)
    db.session.commit()
    winners = [User.query.get(winner_app.user_id)
               for winner_app in winner_apps]
    return winners
