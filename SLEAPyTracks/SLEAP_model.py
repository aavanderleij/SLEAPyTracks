#!/usr/bin/env python
"""
Uses a model that was trained with SLEAP and uses it to estimate key point positions
of the red knot in video's.

author: Antsje van der Leij

"""

import sys
import glob
from logging_config import get_logger

logger = get_logger(__name__)

# sleap-nn 0.3.0 replaced run_inference() with sleap_nn.inference.predict().
# run_inference() still works but is deprecated and will be removed, so use the
# new function when it is there. Older versions fall back to run_inference, which
# takes different argument names, so both are wrapped in run_prediction below.
try:
    from sleap_nn.inference import predict as _predict

    def run_prediction(video, model_paths, output_path):
        """
        Run the model on one video and save the predictions.

        :param video: path to the video file
        :param model_paths: list of paths to the trained model folders
        :param output_path: path to write the .slp file to
        :return: sleap_io Labels object with the predicted instances
        """
        # clean_empty_frames defaults to False in sleap-nn, which keeps a frame in
        # the slp file even when the model found nothing in it. run_inference used
        # to drop those, so keep dropping them to get the same slp file as before.
        return _predict(source=video, model_paths=model_paths,
                        output_path=output_path, clean_empty_frames=True)

except ImportError:
    from sleap_nn.predict import run_inference as _run_inference

    logger.warning(
        "You are using an old version of sleap-nn. SLEAPyTracks is tested with "
        "the newest SLEAP, please update it. See the installation instructions "
        "in the SLEAPyTracks README.")

    def run_prediction(video, model_paths, output_path):
        """
        Run the model on one video and save the predictions (old sleap-nn).

        :param video: path to the video file
        :param model_paths: list of paths to the trained model folders
        :param output_path: path to write the .slp file to
        :return: sleap_io Labels object with the predicted instances
        """
        return _run_inference(data_path=video, model_paths=model_paths,
                              make_labels=True, output_path=output_path)


class SLEAPModel:
    """
    A Class that predicts animal poses using a video as input.
    Returns a csv file with the pixel coordinates of key points found bij the model.
    Uses a model that is trained using the SLEAP GUI.
    """

    def __init__(self, video_file_path):
        # set class vars

        self.video_path = video_file_path
        # self.predictions_out_dir = os.path.join(predictions_out_dir, "predictions", "slp_files")


    def run_model(self, output_path, video=None):
        """
        Loads a pre-trained model from SLEAP.
        Runs the model on video to generate predictions.
        Predictions are then saved.
        :param video: video file name
        :return: SLEAP Labels object
        """

        if video is None:
            video = self.video_path

        logger.info(f"Loading pre-trained model and running inference on {video}")
        # Run inference
        labels = run_prediction(
            video=video,
            model_paths=glob.glob('model/*'),
            output_path=output_path)

        return labels

    def predict(self, video, slp_file_name):
        """
        Docstring for predict
        
        :param self: Description
        """
        if video is None:
            video = self.video_path

        labels = self.run_model(output_path=slp_file_name, video=video)

        logger.debug(f"Labels: {labels}")

        if not labels:
            logger.warning("No labels found!")
        else:
            logger.info(f"Successfully predicted labels from {video}")

def main():
    from logging_config import setup_logging
    setup_logging()
    logger.info("Starting SLEAP_model test")

if __name__ == "__main__":
    sys.exit(main())
