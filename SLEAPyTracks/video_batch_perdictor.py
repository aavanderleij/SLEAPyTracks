#!/usr/bin/env python
"""
This module looks in folders for video files and analyse them using sleap
"""

import os
import sys
import subprocess
from logging_config import get_logger
from SLEAP_model import SLEAPModel
from SLEAP_parser import SleapParser
from processing_log import ProcessingLog, STATUS_FINISHED

logger = get_logger(__name__)


class Predictor():

    def __init__(self, root_video_dir, log_dir=None, re_index=False, overwrite=False,
                 render_tracks=False):
        self.root_video_dir = root_video_dir
        # where the processing log lives, defaults to the video dir itself
        self.log_dir = log_dir if log_dir is not None else root_video_dir
        self.overwrite = overwrite
        self.re_index = re_index
        self.render_tracks = render_tracks

    def find_videos_in_sub_dir(self):
        """
        find videos in self.root_video_dir and return a list of all videos in self.root_video_dir
        :return: list of video file paths
        """
        # move to other class, model only needs to do one video per time
        # no more bulk

        video_files = []
        for root, dirs, files in os.walk(self.root_video_dir):
            # Skip the folders SLEAPyTracks made itself, those hold output
            if "fixed_videos" in root or "tracked_videos" in root:
                continue
            for file in files:
                if file.endswith((".mp4", ".MP4")):
                    video_files.append(os.path.join(root, file))

        logger.debug(f"Found {len(video_files)} video(s) in {self.root_video_dir}")
        return video_files

    def decide_work(self, video, slp_file_name, csv_file_name, processing_log, overwrite):
        """
        Decide what still has to be done for one video.

        The processing log is the source of truth for "was this video done
        before". The files on disk are only checked to notice a log that does
        not match reality.

        :param video: full path to the video file
        :param slp_file_name: path where the .slp file for this video is expected
        :param csv_file_name: path where the .csv file for this video is expected
        :param processing_log: ProcessingLog for this run
        :param overwrite: if True everything is done again
        :return: tuple of (run_prediction, run_parsing) booleans
        """
        video_name = os.path.basename(video)

        if overwrite:
            logger.debug(f"Overwrite is on, re-processing {video_name}")
            return True, True

        status = processing_log.get_status(video)

        if status is None:
            logger.debug(f"{video_name} is not in the processing log yet")
            return True, True

        if status != STATUS_FINISHED:
            logger.debug(f"Log status of {video_name} is '{status}', processing it")
            return True, True

        # the log says this video was finished in an earlier run
        if not os.path.isfile(slp_file_name):
            logger.warning(
                f"The processing log says {video_name} is finished, but its slp file "
                f"is missing: {slp_file_name}")
            logger.warning("Skipping this video. Use the -r option to track it again.")
            return False, False

        if not os.path.isfile(csv_file_name):
            logger.warning(
                f"The processing log says {video_name} is finished, but its csv file "
                f"is missing: {csv_file_name}")
            logger.info("Reading the existing slp file again to make the csv. "
                        "The model is not run again.")
            return False, True

        logger.info(f"Predictions for video {video_name} already exist "
                    f"(log status '{status}')")
        logger.info("Skipping this video")
        return False, False

    def process_video(self, video, processing_log, re_index, overwrite, render_tracks):
        """
        Run the model on one video and parse the results, as far as the
        processing log says is still needed.

        :param video: full path to the video file
        :param processing_log: ProcessingLog for this run
        :param re_index: if True try to fix videos that fail while indexing
        :param overwrite: if True redo work the log says is already done
        :param render_tracks: if True also render a video with the tracks overlaid
        """
        video_dir = os.path.dirname(video)
        video_name = os.path.basename(video)
        # remove extension
        save_name = os.path.splitext(video_name)[0]

        # Save .slp in the same folder as the video
        slp_file_name = os.path.join(video_dir, save_name + ".slp")
        # must match the csv path made by SleapParser.sleap_to_csv
        csv_file_name = os.path.join(video_dir, save_name + ".csv")

        run_prediction, run_parsing = self.decide_work(
            video, slp_file_name, csv_file_name, processing_log, overwrite)

        if not run_prediction and not run_parsing:
            return

        if run_prediction:
            logger.info(f"Output slp file: {slp_file_name}")
            logger.info(f"Running prediction for: {video_name}")

            # most common error is KeyError while indexing videos
            try:
                sleap_model = SLEAPModel(video_file_path=video)
                sleap_model.predict(video=None, slp_file_name=slp_file_name)
            # ffmpeg command is a quick fix for KeyError while indexing
            except KeyError:

                if re_index:
                    # Define the fixed_videos folder
                    fixed_videos_dir = os.path.join(video_dir, "fixed_videos")
                    os.makedirs(fixed_videos_dir, exist_ok=True)

                    logger.error(f"Error while indexing video: {video}")
                    logger.info("Attempting to fix it. please wait...")

                    # Construct the fixed video path
                    fixed_video_path = os.path.join(fixed_videos_dir, "fixed_" + video_name)

                    # Run ffmpeg to re-index and save the fixed video
                    subprocess.run(
                        ["ffmpeg", "-y", "-i", video,
                        "-c:v", "libx264", "-pix_fmt",
                        "yuv420p",
                        "-preset", "superfast", "-crf", "23", fixed_video_path])

                    try:
                        sleap_model = SLEAPModel(video_file_path=fixed_video_path)
                        sleap_model.predict(video=None, slp_file_name=slp_file_name)
                        logger.info(f"SLP file saved at {slp_file_name}")

                    except KeyError:
                        logger.error("Unable to fix video")
                        logger.info("Continuing with next video (if there are any)")
                        processing_log.mark_error(
                            video, "Unable to fix video (KeyError while indexing)")
                        return
                else:
                    logger.error(f"Error while indexing video: {video_name}")
                    logger.warning("Please check the SLEAP faq for more info.")
                    logger.info("Continuing with next video (if there are any)...")
                    processing_log.mark_error(video, "KeyError while indexing video")
                    return

            # any other error should not end the whole run
            except Exception as error:
                logger.error(f"Error while running the model on {video_name}: {error}")
                logger.info("Continuing with next video (if there are any)...")
                processing_log.mark_error(video, error)
                return

        if not os.path.isfile(slp_file_name):
            logger.error(f"No slp file was made for {video_name}")
            processing_log.mark_error(video, "No slp file was made")
            return

        if run_parsing:
            try:
                sleap_parser = SleapParser(slp_file=slp_file_name)
                total_frames, percent_labeled_frames = sleap_parser.sleap_to_csv(slp_file_name)
                sleap_parser.render_image(render_video=render_tracks)
                processing_log.mark_finished(video, total_frames, percent_labeled_frames)
            except Exception as error:
                logger.error(f"Error while parsing results for {video_name}: {error}")
                processing_log.mark_error(video, error)

    def predict(self, re_index=None, overwrite=None, render_tracks=None):
        """
        Predict pose labels for all videos in the root directory

        :param re_index: if True, attempt to fix corrupted video files using ffmpeg
        :param overwrite: if True, re-process videos the log says are finished
        :param render_tracks: if True, render videos with the tracks overlaid
        """
        if overwrite is None:
            overwrite = self.overwrite
        if re_index is None:
            re_index = self.re_index
        if render_tracks is None:
            render_tracks = self.render_tracks

        videos = self.find_videos_in_sub_dir()
        logger.info(f"Predicting on {len(videos)} video(s)")

        # register all found videos in the processing log (status "Unprocessed")
        # before doing any work, so first_seen is filled up front
        processing_log = ProcessingLog(self.log_dir)
        for video in videos:
            processing_log.register_video(video)
        processing_log.save()

        for i, video in enumerate(videos):
            self.process_video(video, processing_log, re_index, overwrite, render_tracks)
            logger.info(f"Done with {i + 1} of {len(videos)} video(s)")


def main():
    from logging_config import setup_logging
    setup_logging()
    logger.info("Starting video_batch_predictor test")

if __name__ == "__main__":
    sys.exit(main())
