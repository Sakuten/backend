import argparse
import sys
import os

sys.path.append(os.getcwd())
from app import app
from api.models import db, User, Application
from cards.id import decode_public_id


def find_user(arg):
    if len(arg) == 4:
        public_id = decode_public_id(arg)
        target_user = db.session.query(User).filter_by(public_id=public_id).first()
        return target_user
    elif len(arg) == 32:
        return db.session.query(User).filter_by(secret_id=arg).first()
    else:
        raise argparse.ArgumentTypeError("Invalid format")

def find_application(user):
    apps = db.session.query(Application).all()
    if not apps:
        print("No application yet")
        exit()
    return max(apps, key=lambda app: app.lottery.index)

def valid_status(arg):
    if arg not in ["pending", "won", "lose", "waiting"]:
        raise argparse.ArgumentTypeError("Illegal status")
    return arg


parser = argparse.ArgumentParser(description="Manipulate Application's status")
parser.add_argument("--id", type=str, required=True,
                    help="Public ID or Secret ID of User that exists in DB")
parser.add_argument("--new_status", type=valid_status, required=True,
                    help="New status to be set - [pending|won|lose|waiting]")
parser.add_argument("-y", "--yes",
                    help="Silence confirmation",
                    action="store_true")



with app.app_context():
    args = parser.parse_args()

    target_user = find_user(args.id)
    target_application = find_application(target_user)
    new_status = args.new_status

    print(f"Going to set status of {target_user} to {new_status}")
    if not args.yes:
        while True:
            print("Are you sure? [yn] ", end="")
            ans = input()
            if ans == "n" or ans == "N":
                exit()
            elif ans != "y" and ans != "Y":
                continue
            else:
                break

    target_application.status = new_status

    db.session.add(target_application)
    db.session.commit()