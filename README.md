
<img src="./img/screenshot2.png" align="right" width="300" />

# Cheetah Bot for Telegram

This script lets you run a Telegram Bot that (semi-regularly) posts pictures of cheetahs and (semi-regularly) replies to comments as if it were a cheetah.


## Features

- Will post a cheetah sound or picture when trigged by every Nth message (configurable)
- Messages with profanity or the middle finger emoji will provoke smartass responses.
- Can be configured to only interact wiht allowlisted groups/group IDs.
- When added to a channel, sent the message `help` on a channel, or DMed, it will respond with an "about me" string.
- Configurable rate limiting to prevent accidental flooding of the group.
- Age checking on messages to prevent spamming the group after a hiatus.
- Support for talking to <a href="https://mitmproxy.org/">mitmproxy</a>, if you'd like to monitor network activity.


## Usage

- Talk to <a href="https://t.me/BotFather">@BotFather on Telegram</a> to create a bot.
- Copy down the API token.
- Go to `Bot Settings -> Group Privacy` and click `Turn Off`. This will allow your bot to see messages sent to groups it is in.
- Copy `.env-SAMPLE` to `.env` and fill out the settings.  Settings are described in detail further down.
- Add your bot to one or more groups.  Make sure the group owners are cool with this!
- Start the bot using one of the methods outlined below:


### Docker Compose

- Verify environment settings with with `docker-compose config`
- `docker-compose up`
- To kill, rebuild, and relaunch the container:
   - `docker-compose kill; docker-compose rm -f; docker-compose build; docker-compose up -d; docker-compose logs -f`


### CLI

- `. .env` - Read the variables from our `.env file.
- `export $(cat .env | egrep "^\w" | cut -d= -f1)` - Mark those varaibles as exportable.
- `pip install -r ./requirements.txt`
- `./cheetah-bot.py` - Usage arguments will be displayed.

### Development mode

- `. .env` - Read the variables from our `.env file.
- `export $(cat .env | egrep "^\w" | cut -d= -f1)` - Mark those varaibles as exportable.
- `./bin/devel.sh` - This will start a Docker container with a `bash` shell.  Follow the instructions on screen to proceed.
   - `./bin/run-bot.sh` - Meant to be run inside of a `bash` shell spawned by `devel.sh`, this will print the environment variables you're using before running the bot and give you a chance to change them.
   - `./bin/import-mitmproxy-cert.py` - Run this inside of a `bash shell spawned by `devel.sh` to import the mitmproxy root certificate.
- `./bin/build.sh` - Build the container only.  This is called by `bin/devel.sh`.
- `./bin/docker-compose-build-and-run.sh` - Build and run the container with `docker-compose`, and tail the output.


## Configuration

- `GROUP_IDS` - Optional. List of group IDs (separated by spaces) where the bot should operate.
   - If unsure of the group ID, use `GROUP_NAMES`, and the ID will show up in the logging messages from the bot.
   - If neither this nor `GROUP_NAMES` are specified, then any group may add this bot.
- `GROUP_NAMES` - Optional. A list of strings (separated by spaces) which are then substring matched against the name of the gorup as messages come in.  Be careful with this, because `test` will match `test`, `test2`, and `test1234`, for example.  Note that a string can't have a space in it, since the space is a delimiter.  
- `ACTIONS` - Used for rate-limiting.  How many messages can be sent in a given period?
- `PERIOD` - Used for rate-limiting. How long is the period in seconds?
   - Note that the queue for sending messages is refilled based on time-elapsed.
   - For example, ACTIONS=2 and PERIOD=10 means that .2 will be added to the queue every second.
   - So if a message is sent at second 0, the queue is now 1, at 1 second, it is 1.2, then 1.4 at 2 seconds, etc. until the queue maxes out at 2.
- `POST_EVERY` - Posts wehn tirggered by every Nth message in the group.  100 is usually a good number.
   - Optional.  If not specified, the cheetah bot will not issue any unsolicited replies.
- `POSTS_FILE` - CSV File containing image comments and optional images to go with them.  Defaults to `./posts.txt`.
   - Default images can be found Imgur: https://imgur.com/gallery/iisbC6p
- `PROFANITY_REPLY` - Set to 1 for the bot to reply to profanity it sees in channels.  This can be annoying, so it's off by default.


## Good Testing Practices

I'm not even sure how to unit test against Telegram, so I have manual instructions here for now:

- Start the bot with default settings, except for... 
   - `POST_EVERY`, which should be 2.
   - `ACTIONS` should be 2.
   - `PERIOD` should be 10.
   - e.g. `POST_EVERY=2 ACTIONS=2 PERIOD=10 /mnt/bin/run-bot.sh`
- Send 2 test messages to the group, ensure the bot replies to the second message.
- Type `chee` and ensure the bot replies.
- Type an f-bomb in a message and make sure the bot catches that.
- Type a message with the bot tagged in it and ensure it replies
   - Repeat a few times to make sure it does text AND images
- Reply to a message from the bot in the gorup and ensure it replies
   - Repeat a few times to make sure it does text AND images
- Spam the bot with messages until you exhaust the quota (it won't take long with these settings) and make sure it goes to sleep than wakes back up.
- Finally, send a DM to the bot and make sure it replies.

### Unit Testing

- `bin/pytest` - Run unit tests.  This script is just a wrapper to add `lib/` into `$PYTHONPATH`.
   - `-s` - Specify `-s` to print contents of stdout. 
   - `-k string` - Run only tests that match that substring
   - `--log-cli-level=info` - Specify to print logging messages.
      - Note that `--log-cli-level=info` may break some tests, and there are calls to get quota values in logging messages.  I warned ya!
   - `file` Specify a unit test file to run

There is a great blog post about mocking <a href="https://yeraydiazdiaz.medium.com/what-the-mock-cheatsheet-mocking-in-python-6a71db997832">over here</a>.


## Mitmproxy Support

If you'd like to send traffic through `mitmproxy` for testing, here's how to make that happen: 

- Make sure `mitmproxy` is installed
- Edit `.env` and set the `HTTP_PROXY` and `HTTPS_PROXY` values to `http://YOUR_IP:8080/`
   - Note that `YOUR_IP` is NEITHER localhost NOR 127.0.0.1.  It must be the local network IP of your machine, since localhost would be just the Docker container.
- Copy the CA for mitmproxy to this directory: `cp ~/.mitmproxy/mitmproxy-ca-cert.pem .`
   - If this fails, try running `mitmproxy` once
- Start the Docker container in devel mode: `./bin/devel.sh`
- Run the script `./bin/import-mitmproxy-cert.py` inside the shell to ingest the CA for mitmproxy.
   - If this is not done, you'll see a `certificate verify failed` error and the bot will not run.
- Make sure `mitmproxy`, `mitmdump`, or `mitmweb` is running on the host machine.
   - If it's not running, you'll see a `Connection refused` error and the bot will not run.


## Future Features to add

- [ ] Ability for group admins to configure limits on bot
- [ ] Add `POST_RANDOM` with a percent float that maxes out at `.10`


## Credits

- Jan De Dobbeleer for <a href="./bin/import-mitmproxy-cert.py">his excellent post</a> on how to talk to mitmproxy from a Python app in a Docker container.


## Copyrights

- The code is copyright by me, and the license is in <a href="LICENSE">LICENSE</a>.
- The images it uses are copyright via their owners.


## Contact

My email is doug.muth@gmail.com.  I am also <a href="http://twitter.com/dmuth">@dmuth on Twitter</a> 
and <a href="http://facebook.com/dmuth">Facebook</a>!



