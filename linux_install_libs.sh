#!/bin/bash
conda create -y --prefix ./4conda python=3.7
conda install -p ./4conda -y tensorflow-gpu=2.0.0
conda activate ./4conda
pip install tensorflow-estimator==2.0.0
conda install -p ./4conda -y keras=2.3.1
pip install pillow== 9.0.1
pip install numpy==1.19.2
pip install scipy==1.6.2
pip uninstall -y scikit-learn
pip install scikit-learn==0.20.4
pip install matplotlib==3.5.3
pip install h5py==2.10.0 --force-reinstall
pip install matplotlib==3.5.3
pip install Pillow==9.0.1
pip install PyQt5==5.15.6
pip install PyQt5-Qt5==5.15.2
pip install PyQt5-sip==12.10.1
pip install opencv-python
pip install opencv-contrib-python