#!/usr/bin/env python

import argparse
from logging_config import setup_logging, get_logger

logger = None

parser = argparse.ArgumentParser(
    prog='SLEAPyTracks',
    description='A tracker for tracking exploration behavior. Trained for use on red knot exploration tests.')
parser.add_argument('video_dir', help='path to the directory containing the videos to be tracked',
                    type=str)
parser.add_argument("-f", "--fix_videos", action="store_true",
                    help="Attempt to re-index if videos can't be read. " \
                    "Will duplicate video videos that produce errors!")
parser.add_argument("-r", "--overwrite", action="store_true",
                    help="re-analyze videos and overwrite results if they exist.")

if __name__ == "__main__":

    args = parser.parse_args()
    # Initialize logging
    logger = setup_logging(log_dir=args.video_dir)
    main_logger = get_logger(__name__)
    

    main_logger.info("Starting SLEAPyTracks...")

    from video_batch_perdictor import Predictor

    # fixing videos can lead to problems
    if args.fix_videos:
        main_logger.warning("The '--fix_videos' option is enabled.")

        print("The '--fix_videos' option is enabled.")

        print("This will leave the original videos as they are. "
        "However, if a videos produces an error, the video(s) "
        "will be copied and re-indexed. This can easily fill up your storage as every video "
        "will potentiality be duplicated! Please check your storage before proceeding.")
        print("Please check the SLEAPyTracks faq for more info.")
    
    if args.overwrite:
        main_logger.warning("The '--overwrite' option is enabled.")

    predictor = Predictor(args.video_dir)
    labels = predictor.predict(fix_videos=args.fix_videos, overwrite=args.overwrite)

    main_logger.info("All done!")
