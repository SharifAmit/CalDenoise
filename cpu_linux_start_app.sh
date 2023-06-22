#!/bin/bash
conda activate ./4conda
export RUN_MODE=STUB
python ./src/cal_denoise_app.py
