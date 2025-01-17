import logging

# create formatter
formatter = logging.Formatter('%(asctime)s | %(name)s | %(levelname)s.%(funcName)s : %(message)s')


def get_stream_handler():
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)
    stream_handler.setFormatter(formatter)
    return stream_handler


def get_logger(name):
    logger = logging.getLogger(name)
    logger.addHandler(get_stream_handler())
    logger.setLevel(logging.INFO)
    uvicorn_logger = logging.getLogger("uvicorn")
    uvicorn_logger.propagate = False
    return logger
