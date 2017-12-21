# Deployment
Currently deployment is very quick and dirty.  We push code changes using local git remotes that point towards bare repositories that relay changes via post-receive hooks on the Staging/Live VPS (yes they are all on one) similar to https://www.digitalocean.com/community/tutorials/how-to-set-up-automatic-deployment-with-git-with-a-vps 
Evennia itself is handled via git repos separately on both local dev environments and the VPS (bad).
This goes over how to do things like deploy changes to an environment (staging or live), manage that environment (up or down) in relation to deployment, and a few best practices.

## Setup Local Dev Environment For Deployment
1. Live Remote - `git remote add live ssh://username@thecryingbeard.com:/var/core/core.git`
  => will push to thecryingbeard.com:/var/telnet/thecryingbeard.com
2. Staging Remote - `git remote add staging ssh://username@thecryingbeard.com/var/core/staging.git`
  => will push to thecryingbeard.com:/var/telnet/staging.thecryingbeard.com

and in the vm project...
3. Server Remote - `git remote add cloud ssh://username@thecryingbeard.com/var/core/vm.git`
  => will push to thecryingbeard.com:/var/vm

## Ready to Deploy Checklist
- Make sure the branch you are pushing (usually master) matches latest from the central github repo
  - Do not forget to merge and push all changes first
  - Do not forget to pull/fetch
- Follow this iterative cycle:  Implement locally > commit to branch on your fork > submit pull request to main repo > pass code review > process/integrate pull request to target branch > deploy to Staging > test > push Staging to Live > test
- If you have data model changes, do not forget to run `evennia makemigrations` locally, commit them to VCS, and then test and push these out to Staging and Live subsequently.

## Deploy
1. git push staging master - Push your local master to staging
2. git push live master - Push your local master to live
3. (in vm repo) git push cloud master - Push your local vm master to the server
(and for first time setup, run deploy_secrets.sh from the root game folder on your dev machine)

## Managing evennia on VPS
Occasionally evennia might need some attention that requires someone to ssh into the VPS, especially since there is no automation around service failure, VPS reboots, etc.

### Cold Starting evennia
Pre-requisites:
- ssh access to the VPS
- VPS login account with sudo privileges

On your dev machine...
1. `ssh your_username@thecryingbeard.com`
2. Provide password if prompted.
While sshed into VPS...
3. `byobu new-session -s evennia` - essentially tmux, a multi-plexer that allows you to start evennia and close your ssh session without leaving evennia processes in bad states.
4. `workon evennia-mush` - activate virtualenv which has evennia installed
5. `cd /var/telnet/[environment_target_root_path]` - `.../thecryingbeard.com` for live & `.../staging` for staging
6. `evennia start > server/logs/server.log`
7. `Shift-F6` or `byobu detach` to detach tmux session and not logout

#### Re-attach to first un-named Session
`byobu attach`

#### Re-attach to Named Session
`byobu attach-session -t evennia`

or

`byobu new-session -A -s evennia`
This tries to attach to a session named `evennia`, and if it doesn't exist, it creates a new one called that.

#### Verify evennia has started
In the byobu-tmux session or in your main ssh login session...
`ps -aux | evennia`

### Further Required Reading
Check out https://github.com/evennia/evennia/wiki/Start-Stop-Reload to understand the right action to take for what you are trying to achieve.
It should hold the most up to date information about evennia process management that isn't bespoke to our VPS.
