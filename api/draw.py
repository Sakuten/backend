import random
from flask import current_app
from api.models import Lottery, Application, db
from itertools import chain
from numpy.random import choice
# typehints imports {{{
from typehint import List, Union, Dict
from api.models import User
# }}}


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


def draw_one(lottery: Lottery) -> Union[List, List[User]]:
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
        set_group_advantage(applications)

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


def draw_one_group_members(applications: List[Application], winners_num: int) -> List[Application]:
    """internal function
        decide win or lose for each group
    """
    winner_apps = []
    loser_apps = []
    winner_reps = []
    loser_reps = []

    def set_group_result(rep: Application, is_won: bool) -> None:
        if is_won:
            status, to_apps, to_reps = "won", winner_apps, winner_reps
        else:
            status, to_apps, to_reps = "lose", loser_apps, loser_reps

        rep.set_status(status)
        to_apps.append(rep)     # record results
        to_reps.append(rep)

        for member in rep.group_members:
            member.own_application.set_status(status)
            to_apps.append(member.own_application)

    def unset_group_result(rep: Application, from_apps: List[Application], from_reps: List[Application]) -> None:
        from_apps.remove(rep)   # remove recorded old results
        from_reps.remove(rep)
        for member in rep.group_members:
            from_apps.remove(member.own_application)

    reps = [app for app in applications if app.is_rep]

    probability_dict = get_probability_dict(applications, winners_num)

    for i, rep in enumerate(reps):
        set_group_result(rep,
                         random.random() < probability_dict[rep])

    n_group_members = sum(len(rep.group_members) + 1
                          for rep in reps)
    n_normal_users = len(applications) - n_group_members

    while (loser_reps and len(winner_apps) < winners_num - n_normal_users or
           len(winner_apps) > winners_num):
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


def draw_one_normal_users(applications: List[Application], winners_num: int) -> List[Application]:
    """internal function
        decide win or lose for each user not belonging to a group
        add applications to the session
    """
    normal_users = [app for app in applications if app.status == "pending"]

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
        application.set_status("won" if application in winner_apps else "lose")
        db.session.add(application)

    return winner_apps


def draw_all_at_index(index: int) -> List[User]:
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


def calc_probabilities(applications: List[Application]) -> List[float]:
    """
        calculate the probability of each application
        return list of the weight of each application showing how likely
        the application is to be chosen in comparison with others
        *the sum of the list is 1*
    """
    sum_advantage = sum(app.get_advantage() for app in applications)
    return [app.get_advantage() / sum_advantage for app in applications]


def get_probability_dict(applications: List[Application], winners_num: int) -> Dict[Application, float]:
    all_probabilities = calc_probabilities(applications)
    return {app: all_probabilities[i] * winners_num
            for i, app in enumerate(applications)}


def set_group_advantage(apps: List[Application]):
    """
        calculate the advantage of the group using group_advantage_calculation
    """
    group_apps = (chain([rep], (member.own_application
                                for member in rep.group_members))
                  for rep in apps if rep.is_rep)
    for group in group_apps:
        advantage = group_advantage_calculation(group)
        for app in group:
            app.set_advantage(advantage)
