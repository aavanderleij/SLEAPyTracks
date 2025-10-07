
# README SLEAPyTracks #
* Version 0.2.2


## What is this repository for? ##

This is a tracker for tracking exploration behavior of the red knot. Currently trained for use on red knot exploration tests.
Runs a trained SLEAP model over multiple videos and returns tracking data as a csv file.

With the update of SLEAP version 1.3.3, SLEAP also added the option to save in CSV but this wrapper adds minor quality of live changes.

The main differences are: 
* SLEAPyTracks will search input directory (and all subdirectories) for videos and analyze all found mp4 files.
* Custom CVS output.

## Installation ##

SLEAPyTracks uses the SLEAP library. So first we install SLEAP using miniconda.

The following instructions are for Windows.

### Install Miniconda ###

Anaconda is a Python environment manager that makes it easy to install SLEAP and its necessary dependencies without affecting other Python software on your computer.

Miniconda is a lightweight version of Anaconda. To install it:

Go to: https://docs.conda.io/en/latest/miniconda.html#latest-miniconda-installer-links

Download the latest version for your OS.

Follow the installer instructions.



### Install SLEAP ###

open "Anaconda Powershell Prompt" from the start menu.

First we install SLEAP.

Copy the following line in the Anaconda powershell and press enter:

```bash
conda create -y -n sleap -c sleap -c nvidia -c conda-forge sleap=1.3.0
```

Wait until the installation is finished.

After installing SLEAP install ffmpeg by coping the following line into the shell and pressing enter:

```bash
conda install -n sleap ffmpeg
```


If you don't have git installed already, you can also install it with Miniconda:

```bash
conda install git
```


### Install SLEAPyTracks ###

Clone the SLEAPyTracks repo from GitHub.

in the Anaconda powershell:

```bash
git clone https://github.com/aavanderleij/SLEAPyTracks.git
```

To update SLEAPyTracks, you can run the following git command:

```bash
git pull
```

Remember to save any tracking files you want to keep somewhere else.

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


### more options: ###

Automatically fix video index errors.

```bash
python SLEAPyTracks "path/to/your/video_dir/location/" -f
```

direct output to different directory

```bash
python SLEAPyTracks "path/to/your/video_dir/location/" -o "path/to/output"
```


track more than one animal in a video (e.g 3 animals):

```bash
python SLEAPyTracks "path/to/your/video_dir/location/" -t -n 3
```

## FAQ ## 

#### Videos take a long time to analyze. Can I make it go faster?
* Running it on a pc with a Nvidia GPU or a High Preformance Culster will greatly increase speed.

#### SLEAPyTracks skips some of my videos? It said there was an error?
* This is likely an index error while trying to read the video. Adding -f option will cause the program to copy and re-index you video's.
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
