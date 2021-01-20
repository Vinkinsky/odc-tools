import click

import logging
from odc.aws.queue import get_queue, get_messages
from ._cli_common import main, setup_logging

setup_logging()

@main.command("redrive_to_queue")
@click.argument("queue", required=True)
@click.argument("to-queue", required=True)

@click.option(
    "--limit",
    "-l",
    type=int,
    help="Limit the number of messages to transfer.",
    default=None,
)
@click.option(
    "--dryrun",
    is_flag=True,
    default=False,
    help="Don't actually do real work"
)
def redrive_to_queue(queue, to_queue, limit, dryrun):
    """
    Redrives all the messages from the given sqs queue to the destination
    """

    _log = logging.getLogger(__name__)

    dead_queue = get_queue(queue)
    alive_queue = get_queue(to_queue)

    messages = get_messages(dead_queue)

    count = 0

    count_messages = dead_queue.attributes.get("ApproximateNumberOfMessages")

    if count_messages == 0:
        _log.info("No messages to redrive")
        return

    if not dryrun:
        for message in messages:
            response = alive_queue.send_message(MessageBody=message.body)
            if response["ResponseMetadata"]["HTTPStatusCode"] == 200:
                message.delete()
                count += 1
                if limit and count >= limit:
                    break
            else:
                _log.error(f"Unable to send message {message} to queue")
        _log.info(f"Completed sending {count} messages to the queue")
    else:
        _log.warning(
            f"DRYRUN enabled, would have pushed approx {count_messages} messages to the queue"
        )
