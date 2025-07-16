from auth import DropboxAuth
import argparse
from dropbox.team import UserSelectorArg


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-u",
        "--username",
        required=True,
        help="Username of the user you want to get the ID for",
    )
    args = parser.parse_args()

    auth = DropboxAuth()
    dbx_team = auth.dbx_team
    selector = UserSelectorArg.email(f"{args.username}@uoregon.edu")
    res = dbx_team.team_members_get_info([selector])
    if res is None or len(res) == 0:
        print("Failed to get username for user :(")
    userid = res[0].get_member_info().profile.team_member_id
    print(userid)


if __name__ == "__main__":
    main()
