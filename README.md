

# Cheetah Bot

This script lets you run a Telegram Bot that (semi-regularly) posts pictures of cheetahs and (semi-regularly) replies to comments as if it were a cheetah.


## Features

- Will reply to every Nth message with cheetah sounds or pictures. (configurable)
- Messages with profanity or the middle finger emoji will provoke smartass responses.
- Will only interact with allowlisted groups/group IDs.
- Configurable rate limiting to prevent accidental flooding of the group.
- Age checking on messages to prevent spamming the group after a hiatus.


## Usage

- Talk to <a href="https://t.me/BotFather">@BotFather on Telegram</a> to create a bot.
- Copy down the API token.
- Go to `Bot Settings -> Group Privacy` and click `Turn Off`. This will allow your bot to see messages sent to groups it is in.
- Add your bot to one or more groups.  Make sure the group owners are cool with this!
- Start the bot using one of the methods outlined below:


### CLI

- `pip install -r ./requirements.txt`
- `./cheetah-bot.py` - Usage arguments will be displayed.


### Docker

- `cp .env-SAMPLE .env`
- Edit .env with your token and allowed groups.
- `./bin/go.sh`


### Docker Compose

- `cp .env-SAMPLE .env`
- Edit .env with your token and allowed groups.
- Verify with `docker-compose config`
- `docker-compose up`


## Development

- `./build.sh` - Build the Docker container with required dependencies
- `./devel.sh` - Build the container and spawn an interactive shell
- `./go.sh` - Used to run the container


