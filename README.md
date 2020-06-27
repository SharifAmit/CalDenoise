# Denoising Images from Confocal Calcium Imaging
Denoising Images extracted using Calcium Imaging confocal microscopy. The images are of in-vitro interstitial cells of Cajal (ICC) collected from gastroenterological tracts of mice.
## Pre-requisite
- Ubuntu 18.04 / Windows 7 or later

## Installation Instruction for Ubuntu/Windows
- Install Pip3
```
https://pip.pypa.io/en/stable/installing/
```
- Install Python3 (Windows)
```
https://www.python.org/downloads/release/python-377/
```
- Install Python (Ubuntu)

```
sudo apt-get install pip3 python3-dev
```


- Install packages from requirements.txt
```
sudo pip3 -r requirements.txt
```
- Create a directory called "Images" and put the ICC image files in the directory.

### Run the following command in your Command prompt/Terminal

For ICC-MY we use the following command 

```
python3 denoising_pipeline.py --dir=Images --enhance=3 --large_median=15 --small_median=3
```

For ICC-IM we use the following command 

```
python3 denoising_pipeline.py --dir=Images --enhance=3 --large_median=3 --small_median=3 --SOL=True --threshold_SOL=65
```

- There are different flags to choose from. Not all of them are mandatory.

- For ICC-MY we use the following flags.

```
   '--enhance', type=int, default=3
   '--small_median', type=int, default=3
   '--large_median', type=int, default=15 
   '--dir', type=str, required=True, help='path/to/images'
```

- For ICC-IM we use the following flags. N.B. different image might require different threshold value for streak of light.

```
   '--enhance', type=int, default=3
   '--small_median', type=int, default=3
   '--large_median', type=int, default=3 
   '--dir', type=str, required=True, help='path/to/images'
   '--threshold_SOL', type=int, default=65
   '--SOL', type=bool, required=False, default=False
```
