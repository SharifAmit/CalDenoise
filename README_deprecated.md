# Automated Denoising Software for Calcium Imaging Signals Using Deep Learning 

We developed CalDenoise, a software designed to automate the denoising of Ca<sup>2+</sup> Spatio-Temporal Maps (STMaps) to quantify cellular Ca<sup>2+</sup> patterns. The software comprises an image-processing-based pipeline and three generative-adversarial-network-based deep learning models capable of removing various types of noise patterns.

# Summary

Ca<sup>2+</sup> signaling is vital for cell survival and death, and Ca<sup>2+</sup> imaging is a common method to study and measure these cellular patterns. Nevertheless, noise from equipment and experimental protocols can hinder the accurate extraction of Ca<sup>2+</sup> signals from the resulting Spatio-Temporal Maps (STMaps). Current denoising methods for STMaps are often time-consuming and subjective. To address this issue, we've developed CalDenoise, an automated software that utilizes robust image processing and deep learning models to effectively eliminate noise, enhancing Ca<sup>2+</sup> signals in STMaps. The software offers four pipelines for noise removal, covering salt-and-pepper, impulsive, periodic noise, and background noise detection and subtraction. It incorporates three deep learning models capable of handling complex noise patterns and accurately distinguishing boundary noise. CalDenoise is adaptable to various cell types, reducing the potential for user errors through its automated denoising modules. The software also features adjustable parameters and a user-friendly graphical interface for ease of access and utilization.


# Highlights

•	CalDenoise: an automated Ca<sup>2+</sup> signals denoising software that effectively removes background image noise.

•	The software features one image-processing pipeline and three GAN models for removing noise from STMaps.

•	CalDenoise: effectively removes STMap noise such as salt-and-pepper, impulsive, and periodic noises.

•	The software enhances the extraction of key Ca<sup>2+</sup> event parameters effectively.

•	The denoising models minimize user error and offer multiple options for end-users to calibrate parameters, enabling efficient denoising of STMap datasets.

![graphical-caldenoise](https://github.com/SharifAmit/CalDenoise/assets/68434296/1fe5108d-7a83-4eb7-bf18-fd4ef434a764)


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
- Install Python (Linux/Ubuntu)

```
sudo apt-get install pip3 python3-dev
```


- Install packages from requirements.txt
```
sudo pip3 -r requirements.txt
```
## Cloning Repository and Defining Image directory

- Clone this repository using the following command in the terminal/command prompt.
```
git clone https://github.com/SharifAmit/CalciumDenoising.git
```
- Create a directory called "Images" inside the repository and put the ICC image files in the directory.
```
mkdir Images
```
## Run the following command in your Command prompt/Terminal

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
- For using sobel instead of Laplacian for gradient use the following flag.

```
   '--gradient_filter',type=str, required=False, help='Either Laplacian or Sobel', default='laplacian'
```
- For saving plots of intermediate operations use the following flag.
```
   '--plot_signals',type=bool, required=False, help='Plot the signals for sum,gaussian,gradient,zero_crossings', default=False
```
- For creating images for intermediate steps use the following flag.

```
   '--interm',type=bool, required=False, help='save intermediate images', default=False
```
- For saving both images with and without streaks of light use the following flag.

```
   '--median_w_SOL',type=bool, required=False, help='generate both SOL and without SOL images', default=False
```
