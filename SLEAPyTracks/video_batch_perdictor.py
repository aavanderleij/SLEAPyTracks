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

logger = get_logger(__name__)


class Predictor():

    def __init__(self, root_video_dir, re_index=False, overwrite=False, render_tracks=False):
        self.root_video_dir = root_video_dir
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
            # Skip 'fixed_videos' directories
            if "fixed_videos" in root:
                continue
            for file in files:
                if file.endswith((".mp4", "MP4")):
                    video_files.append(os.path.join(root, file))

        logger.debug(f"Found {len(video_files)} video(s) in {self.root_video_dir}")
        return video_files

    def predict(self, re_index=None, overwrite=None, render_tracks=None):
        """
        Predict pose labels for all videos in the root directory
        
        :param fix_videos: if True, attempt to fix corrupted video files using ffmpeg
        :param overwrite: if True, re-predict even if .slp file already exists
        """
        if overwrite is None:
            overwrite = self.overwrite
        if re_index is None:
            re_index = self.re_index
        if render_tracks is None:
            render_tracks = self.render_tracks

        videos = self.find_videos_in_sub_dir()
        logger.info(f"Predicting on {len(videos)} video(s)")

        for i, video in enumerate(videos):

            # get video names
            video_dir = os.path.dirname(video)
            video_name = os.path.basename(video)
            # remove extension
            save_name = os.path.splitext(video_name)[0]

            # Save .slp in the same folder as the video
            slp_file_name = os.path.join(video_dir, save_name + ".slp")
            logger.info(f"Output slp file: {slp_file_name}")


            if os.path.isfile(slp_file_name) and not overwrite:
                logger.info(f"Predictions for video {video_name} already exist")
                logger.info("Skipping prediction for this video")
            else:

                logger.info(f"Running prediction for: {video_name}")

                # most common error is KeyError while indexing videos
                try:
                    sleap_model = SLEAPModel(video_file_path=video)
                    labels = sleap_model.predict(video=None, slp_file_name=slp_file_name)
                # ffmpeg command is a quick fix for KeyError while indexing
                except KeyError:

                    if re_index:
                        # Define the fixed_videos folder
                        fixed_videos_dir = os.path.join(video_dir, "fixed_videos")
                        os.makedirs(fixed_videos_dir, exist_ok=True)

                        logger.error(f"Error while indexing video: {video}")
                        logger.info("Attempting to fix it. please wait...")

                        # Extract just the filename of the video
                        video_name = os.path.basename(video)

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
                            labels = sleap_model.predict(video=None, slp_file_name=slp_file_name)
                            logger.info(f"SLP file saved at {slp_file_name}")

                        except KeyError:
                            logger.error("Unable to fix video")
                            logger.info("Continuing with next video (if there are any)")
                            continue
                    else:
                        logger.error(f"Error while indexing video: {video_name}")
                        logger.warning("Please check the SLEAP faq for more info.")
                        logger.info("Continuing with next video (if there are any)...")
                        continue

            if os.path.isfile(slp_file_name):
                # TODO discuss if this is how we want it
                sleap_parser = SleapParser(slp_file=slp_file_name)
                sleap_parser.sleap_to_csv(slp_file_name)
                sleap_parser.render_image(render_video=self.render_tracks)

            logger.info(f"Done with {i + 1} of {len(videos)} video(s)")


def main():
    from logging_config import setup_logging
    setup_logging()
    logger.info("Starting video_batch_predictor test")



if __name__ == "__main__":
    sys.exit(main())
