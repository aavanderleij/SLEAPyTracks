#!/usr/bin/env python
"""
Keeps a persistent JSON log of which videos SLEAPyTracks has seen and processed.

The log lives next to the videos (in the root video directory) as
``video_processing_log.json``. Videos are registered with status "Unprocessed"
as soon as they are found, before any prediction runs, and updated to "finished"
or "error" afterwards.

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


class ProcessingLog:
    """
    Reads, updates and writes video_processing_log.json in the root video dir.
    """

    def __init__(self, root_video_dir):
        self.root_video_dir = root_video_dir
        self.log_path = os.path.join(root_video_dir, LOG_FILE_NAME)
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

    def _get_or_create(self, video_path):
        """Return the record for a video, creating it if it does not exist yet."""
        key = os.path.abspath(video_path)
        if key not in self.records:
            self.register_video(video_path)
        return self.records[key]

    def register_video(self, video_path):
        """
        Add a video to the log with status "Unprocessed" and fill first_seen.

        Called before processing. Videos already in the log are left untouched
        so their first_seen and history are kept.

        :param video_path: full path to the video file
        """
        key = os.path.abspath(video_path)
        if key in self.records:
            return

        now = _now()
        self.records[key] = {
            "video_path": os.path.dirname(video_path),
            "video_name": os.path.basename(video_path),
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
