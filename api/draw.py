import random
from flask import current_app
from api.models import Lottery, Application, db
from itertools import chain


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

        winners = [winner_app.user for winner_app in chain(won_group_members,
                                                           won_normal_users)]

    db.session.add(lottery)
    db.session.commit()

    return winners


def draw_one_group_members(applications, winners_num):
    """internal function
        decide win or lose for each group
        add applications to the session
    """
    winner_apps = []
    loser_apps = []
    winner_reps = []
    loser_reps = []

    def set_group_result(rep, is_won):
        status, to_apps, to_reps = \
            ("won", winner_apps, winner_reps) if is_won \
            else ("lose", loser_apps, loser_reps)

        rep.status = status
        to_apps.append(rep)
        to_reps.append(rep)

        for member in rep.group_members:
            member.application.status = status
            to_apps.append(member.application)

    def unset_group_result(rep, from_apps, from_reps):
        from_apps.remove(rep)
        from_reps.remove(rep)
        for member in rep.group_members:
            from_apps.remove(member.application)

    reps = [app for app in applications if app.is_rep]

    # How likely is a rep to win
    probability = min(winners_num / len(applications), 1)

    for rep in reps:
        set_group_result(rep, random.random() < probability)

    n_group_members = sum(len(rep_app.group_members) + 1 for rep_app in reps)
    n_normal_users = len(applications) - n_group_members

    # when too few groups accidentally won
    while loser_reps and len(winner_apps) < winners_num - n_normal_users:
        new_winner = random.choice(loser_reps)
        unset_group_result(new_winner, loser_apps, loser_reps)
        set_group_result(new_winner, True)

    # when too many groups accidentally won
    while len(winner_apps) > winners_num:
        new_loser = random.choice(winner_reps)
        unset_group_result(new_loser, winner_apps, winner_reps)
        set_group_result(new_loser, False)

    for user in chain(winner_apps, loser_apps):
        db.session.add(user)

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
    """
    lotteries = Lottery.query.filter_by(index=index)

    winners = [draw_one(lottery)
               for lottery in lotteries]

    for lottery in lotteries:
        lottery.done = True
        db.session.add(lottery)
        db.session.commit()

    return winners
