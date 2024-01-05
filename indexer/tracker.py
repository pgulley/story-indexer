"""
keep track of queued files.

isolates implementation of record keeping for queuers.
would prefer something replicated/durable (S3, AWS SimpleDB, ES)
see https://github.com/mediacloud/story-indexer/issues/203
"""

import dbm
import logging
import os
import time
from enum import Enum
from typing import Any, Callable, Type, cast

from indexer.app import AppException

logger = logging.getLogger(__name__)


class TrackerException(AppException):
    """
    thrown when file is in some state other than NOT_STARTED
    """


class FileStatus(Enum):
    """
    file status: values (except NOT_STARTED) may be thrown
    as Exception by FileTracker __init__.
    All values are instances of FileStatus
    """

    NOT_STARTED = 1
    STARTED = 2  # processing started
    EXPIRED = 3  # started, not finished in expected time
    FINISHED = 4


class FileTracker:
    def __init__(self, app_name: str, fname: str):
        self.app_name = app_name
        self.fname = fname
        # raise exception FileStatus.THING if status not NOT_STARTED??

    def __enter__(self) -> "FileTracker":
        self._set_status(FileStatus.STARTED)
        return self

    def __exit__(self, type: Any, value: Any, traceback: Any) -> None:
        if traceback:
            self._set_status(FileStatus.NOT_STARTED)
        else:
            self._set_status(FileStatus.FINISHED)
        self._cleanup()

    def _set_status(self, status: FileStatus) -> None:
        raise NotImplementedError("_set_status not overridden")

    def _cleanup(self) -> None:
        raise NotImplementedError("_cleanup not overridden")


class LocalFileTracker(FileTracker):
    """
    a file tracker that uses a local directory for data storage
    """

    def __init__(self, app_name: str, fname: str):
        super().__init__(app_name, fname)
        self._app_data_dir = "/app/data"  # os.environ.get("APP_DATA")?
        if not os.path.isdir(self._app_data_dir):
            logger.warning("%s directory not found", self._app_data_dir)
            self._app_data_dir = "."
        self._work_dir = os.path.join(self._app_data_dir, self.app_name)
        if not os.path.isdir(self._work_dir):
            os.mkdir(self._work_dir)


class DBMFileTracker(LocalFileTracker):
    """
    HOPEFULLY TEMPORARY!!!
    NOTE!!!! GDBM locks file for exclusive access!!
    Will see:
    _gdbm.error: [Errno 11] Resource temporarily unavailable

    Local concurrent access is likely safe?
    NFS access at your own risk/funeral.
    """

    def __init__(self, app_name: str, fname: str):
        super().__init__(app_name, fname)
        path = os.path.join(self._work_dir, "file-tracker.db")
        # GDBM takes advisory lock!!! cleanup *MUST* be called!!!
        self._dbm = dbm.open(path, "c", 0o644)
        status, ts = self._dbm.get(fname, b"NOT_STARTED,0").decode().split(",")
        if status != "NOT_STARTED":
            self._cleanup()
            raise TrackerException(getattr(FileStatus, status).name)

    def _set_status(self, status: FileStatus) -> None:
        if status == FileStatus.NOT_STARTED:
            del self._dbm[self.fname]
        else:
            status_string = f"{status.name},{int(time.time())}"
            self._dbm[self.fname] = status_string.encode()
        sync = getattr(self._dbm, "sync")
        if sync is not None:
            csync = cast(Callable[[], None], sync)
            csync()

    def _cleanup(self) -> None:
        """
        NOTE! GDBM takes exclusive lock!!!
        """
        if self._dbm:
            self._dbm.close()
            del self._dbm


def get_tracker(app_name: str, fname: str) -> FileTracker:
    cls = DBMFileTracker  # complex decision process
    return cls(app_name, fname)
