import random
from flask import current_app
from api.models import Lottery, Application, db
from itertools import chain
from numpy.random import choice
from datetime import date


class GroupAdvantage:
    @staticmethod
    def minimum(group):
        return min(app.get_advantage() for app in group)

    @staticmethod
    def average(group):
        group = list(group)
        return sum(app.get_advantage() for app in group) / len(group)

    @staticmethod
    def rep(group):
        return next(filter(lambda app: app.is_rep, group)).get_advantage()


group_advantage_calculation = GroupAdvantage.average


def draw_one(lottery):
    """
        Draw the specified lottery
        Args:
          lottery(Lottery): The lottery to be drawn
        Return:
          applications([User]): The list of applications handled
    """
    lottery.previous_on = date.today()

    idx = lottery.id
    applications = (
        Application.query
        .filter_by(lottery_id=idx, created_on=date.today())
        .all()
    )

    if len(applications) == 0:
        winners = []
    else:
        set_group_advantage(applications)

        winners_num = current_app.config['WINNERS_NUM']
        waiting_num = current_app.config['WAITING_NUM']

        won_group_members = draw_one_group_members(
            applications, winners_num, set_just=True,
            target_status="pending", win_status="won",
            lose_status="waiting-pending")

        rest_winners_num = winners_num - len(won_group_members)
        won_normal_users = draw_one_normal_users(
            applications, rest_winners_num,
            target_status="pending", win_status="won",
            lose_status="waiting-pending")

        winners = [winner_app.user for winner_app in chain(won_group_members,
                                                           won_normal_users)]

        waiting_group_members = draw_one_group_members(
            applications, waiting_num, set_just=False,
            target_status="waiting-pending",
            win_status="waiting", lose_status="lose")

        rest_waiting_num = waiting_num - len(waiting_group_members)
        draw_one_normal_users(
            applications, rest_waiting_num,
            target_status="waiting-pending",
            win_status="waiting", lose_status="lose")

    db.session.add(lottery)
    db.session.commit()

    return winners


def draw_one_group_members(applications, winners_num, set_just=True,
                           **kwargs):
    """internal function
        decide win (waiting) or lose for each group
    """
    target_status = \
        kwargs['target_status'] if 'target_status' in kwargs else "pending"
    win_status = \
        kwargs['win_status'] if 'win_status' in kwargs else "won"
    lose_status = \
        kwargs['lose_status'] if 'lose_status' in kwargs else "lose"

    target_apps = [app for app in applications if app.status == target_status]
    winner_apps = []
    loser_apps = []
    winner_reps = []
    loser_reps = []

    def set_group_result(rep, is_won):
        if is_won:
            status, to_apps, to_reps = win_status, winner_apps, winner_reps
        else:
            status, to_apps, to_reps = lose_status, loser_apps, loser_reps

        rep.set_status(status)
        to_apps.append(rep)     # record results
        to_reps.append(rep)

        for member in rep.group_members:
            member.own_application.set_status(status)
            to_apps.append(member.own_application)

    def unset_group_result(rep, from_apps, from_reps):
        from_apps.remove(rep)   # remove recorded old results
        from_reps.remove(rep)
        for member in rep.group_members:
            from_apps.remove(member.own_application)

    reps = [app for app in target_apps if app.is_rep]

    probability_dict = get_probability_dict(target_apps, winners_num)

    for i, rep in enumerate(reps):
        set_group_result(rep,
                         random.random() < probability_dict[rep])

    n_group_members = sum(len(rep.group_members) + 1
                          for rep in reps)
    n_normal_users = len(target_apps) - n_group_members

    def adjust():
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

    if not set_just:
        adjust()
        for user in chain(winner_apps, loser_apps):
            db.session.add(user)

        return winner_apps

    while (loser_reps and len(winner_apps) < winners_num - n_normal_users or
           len(winner_apps) > winners_num):
        adjust()

    for user in chain(winner_apps, loser_apps):
        db.session.add(user)

    return winner_apps


def draw_one_normal_users(applications, winners_num, **kwargs):
    """internal function
        decide win or lose for each user not belonging to a group
        add applications to the session
    """
    target_status = \
        kwargs['target_status'] if 'target_status' in kwargs else "pending"
    win_status = \
        kwargs['win_status'] if 'win_status' in kwargs else "won"
    lose_status = \
        kwargs['lose_status'] if 'lose_status' in kwargs else "lose"

    normal_users = [app for app in applications if app.status == target_status]

    if len(normal_users) <= winners_num or not normal_users:
        # if pending applications are less than winners_num,
        # all applications win
        winner_apps = normal_users
    else:
        winner_apps = choice(
            normal_users, winners_num,
            replace=False,      # no duplication
            p=calc_probabilities(normal_users))

    for application in normal_users:
        application.set_status(win_status if application in winner_apps
                               else lose_status)
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
        db.session.add(lottery)
    db.session.commit()

    return winners


def calc_probabilities(applications):
    """
        calculate the probability of each application
        return list of the weight of each application showing how likely
        the application is to be chosen in comparison with others
        *the sum of the list is 1*
    """
    sum_advantage = sum(app.get_advantage() for app in applications)
    return [app.get_advantage() / sum_advantage for app in applications]


def get_probability_dict(applications, winners_num):
    all_probabilities = calc_probabilities(applications)
    return {app: all_probabilities[i] * winners_num
            for i, app in enumerate(applications)}


def set_group_advantage(apps):
    """
        calculate the advantage of the group using group_advantage_calculation
    """
    def group_apps(rep):
        members = [member.own_application for member in rep.group_members]
        members.append(rep)
        return members

    reps = (app for app in apps if app.is_rep)
    groups = (group_apps(rep) for rep in reps)
    for group in groups:
        advantage = group_advantage_calculation(group)
        for app in group:
            app.set_advantage(advantage)
