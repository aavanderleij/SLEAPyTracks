#!/usr/bin/env python


import argparse

parser = argparse.ArgumentParser(
    prog='SLEAPyTracks',
    description='A tracker for tracking exploration behavior. Currently trained for use on red knot exploration tests.',
    epilog='Still a work in progress!')
parser.add_argument('video_dir', help='path to the directory containing the videos to be tracked', type=str)
parser.add_argument('-o', '--output_dir', help='path to the directory to store the csv output files',
                    default='', type=str)
parser.add_argument('-n', '--number_of_animals', help='the maximum number of animals that are visible in one video',
                    type=int,
                    default=1)
parser.add_argument('-t', '--tracking', action='store_true', help='use tracking functionality (not trained properly '
                                                                  'yet!)')
parser.add_argument("-f", "--fix_videos", action="store_true", help="attempt to re-index if videos can't be"
                                                                    "read. Will duplicate video videos that produce "
                                                                    "errors!")

if __name__ == "__main__":
    args = parser.parse_args()
    print("Starting SLEAPyTracks...")

    from SLEAP_parser import SleapParser
    from SLEAP_model import SLEAPModel

    if args.fix_videos:
        print("Warning: The '--fix_videos' option is enabled.")
        print(
            "This will leave the original videos as they are. However, if a videos produces an error, the video(s) "
            "will be copied and re-indexed. This can easily fill up your storage as every video will potentiality be "
            "duplicated! Please check your storage before proceeding.")
        print("please check the SLEAP faq for more info.")
        confirm = input("Do you want to continue? (y/n): ").strip().lower()
        if confirm not in ['yes', 'y']:
            print("Operation aborted by the user.")
            exit(0)

    if args.output_dir == '':
        model = SLEAPModel(args.video_dir, predictions_out_dir=args.video_dir)
        model.predict(args.number_of_animals, args.tracking, args.fix_videos)
        SleapParser().get_results(args.video_dir)
    else:
        model = SLEAPModel(args.video_dir, predictions_out_dir=args.output_dir)
        model.predict(args.number_of_animals, args.tracking, args.fix_videos)
        SleapParser().get_results(args.output_dir)

    print('all done!')
