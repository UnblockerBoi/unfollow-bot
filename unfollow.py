import argparse
import configparser
import json
import sys

from bot import Bot

EXCLUSIONS_FILE = "exclude.txt"


def load_exclusions(section: str) -> list[str]:
    """
    Looks for file named 'config.ini' to load credentials from.

    returns: a list of usernames to exclude.
    """

    items = []

    try:
        config = configparser.ConfigParser()
        config.read("config.ini")
        items = json.loads(config.get(section, "exclusions"))
    except KeyError as e:
        print(f"Configuration key error: {e}")
        sys.exit(1)

    return items


def get_credentials(section: str) -> tuple[str, str]:
    """
    Looks for file named 'config.ini' to load credentials from.
    """

    config = configparser.ConfigParser()
    config.read("config.ini")
    section_user, section_pass = "", ""

    try:
        section_user = config[section]["username"]
        section_pass = config[section]["password"]
    except KeyError as e:
        print(f"Configuration key error: {e}")
        sys.exit(1)

    return section_user, section_pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="unfollow-bot")
    parser.add_argument(
        "-e", "--exclude", action="store_true", help="Run with excluded accounts"
    )
    parser.add_argument(
        "credentials",
        type=str,
        help="Section in 'credentials.ini' containing the credentials to use",
    )

    args = parser.parse_args()
    cred_section = args.credentials

    exclude = load_exclusions(cred_section) if args.exclude else []
    username, password = get_credentials(cred_section)

    bot = Bot(username, password, exclude)
    bot.run()
