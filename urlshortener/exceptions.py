class StorageError(Exception):
    pass


class AlreadyExists(StorageError):
    pass


class NotFound(StorageError):
    pass


class NoAvailableIDs(StorageError):
    pass
