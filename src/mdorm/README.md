# MDorm - Save your data to md files

## File Persistence

### Local

All you need is a file path for saving to your local machine.

### Dropbox

1. Go to https://www.dropbox.com/developers/apps
2. Create an app with the following permissions:
   - `files.metadata.write`
   - `files.content.write`
   - `files.content.read`
3. Generate a personal access token
4. Create the DropboxFiles object for MDorm initialization
   - `DropboxFiles(access_token, root_path="/yourapp")`
