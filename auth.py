import os
import dropbox

class DropboxAuth:
    def __init__(self):
        self.dbx = None
        self.dbx_team = None
        self.access_token = None
        self.refresh_token = None
        self.admin_id = None

        self.admin_id = os.environ.get("DROPBOX_TAGS_ADMIN_ID")
        APP_KEY = os.environ.get("DROPBOX_TAGS_APP_KEY")
        APP_SECRET = os.environ.get("DROPBOX_TAGS_APP_SECRET")
        if not all([APP_KEY, APP_SECRET]):
            print("Set both DROPBOX_TAGS_APP_KEY and DROPBOX_TAGS_APP_SECRET environment variables")
            exit(1)

        REFRESH_TOKEN = os.environ.get("DROPBOX_TAGS_REFRESH_TOKEN")
        if REFRESH_TOKEN:
            self.dbx = dropbox.Dropbox(
                app_key=APP_KEY, app_secret=APP_SECRET, oauth2_refresh_token=REFRESH_TOKEN
            )
            self.dbx_team = dropbox.DropboxTeam(
                app_key=APP_KEY, app_secret=APP_SECRET, oauth2_refresh_token=REFRESH_TOKEN
            )
            self.access_token = self.dbx_team._oauth2_access_token
            self.refresh_token = self.dbx_team._oauth2_refresh_token
        else:
            auth_flow = dropbox.oauth.DropboxOAuth2FlowNoRedirect(
                APP_KEY,
                APP_SECRET,
                token_access_type="offline",
            )
            authorize_url = auth_flow.start()
            print("1. Go to:", authorize_url)
            print('2. Click "Allow" (you might need to log in).')
            print("3. Copy the code Dropbox shows you.")
            auth_code = input("Enter the authorization code here: ").strip()
            oauth_result = auth_flow.finish(auth_code)
            if oauth_result.refresh_token:
                print(
                    f'Run the following command to automated auth:  export DROPBOX_TAGS_REFRESH_TOKEN="{oauth_result.refresh_token}"'
                )
            self.access_token = oauth_result.access_token
            self.refresh_token = oauth_result.refresh_token
            self.dbx = dropbox.Dropbox(oauth2_access_token=oauth_result.access_token)
            self.dbx_team = dropbox.DropboxTeam(oauth2_access_token=oauth_result.access_token)

