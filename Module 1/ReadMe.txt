While installing python select the radio option set the environment variables to be able to run the python files directly from the terminal or Command prompt. 
If not you need to set the environment variables directly from the control panel.

To deploy the app on the remote server we set up a VPS (Virtual private server), to connect to this server we use ssh (sercure shell) protocol to gain control over the remote server. 
For such operations PuTTy is one of the best open source ssh client.

While pushing files in to git there might be some integrity or to be more specific merge issues which would deny the push request since the both the local and remote versions to be same in order to push into git.
If you want to give more priority to your local version you can use a git force command (git push origin --force) to push your local version in to the git directory.   