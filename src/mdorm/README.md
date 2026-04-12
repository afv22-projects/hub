# MDorm - A markdown-native ORM for apps that outlive their infrastructure

This is a framework that persists objects in markdown files to ensure it stays human readable outside the app.

The cache assumes that the md files are not externally modified while running. A sync method is included for manual use in case a file is modified, but otherwise the cache will not read from the md files after initial load.

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
