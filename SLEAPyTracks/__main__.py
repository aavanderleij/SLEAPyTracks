#!/usr/bin/env python

import argparse
import os
from logging_config import setup_logging, get_logger
from processing_log import find_log_dir

logger = None

parser = argparse.ArgumentParser(
    prog='SLEAPyTracks',
    description='A tracker for tracking exploration behavior. Trained for use on red knot exploration tests.')
parser.add_argument('video_dir', help='path to the directory containing the videos to be tracked',
                    type=str)
parser.add_argument("-f", "--re_index", action="store_true",
                    help="Attempt to re-index if videos can't be read. " \
                    "Will duplicate video videos that produce errors!")
parser.add_argument("-r", "--overwrite", action="store_true",
                    help="re-analyze videos and overwrite results if they exist.")
parser.add_argument("-t", "--render_tracks", action="store_true", help="Render video's with tracking overlay.")
parser.add_argument("--log_dir", type=str, default=None,
                    help="Directory to write the run log and the processing log to. "
                         "By default SLEAPyTracks looks for an existing processing log "
                         "in the video directory and the folders above it.")



if __name__ == "__main__":

    args = parser.parse_args()

    # work out where the run level files go before logging starts,
    # the run log goes there too
    if args.log_dir:
        log_dir = args.log_dir
        log_dir_notes = [("info", f"Using the log directory given with --log_dir: {log_dir}")]
    else:
        log_dir, log_dir_notes = find_log_dir(args.video_dir)

    # a new run log is made every run, keep them together in a logs subfolder
    # instead of letting them pile up next to the videos
    run_log_dir = os.path.join(log_dir, "logs")

    # Initialize logging
    logger = setup_logging(log_dir=run_log_dir)
    main_logger = get_logger(__name__)

    main_logger.info("Starting SLEAPyTracks...")
    main_logger.info(f"Writing the run log to: {run_log_dir}")

    # write the notes from find_log_dir now that logging is set up
    for level, message in log_dir_notes:
        getattr(main_logger, level)(message)

    from video_batch_perdictor import Predictor

    # fixing videos can lead to problems
    if args.re_index:
        main_logger.warning("The '--re_index' option is enabled.")

        print("The '--re_index' option is enabled.")

        print("This will leave the original videos as they are. "
        "However, if a videos produces an error, the video(s) "
        "will be copied and re-indexed. This can easily fill up your storage as every video "
        "will potentiality be duplicated! Please check your storage before proceeding.")
        print("Please check the SLEAPyTracks faq for more info.")
    
    if args.overwrite:
        main_logger.warning("The '--overwrite' option is enabled.")

    predictor = Predictor(args.video_dir, log_dir=log_dir, re_index=args.re_index,
                          render_tracks=args.render_tracks)
    predictor.predict(overwrite=args.overwrite)

    main_logger.info("All done!")
