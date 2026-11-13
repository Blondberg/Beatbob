class MusicError(Exception):
    """An expected playback failure that can be explained to the user"""


class QueueLimitReaced(MusicError):
    pass
