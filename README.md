

# Cheetah Bot

This script lets you run a Telegram Bot that (semi-regularly) posts pictures of cheetahs and (semi-regularly) replies to comments as if it were a cheetah.


## Features

- [ ] Will post cheetah pictures to the group semi-regularly
- [ ] Will reply to the last message with cheetah sounds semi-regularly
- [x] Any messages sent to it containing profanity or the middle finger emojii will cause the bot to reply with smartass responses.
- [x] Will only interact with allowlisted groups/group IDs.
- [ ] Rate limiting to prevent accidental flooding of the room.



## Usage

- Talk to <a href="https://t.me/BotFather">@BotFather on Telegram</a> to create a bot.
- Copy down the API token.
- Go to `Bot Settings -> Group Privacy` and click `Turn Off`. This will allow your bot to get messages sent to groups it is in.
- Add your bot to one or more groups.  Make sure the group owners are cool with this.
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


