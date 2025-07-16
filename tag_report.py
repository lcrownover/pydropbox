#!/usr/bin/env python3

import multiprocessing as mp
import sys
import json

from dropbox.common import PathRoot
from dropbox.team import GroupSelector

from auth import DropboxAuth

def process_team_folder(tf, dbx_team, dbx_admin) -> dict | None:
    out = {"name": tf.name}
    index = ""
    if not tf.status.is_active():
        return
    # pprint(tf)
    # if not tf.name == "USS-Admin":
    #     continue
    # print(f"{tf.name}: ", end="", flush=True)
    # find user to impersonate, just use the first team member available
    impersonate_id = ""
    members_res = dbx_admin.sharing_list_folder_members(tf.team_folder_id)
    if len(members_res.users) == 0 and len(members_res.groups) == 0:
        raise Exception(f"no users or groups assigned to team folder: {tf.name}")
    # pprint(members_res)
    if len(members_res.users) > 0:
        for member in members_res.users:
            if member.user.team_member_id is not None:
                impersonate_id = member.user.team_member_id
                break
    # no useful user, check groups
    if impersonate_id == "":
        for g in members_res.groups:
            if g.group.member_count == 0:
                return
            gs = GroupSelector.group_id(g.group.group_id)
            grp_res = dbx_team.team_groups_members_list(gs)
            impersonate_id = grp_res.members[0].profile.team_member_id
            break
    # impersonate the team member
    dbx_user = dbx_team.as_user(impersonate_id)

    # set the root
    root_ns = dbx_user.users_get_current_account().root_info.root_namespace_id
    dbx_user = dbx_user.with_path_root(PathRoot.root(root_ns))
    folders = dbx_user.files_list_folder("")
    for f in folders.entries:
        if f.name == tf.name:
            tags_res = dbx_user.files_tags_get([f.path_lower])
            for pt in tags_res.paths_to_tags:
                for t in pt.tags:
                    ugt = t.get_user_generated_tag()
                    if ugt.tag_text.startswith("index_"):
                        index = ugt.tag_text.replace("index_", "")

    if index == "":
        raise Exception(f"failed to find index for team folder: {tf.name}")

    out['index'] = index
    return out

def worker(q: mp.Queue, f, *args):
    try:
        index = f(*args)
        q.put((index, None))
    except Exception as e:
        q.put((None, e))


def main():
    auth = DropboxAuth()
    if auth.admin_id is None:
        sys.stderr.write("You must set DROPBOX_TAGS_ADMIN_ID to get team folder data. See the README.md for instructions.\n")
        exit(1)
    dbx_team = auth.dbx_team
    root_admin_id = auth.admin_id

    res = dbx_team.team_team_folder_list()
    team_folders = res.team_folders
    while res.has_more:
        res = dbx_team.team_team_folder_list_continue(res.cursor)
        team_folders.extend(res.team_folders)

    dbx_admin = dbx_team.as_admin(root_admin_id)

    q = mp.Manager().Queue()
    procs = []

    for tf in team_folders:
        dbx_team = dbx_team.clone()
        dbx_admin = dbx_admin.clone()
        p = mp.Process(target=worker, args=(q, process_team_folder, tf, dbx_team, dbx_admin,))
        p.start()
        procs.append(p)

    for p in procs:
        p.join()

    team_folder_records, errors = [], []
    while not q.empty():
        res, err = q.get()
        if err is not None:
            errors.append(err)
        if res:
            team_folder_records.append(res)

    for e in errors:
        sys.stderr.write(f"Error: {e}\n")

    print(json.dumps(team_folder_records))

if __name__ == "__main__":
    main()
