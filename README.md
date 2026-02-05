
# README SLEAPyTracks #
* Version 1.0.2


## What is this repository for? ##

This is a tracker for tracking exploration behavior of the red knot. Currently trained for use on red knot exploration tests.
Runs a trained SLEAP model over multiple videos and returns tracking data as CSV files.

With the update of SLEAP version 1.5.0, major changes were made to the framework.

Main functionality: 
* SLEAPyTracks will search input directory (and all subdirectories) for videos and analyze all found mp4 files.
* CSV files and SLP files are saved in the location of the video.
* Generates a montage to preview tracking results.
* Custom CVS output will contain the pixel coordinates and scores of every instance.

## Installation ##

I recommend reading the [installation documentation](https://nn.sleap.ai/latest/installation/) of SLEAP yourself but I will provide a step by step on how to get SLEAPyTracks running on a basic Windows computer without a Nvidia GPU.

SLEAPyTracks uses the SLEAP library. So first we install SLEAP using miniconda.

### Install Miniconda ###

Anaconda is a Python environment manager that makes it easy to install SLEAP and its necessary dependencies without affecting other Python software on your computer.

Miniconda is a lightweight version of Anaconda. To install it:

Go to: https://www.anaconda.com/docs/getting-started/miniconda/install#quickstart-install-instructions

Download the latest version for your OS.

Follow the installer instructions.



### Install SLEAP ###

Open "Anaconda Powershell Prompt" from the start menu.

Check if you have the latest version of conda.

If not, you can update conda by entering the following:

```bash
conda update --name base conda
```

First we install SLEAP.

Copy the following line in the Anaconda powershell and press enter:

```bash
conda create -n sleap python=3.13
```

Activate the environment:

```bash
conda activate sleap
```

Install SLEAP:

```bash
pip install "sleap[nn]" --extra-index-url https://download.pytorch.org/whl/cpu --index-url https://pypi.org/simple
```

Wait until the installation is finished.

Test the installation:

```bash
sleap-label --help
```


### Install SLEAPyTracks ###

Clone the SLEAPyTracks repo from GitHub.

In the Anaconda powershell:

```bash
git clone https://github.com/aavanderleij/SLEAPyTracks.git
```

To update SLEAPyTracks, you can run the following git command:

```bash
git pull
```

Remember to save any model files you want to keep somewhere else.

## Usage ##

With the Anaconda powershell start the sleap virtual environment.

```bash
conda activate sleap
```

Using the the Anaconda powershell go into the map for SLEAPyTracks (the location of this readme).

```bash
cd SLEAPyTracks
```
Run SLEAPyTracks on the directory you want to track.
SLEAPyTracks will look for and process **all mp4 video files** in this directory and its subdirectories.

```bash
python SLEAPyTracks "path/to/your/video_dir/location/"
```

The output can be found in the same directory as the video.

Files are saved as csv and .slp with the name of the video.


### More options: ###

Automatically fix video index errors. (with the new version this option might not be needed anymore but that needs more testing)

```bash
python SLEAPyTracks "path/to/your/video_dir/location/" -f
```

Re-analyze videos. By default SLEAPyTracks will skip videos that already have a slp file with the same name, only running the model on "new" videos

```bash
python SLEAPyTracks "path/to/your/video_dir/location/" -r
```

Create a separate videos with the tracks overlaid over the original video. These will be save in there own folder: "tracked_videos"

```bash
python SLEAPyTracks "path/to/your/video_dir/location/" -t
```

## FAQ ## 

#### When testing the installation of SLEAP I get errors.
* Remove the environment, update conda and reinstall. This is an known issue being worked on but a clean reinstall should fix most issus. Please contact me if the issue persists.

#### Videos take a long time to analyze. Can I make it go faster?
* Running it on a pc with a Nvidia GPU or a High Performance Cluster will greatly increase speed.

#### SLEAPyTracks skips some of my videos? It said there was an error?
* This is likely an index error while trying to read the video. Adding -f option will cause the program to copy and re-index you video's.

#### How do I check if my tracks are correct?
* SLEAPyTracks will generate an image containing 4 frames evenly spaced in the video with tracks overlaid. This way you can see if the subject was identified. You can also use the -t flag to generate videos overlaying the tracks so you can easily see how the model behaved. for a closer look you can view the SLP file by loading it into the SLEAP gui. You can activate sleap in the same env as SLEAPyTracks and typing "sleap-label". The application will start and in the upper left corner of the screen select "file" and then press "Open Project..." to select your slp file

#### I have empty CSV files....
* That means the model did not find any instances in the video.

#### But I know there is a bird there!
* If the current model does not work for your Red Knot exploration test, please contact me so I can add it as training data for the next model. If you are in a hurry, you can train your own model. Tutorials can be found [here](https://docs.sleap.ai/latest/tutorial/overview/).

#### SLEAPyTracks does not work...
* If you encounter any problems/bugs using this library, please let me know so I can fix/improve you experience.


## References ##

### SLEAP ###

SLEAP is the successor to the single-animal pose estimation software LEAP (Pereira et al., Nature Methods, 2019).

If you use SLEAP in your research, please cite:

T.D. Pereira, N. Tabris, A. Matsliah, D. M. Turner, J. Li, S. Ravindranath, E. S. Papadoyannis, E. Normand,
D. S. Deutsch, Z. Y. Wang, G. C. McKenzie-Smith, C. C. Mitelut, M. D. Castro, J. D’Uva, M. Kislin, D. H. Sanes,
S. D. Kocher, S. S-H, A. L. Falkner, J. W. Shaevitz, and M. Murthy. Sleap: A deep learning system for multi-animal pose
tracking. Nature Methods, 19(4), 2022

### Exploration in red knots ###

Ersoy, S. Exploration in red knots: The role of personality in the expression of individual behaviour across contexts,
PhD Thesis, University of Groningen, Groningen, The Netherlands.

### NIOZ ###

This repository is currently being developed and maintained for behavior research at NIOZ, the Royal Netherlands Institute for Sea Research.


## Contact ##

For questions or suggestions please email me at:
antsje.van.der.leij@nioz.nl

https://github.com/aavanderleij
