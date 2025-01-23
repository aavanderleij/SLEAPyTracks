#!/usr/bin/env python
"""
Uses a model that was trained with SLEAP and uses it to estimate keypoint positions of the red knot in video's.

autor: Antsje van der Leij

"""

import sys
import os
import logging
import glob
import subprocess
import sleap


class SLEAPModel:
    """
    A Class that predicts animal poses using a video as input.
    Returns a csv file with the pixel coordinates of key points found bij the model.
    Uses a model that is trained using the SLEAP GUI.
    """

    def __init__(self, video_dir, predictions_out_dir):

        self.video_dir = video_dir
        self.model = self.load_model()
        self.predictions_out_dir = os.path.join(predictions_out_dir, "predictions", "slp_files")

    def get_files_from_dir(self, path, file_extension):
        """
        gets files names ending with the file exetntion from target directory and returns those files as a list
        :param path: absolute path to target directory
        :param file_extension: the extension of retrieved files
        :return: list with files ending with the file_extension
        """

        # check if file exists
        if not os.path.isdir(path):
            sys.exit("File path to videos does not exist or is incorrect!")

        # get only one type of file
        files = [f for f in os.listdir(path) if f.endswith(file_extension) or f.endswith(file_extension.upper())]

        # check if any files match file type
        if not files:
            sys.exit("no " + file_extension + " found in " + path)

        return files

    def find_videos_in_sub_dir(self):
        """
        find videos in self.video_dir and return a list of all videos in self.video_dir
        :return:
        """
        video_files = []
        for root, dirs, files in os.walk(self.video_dir):
            for file in files:
                if file.endswith((".mp4", "MP4")):
                    video_files.append(os.path.join(root, file))

        return video_files

    def load_video(self, path_to_video):
        """
        Loads a mp4 video as SLEAP video object
        :param path_to_video:
        :return: SLEAP video object
        """
        print("load video")

        loaded_video = sleap.load_video(path_to_video)
        return loaded_video

    def load_model(self):
        """
        loads a trained SLEAP model directory model
        """
        print("load model")

        # use glob to make a variable model path so name of model doesn't matter
        model_path = glob.glob('model/*')

        model = sleap.load_model(model_path)

        return model

    def run_tracker(self, labels, instance_count):

        """
        initialises SLEAP tracker
        :param labels: SLEAP Labels object
        :param instance_count: int
        :return: SLEAP Labels object
        """

        print(labels)
        print("initializing tracker")

        # Here I'm removing the tracks, so we just have instances without any tracking applied.
        for instance in labels.instances():
            instance.track = None
        labels.tracks = []

        # Create tracker
        tracker = sleap.nn.tracking.Tracker.make_tracker_by_name(
            # General tracking options
            tracker="flow",
            track_window=5,

            # Matching options
            similarity="instance",
            match="greedy",
            min_new_track_points=1,
            min_match_points=1,

            # Optical flow options (only applies to "flow" tracker)
            img_scale=0.5,
            of_window_size=21,
            of_max_levels=3,

            # Pre-tracking filtering options
            target_instance_count=instance_count,
            pre_cull_to_target=True,
            pre_cull_iou_threshold=0.8,

            # Post-tracking filtering options
            post_connect_single_breaks=True,
            clean_instance_count=instance_count,
            clean_iou_threshold=None,
        )

        tracked_lfs = []
        for lf in labels:
            lf.instances = tracker.track(lf.instances, img=lf.image)
            tracked_lfs.append(lf)
            print(lf)

        tracked_labels = sleap.Labels(tracked_lfs)

        return tracked_labels

    def run_model(self, video):
        """
        Loads a pre-trained model from SLEAP.
        Runs the model on video to generate predictions.
        Predictions are then saved.
        :param video: video file name
        :return: SLEAP Labels object
        """

        print(f'running model on {video}')

        # run model

        labels = self.model.predict(video)
        labels = sleap.Labels(labels.labeled_frames)

        return labels

    def predict(self, instance_count, tracking, fix_videos):
        """
        run model over every video in target directory and actives tracking if tracking is True
        :param instance_count: (int) amount of expected animals in videos
        :param tracking: (boolean) activate tracking if True
        :param fix_videos: (boolean) fix idex erros

        """

        videos = self.find_videos_in_sub_dir()
        print(f"predicting on {len(videos)} videos")
        for i, video in enumerate(videos):

            # get video names
            video_name = os.path.basename(video)
            save_name = os.path.splitext(video_name)[0]

            # file path to save sleap predictions
            slp_file = os.path.join(self.predictions_out_dir, save_name + ".slp")

            if os.path.isfile(slp_file):
                print(f"predictions for video {video_name} already exist")
                print("skipping prediction for this video")
                continue

            print("run prediction for:")
            print(video_name)
            # use video name as name for predictions save file
            sleap_video = self.load_video(video)

            # make directory for sleap predictions one doesn't exist
            if not os.path.isdir(self.predictions_out_dir):
                os.makedirs(self.predictions_out_dir)
                logging.debug("made a new directory for sleap predictions")

            # most common error is KeyError while indexing videos
            try:
                labels = self.run_model(sleap_video)
                labels.save(slp_file)
                logging.info(f"slp file at {slp_file}")
            # ffmpeg command is a quick fix for KeyError while indexing
            except KeyError:

                if fix_videos:
                    # Define the fixed_videos folder
                    fixed_videos_dir = os.path.join(self.video_dir, "fixed_videos")
                    os.makedirs(fixed_videos_dir, exist_ok=True)

                    print("ran into error while indexing video: " + video)
                    print("Attempting to fix it. please wait...")

                    # Extract just the filename of the video
                    video_name = os.path.basename(video)

                    # Construct the fixed video path
                    fixed_video_path = os.path.join(fixed_videos_dir, "fixed_" + video_name)

                    # Run ffmpeg to re-index and save the fixed video
                    subprocess.run(
                        ["ffmpeg", "-y", "-i", os.path.join(self.video_dir, video), "-c:v", "libx264", "-pix_fmt",
                         "yuv420p",
                         "-preset", "superfast", "-crf", "23", fixed_video_path]
                    )

                    try:
                        sleap_video = self.load_video(fixed_video_path)
                        labels = self.run_model(sleap_video)
                        labels.save(slp_file)
                        logging.info(f"slp file at {slp_file}")

                    except KeyError:
                        print("unable to fix video")
                        print("continue with next video (if there are any)")
                        continue
                else:
                    print("ran into error while indexing video: " + video_name)
                    print("please check the SLEAP faq for more info.")
                    print("continue with next video (if there are any)...")
                    continue

            # if tracking flag is set to True start tracking function
            if tracking:
                print("tracking...")
                print("this can take a few minutes")
                tracked_labels = self.run_tracker(labels, instance_count)
                print(tracked_labels)

                tracked_labels.save("predictions/tracks/" + save_name)

            print(f"done with {i + 1} of {len(videos)} videos")


def main():
    print("in main")

    model = SLEAPModel(args.video_dir)
    model.predict()


if __name__ == "__main__":
    sys.exit(main())
