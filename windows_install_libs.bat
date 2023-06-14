call conda create -y --prefix ./4conda python=3.7
call conda install -p ./4conda -y tensorflow-gpu=2.0.0
call conda activate ./4conda
call pip install tensorflow-estimator==2.0.0
call conda install -p ./4conda -y keras=2.3.1
call pip install pillow== 9.0.1
call pip install numpy==1.22.4
call pip install scipy==1.8.1
call pip install opencv-python
call pip uninstall -y scikit-learn
call pip install scikit-learn==0.20.4
call pip install matplotlib==3.5.3
call pip install h5py==2.10.0 --force-reinstall
call pip install matplotlib==3.5.3
call pip install Pillow==9.0.1
call pip install PyQt5==5.15.6
call pip install PyQt5-Qt5==5.15.2
call pip install PyQt5-sip==12.10.1
PAUSE









