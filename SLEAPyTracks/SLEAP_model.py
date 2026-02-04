#!/usr/bin/env python
"""
Uses a model that was trained with SLEAP and uses it to estimate key point positions
of the red knot in video's.

author: Antsje van der Leij

"""

import sys
import glob
from sleap_nn.predict import run_inference
from logging_config import get_logger

logger = get_logger(__name__)


class SLEAPModel:
    """
    A Class that predicts animal poses using a video as input.
    Returns a csv file with the pixel coordinates of key points found bij the model.
    Uses a model that is trained using the SLEAP GUI.
    """

    def __init__(self, video_file_path):
        # init
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
        labels = run_inference(
            data_path=video,
            model_paths=glob.glob('model/*'),
            make_labels=True,
            # frames=list(range(20,70,1)),
            return_confmaps=True,
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
