#!/usr/bin/env python
"""
Keeps a persistent JSON log of which videos SLEAPyTracks has seen and processed.

The log is called ``SLEAPyTracks_processing_log.json``. It does not have to sit
in the directory that is being tracked: ``find_log_dir`` walks up from that
directory and uses the first existing log it finds, so one log placed in a year
folder covers every video beneath it. Videos are registered with status
"Unprocessed" as soon as they are found, before any prediction runs, and updated
to "finished" or "error" afterwards.

The log is a JSON object keyed by the absolute path of the video file. Each entry
holds the columns below:

    video_path              directory the video lives in
    video_name              file name of the video
    status                  Unprocessed | finished | error
    first_seen              when the video was first added to the log
    last_processed          when it was last processed successfully
    version_last_processed  SLEAPyTracks version used for the last success
    last_attempt            when processing was last attempted
    last_status_change      when the status last changed
    total_frames            number of frames in the video
    percent_labeled_frames  percentage of frames that got labels
    error_message           last error message (empty when there is none)
"""

import json
import os
from datetime import datetime

from logging_config import get_logger

try:
    # single source of truth for the version number
    from __init__ import __version__ as SLEAPYTRACKS_VERSION
except Exception:
    SLEAPYTRACKS_VERSION = "unknown"

logger = get_logger(__name__)

# possible processing statuses
STATUS_UNPROCESSED = "Unprocessed"
STATUS_FINISHED = "finished"
STATUS_ERROR = "error"

LOG_FILE_NAME = "SLEAPyTracks_processing_log.json"


def _now():
    """Return the current time as an ISO formatted string."""
    return datetime.now().isoformat()


def find_log_dir(video_dir):
    """
    Find the directory the run level files belong in.

    The processing log itself is written here, the run log goes in a "logs"
    subfolder of it.

    Walks up from video_dir and returns the first directory that already
    contains a processing log. This way one log per year folder covers every
    video beneath it, no matter which subfolder SLEAPyTracks is pointed at.
    Falls back to video_dir when no log is found higher up.

    This runs before logging is set up, so it does not log itself. It returns
    notes for the caller to write to the log once logging is ready.

    :param video_dir: directory given on the command line
    :return: tuple of (log_dir, notes), notes is a list of (level, message)
    """
    notes = []
    start_dir = os.path.abspath(video_dir)

    current = start_dir
    while True:
        if os.path.isfile(os.path.join(current, LOG_FILE_NAME)):
            if os.access(current, os.W_OK):
                notes.append(("info", f"Using the processing log in: {current}"))
                return current, notes
            # log found but the drive is gone or read only
            notes.append((
                "warning",
                f"Found a processing log in {current} but it can not be written to. "
                f"Writing this run's files to {start_dir} instead."))
            notes.append(("info", f"Using the processing log in: {start_dir}"))
            return start_dir, notes

        parent = os.path.dirname(current)
        # stop at the root of the drive
        if parent == current:
            break
        current = parent

    notes.append((
        "info",
        f"No processing log found in {start_dir} or any folder above it. "
        f"Starting a new one in: {start_dir}"))
    return start_dir, notes


class ProcessingLog:
    """
    Reads, updates and writes SLEAPyTracks_processing_log.json in the log dir.
    """

    def __init__(self, log_dir):
        self.log_dir = log_dir
        self.log_path = os.path.join(log_dir, LOG_FILE_NAME)
        self.records = self._load()

    def _load(self):
        """Load an existing log file, or start with an empty log."""
        if os.path.isfile(self.log_path):
            try:
                with open(self.log_path, "r", encoding="utf-8") as log_file:
                    return json.load(log_file)
            except (json.JSONDecodeError, OSError) as error:
                logger.warning(
                    f"Could not read existing log {self.log_path}: {error}. "
                    "Starting a new log.")
        return {}

    def save(self):
        """Write the current log to disk as JSON."""
        try:
            with open(self.log_path, "w", encoding="utf-8") as log_file:
                json.dump(self.records, log_file, indent=2)
        except OSError as error:
            logger.error(f"Could not write processing log to {self.log_path}: {error}")

    def _key(self, video_path):
        """
        Return the key a video is stored under in the log.

        Kept in one place so the keying rule is defined once.

        :param video_path: full path to the video file
        :return: key string for self.records
        """
        return os.path.abspath(video_path)

    def _get_or_create(self, video_path):
        """Return the record for a video, creating it if it does not exist yet."""
        key = self._key(video_path)
        if key not in self.records:
            self.register_video(video_path)
        return self.records[key]

    def get_record(self, video_path):
        """
        Return the stored record for a video, or None when it is not in the log.

        Read only: nothing is created and nothing is written.

        :param video_path: full path to the video file
        :return: the record dict, or None
        """
        return self.records.get(self._key(video_path))

    def get_status(self, video_path):
        """
        Return the status recorded for a video.

        :param video_path: full path to the video file
        :return: "Unprocessed", "finished" or "error", or None when the video
                 is not in the log at all
        """
        record = self.get_record(video_path)
        if record is None:
            return None
        return record.get("status", STATUS_UNPROCESSED)

    def register_video(self, video_path):
        """
        Add a video to the log with status "Unprocessed" and fill first_seen.

        Called before processing. Videos already in the log are left untouched
        so their first_seen and history are kept.

        :param video_path: full path to the video file
        """
        key = self._key(video_path)
        if key in self.records:
            return

        now = _now()
        # take these from the key so they are always a full, normalised path,
        # also when SLEAPyTracks was given a relative directory
        self.records[key] = {
            "video_path": os.path.dirname(key),
            "video_name": os.path.basename(key),
            "status": STATUS_UNPROCESSED,
            "first_seen": now,
            "last_processed": None,
            "version_last_processed": None,
            "last_attempt": None,
            "last_status_change": now,
            "total_frames": None,
            "percent_labeled_frames": None,
            "error_message": "",
        }
        logger.debug(f"Registered new video in log: {os.path.basename(video_path)}")

    def _set_status(self, record, status):
        """Set a record's status and update last_status_change if it changed."""
        if record["status"] != status:
            record["last_status_change"] = _now()
        record["status"] = status

    def mark_finished(self, video_path, total_frames, percent_labeled_frames):
        """
        Mark a video as finished and store its frame statistics.

        :param video_path: full path to the video file
        :param total_frames: number of frames in the video
        :param percent_labeled_frames: percentage of frames that got labels
        """
        record = self._get_or_create(video_path)
        now = _now()
        self._set_status(record, STATUS_FINISHED)
        record["last_attempt"] = now
        record["last_processed"] = now
        record["version_last_processed"] = SLEAPYTRACKS_VERSION
        record["total_frames"] = total_frames
        record["percent_labeled_frames"] = percent_labeled_frames
        record["error_message"] = ""
        self.save()

    def mark_error(self, video_path, error_message):
        """
        Mark a video as errored and store the error message.

        :param video_path: full path to the video file
        :param error_message: description of what went wrong
        """
        record = self._get_or_create(video_path)
        now = _now()
        self._set_status(record, STATUS_ERROR)
        record["last_attempt"] = now
        record["error_message"] = str(error_message)
        self.save()
