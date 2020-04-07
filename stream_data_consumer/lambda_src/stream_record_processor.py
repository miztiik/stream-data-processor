# -*- coding: utf-8 -*-
"""
.. module: get_video_metadata.py
    :Actions: Get 
    :copyright: (c) 2020 Mystique.,
.. moduleauthor:: Mystique
.. contactauthor:: miztiik@github issues
"""

import json
import base64
import logging
import os

__author__ = 'Mystique'
__email__ = 'miztiik@github'
__version__ = '0.0.1'
__status__ = 'production'


class global_args:
    """ Global statics """
    OWNER = 'Mystique'
    ENVIRONMENT = 'production'
    MODULE_NAME = 'stream_record_processor'
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO').upper()


def set_logging(lv=global_args.LOG_LEVEL):
    """ Helper to enable logging """
    logging.basicConfig(level=lv)
    LOGGER = logging.getLogger(__name__)
    LOGGER.setLevel(lv)
    return LOGGER


def lambda_handler(event, context):
    # Initialize Logger
    global LOGGER
    LOGGER = set_logging(logging.INFO)
    resp = {"status": False, "records": ""}
    LOGGER.info(f'Event: {event}')

    try:
        if event.get('Records'):
            for record in event['Records']:
                # Kinesis data is base64 encoded so decode here
                payload = base64.b64decode(record["kinesis"]["data"])
                LOGGER.info(f"Decoded payload: {str(payload)}")
            LOGGER.info(f'{{"records_processed":{len(event.get("""Records"""))}}}')
            resp["status"] = True
    except Exception as e:
        LOGGER.error(f"ERROR:{str(e)}")
        resp['error_message'] = str(e)

    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": resp
        })
    }


if __name__ == '__main__':
    lambda_handler({}, {})
