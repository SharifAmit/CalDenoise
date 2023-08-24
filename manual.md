# Calcium denoise User Guide

This guide will help you install and run our application, Calcium denoise, on Windows, Ubuntu, Arch Linux, and Mac (Intel and M1/M2). Please follow the instructions carefully. 

## Prerequisites

The scripts for the installation process use Anaconda, a platform for managing packages in Python and R. You need to install it before proceeding. 

### Installation of Anaconda 

For detailed instructions, please visit the [official Anaconda documentation](https://docs.anaconda.com/anaconda/install/). 

## Installation of Research Thing

Once Anaconda is installed, you can use our provided scripts to install Research Thing. The script you use depends on your operating system. 

### Windows users

Run the following command:

```cmd
install_windows.bat
```

### Linux (GPU) users
Run the following command:
```bash
./install_gpu_linux.sh
```
### Special instructions for Linux users
Linux users need to execute a series of additional commands to ensure compatibility. Here are the commands:

```bash
sudo apt-get install libxcb-xinerama0
sudo apt-get install '^libxcb.*-dev' libx11-xcb-dev libglu1-mesa-dev libxrender-dev libxi-dev libxkbcommon-dev libxkbcommon-x11-dev
pip3 uninstall pyqt5 pyqt5-qt5 pyqt5-sip
conda install PyQt5-sip
pip install pyqt5 pyqt5-qt5
conda remove --force qt-main
pip uninstall opencv-python
pip install opencv-python-headless
export LD_LIBRARY_PATH="$LD_LIBRARY_PATH:$(dirname "$(readlink -f "$0")")/4conda/lib"
```
Users on other platforms can skip this step.

### Mac (Intel & M1/M2) users
Run the following command:
```bash
./install_m1m2.sh
```

### Running the Application
To run the application on macOS or linux, execute the following command:

```bash
./run_gpu_linux.sh
```
Windows users should run this command:
```bat
./run_windows.bat
```
Now, Calcium denoise should be up and running on your machine!