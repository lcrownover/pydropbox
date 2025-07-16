# Dropbox Team Folder Tag Scanner

`tag_report.py` will scan all team folders for the `index_FOO` tag and return a json string resembling:

```json
[{"name": "Team-Folder1", "index": "foo"},{"name": "Team-Folder2", "index": "otherindex"}]
```

It will output any errors on stderr such as the index tag missing or some other issue.

## Dependencies

The only dependency for these tools is the `dropbox` package which you can install with:

```bash
pip install dropbox
```

## Configuration

First, [create a dropbox API app](https://www.dropbox.com/developers/apps) to use as your authentication. 

As far as permissions go for the scopes, I configured mine to have all the `.read` permissions available.

Copy down the `App key` and `App secret`, then set them in your environment variables:

```bash
export DROPBOX_TAGS_APP_KEY="your app key"
export DROPBOX_TAGS_APP_SECRET="your app secret"
```

Once these are set, run `get_admin_id.py --username YOURUSER` to get the dropbox ID of your account, then set that environment variable as well:

```bash
export DROPBOX_TAGS_ADMIN_ID="your id here"
```

Now you can run `tag_report.py`.
