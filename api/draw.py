import random
from flask import current_app
from api.models import User, Lottery, Application, db
from itertools import chain


class AlreadyDoneError(Exception):
    """
        The Exception that indicates the lottery has already done
    """
    pass


def draw_one(lottery):
    """
        Draw the specified lottery
        Args:
          lottery(Lottery): The lottery to be drawn
        Return:
          winners([User]): The list of users who won
        Raises:
            AlreadyDoneError
    """
    if lottery.done:
        raise AlreadyDoneError()

    lottery.done = True

    idx = lottery.id
    applications = Application.query.filter_by(lottery_id=idx).all()

    if len(applications) == 0:
        winners = []
    else:
        winners_num = current_app.config['WINNERS_NUM']

        won_group_members = draw_one_group_members(applications, winners_num)

        rest_winners_num = winners_num - len(won_group_members)
        won_normal_users = draw_one_normal_users(applications,
                                                 rest_winners_num)

        winners = [User.query.get(winner_app.user_id)
                   for winner_app in chain(won_group_members,
                                           won_normal_users)]

    db.session.add(lottery)
    db.session.commit()

    return winners


def draw_one_group_members(applications, winners_num):
    """internal function
        decide win or lose for each group
        add applications to the session
    """
    reps = [app for app in applications if app.is_rep]

    # How likely is a rep to win
    probability = min(winners_num / len(applications), 1)

    winner_reps = [rep for rep in reps if random.random() < probability]

    winner_apps = set()
    is_full = False

    for rep in reps:
        # when accidentally too many reps 'won' the lottery
        is_full = is_full or \
            len(winner_apps) + len(rep.group_members) + 1 > winners_num

        is_won = (not is_full) and rep in winner_reps
        status = "won" if is_won else "lose"

        rep.status = status
        db.session.add(rep)
        if is_won:
            winner_apps.add(rep)

        for member_id in rep.group_members:
            member = Application.query.filter_by(user_id=member_id).first()
            member.status = status
            db.session.add(member)
            if is_won:
                winner_apps.add(member)

    return winner_apps


def draw_one_normal_users(applications, winners_num):
    """internal function
        decide win or lose for each user not belonging to a group
        add applications to the session
    """
    normal_users = [app for app in applications if app.status == "pending"]
    try:
        winner_apps = random.sample(normal_users, winners_num)
    except ValueError:
        # if applications are less than winners_num, all applications win
        winner_apps = normal_users

    for application in normal_users:
        application.status = "won" if application in winner_apps else "lose"
        db.session.add(application)

    return winner_apps


def draw_all_at_index(index):
    """
        Draw all lotteries in the specific index
        Args:
          index(int): zero-based index that indicates the time of lottery
        Return:
          winners([[User]]): The list of list of users who won
        Raises:
            AlreadyDoneError
    """
    lotteries = Lottery.query.filter_by(index=index)
    if any(lottery.done for lottery in lotteries):
        raise AlreadyDoneError()

    winners = [draw_one(lottery)
               for lottery in lotteries]

    for lottery in lotteries:
        lottery.done = True
        db.session.add(lottery)
        db.session.commit()

    return winners
