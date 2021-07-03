import argparse
import logging

from argparse_logging import add_logging_arguments

from cli.daemon import Daemon
from generator.generator import Generator


def add_upload_command(parser_group):
    parser_group.add_parser(
        name="upload",
        help="Upload all remaining keys in the queue.",
        description="Checks the queue and tries to upload all keys in it.",
    )


def add_generate_command(parser_group):
    parser_group.add_parser(
        name="generate",
        help="Generate a new key.",
        description="Generate a new key, put it in place and upload it to the keyserver.",
    )


def run():
    parser = argparse.ArgumentParser(
        description="Automatically create and upload new keys."
    )

    logging.getLogger("apscheduler").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    add_logging_arguments(parser)

    subparsers = parser.add_subparsers(
        dest="subparser",
        description="Use the following subcommands to perform the actions once. "
        "If omitted, the keygenerator runs in daemon mode, "
        "automatically rotating keys based on schedule",
    )

    add_generate_command(subparsers)
    add_upload_command(subparsers)

    args = parser.parse_args()

    if "subparser" in args and args.subparser is not None:
        if args.subparser == "upload":
            Generator.upload_queue_to_kms()
        elif args.subparser == "generate":
            Generator.change_key()
    else:
        Daemon.run()


if __name__ == "__main__":
    run()
