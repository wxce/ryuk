import logging


def create_logger(name):
    """Creates and returns a custom logger with the given name. Use from cogs with __name__"""
    # Create a custom logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Create handlers
    handler = logging.StreamHandler()
    handler.setLevel(logging.INFO)

    # Create formatters and add it to handlers
    formatter = logging.Formatter('%(asctime)s %(levelname)-7s %(funcName)18s() :: %(message)s', datefmt='[%H:%M:%S]')
    handler.setFormatter(formatter)

    # Add handlers to the logger
    logger.addHandler(handler)

    # logger.warning('This is a warning')
    # logger.error('This is an error')
    # logger.info('This is info')

    # print(f"logger created as {name}")
    return logger


def format_log(ctx, rest):
    """Formats a nice log message from given context and additional values"""
    if rest == "":
        end = ""
    else:
        end = f":: {rest}"
    return f'{ctx.message.guild} | {ctx.message.author}: "{ctx.message.content}" {end}'
