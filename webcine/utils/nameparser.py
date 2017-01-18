import logging

import re

REGEX_EPISODE = re.compile(r'(?:S(\d+)E(\d+)|[^0-9xh](\d)(\d\d)[^0-9p])', re.IGNORECASE)


def parse_episode_number(filename):
    try:
        match = REGEX_EPISODE.search(filename)
        if match:
            groups = list(match.groups())
            groups = list(filter(None, groups))
            return int(groups[0]), int(groups[1])
        else:
            logging.error('No episode number in filename: {}'.format(filename))
            return None
    except Exception:
        logging.error('Cannot parse episode number in: {}'.format(filename))
        if groups:
            logging.error(groups)
        raise
