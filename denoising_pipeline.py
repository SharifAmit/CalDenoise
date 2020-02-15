import numpy as np
from PIL import Image
from PIL import ImageEnhance
from PIL import ImageFilter
import matplotlib.pyplot as plt
from scipy import ndimage
import argparse
import time
import os

def sum1dsignal(img,img_name):
    np_img = np.asarray(img)
    np_sum = np.sum(np_img, axis=1)
    plt.plot(np_sum[:,0])
    filename = 'Outputs/sum_signal1d/'+img_name+'.png'
    plt.savefig(filename)
    return np_sum

def gaussain1d(sum1d,sigma,img_name):
    gauss_img = ndimage.filters.gaussian_filter1d(sum1d[:,0],sigma)
    plt.plot(gauss_img)
    filename = 'Outputs/gaussian_1d/'+img_name+'.png'
    plt.savefig(filename)
    return gauss_img

def gradient2ndOrder(gauss_img,img_name):
    grad_img = np.gradient(gauss_img,2)
    plt.plot(grad_img)
    filename = 'Outputs/gradient_2ndOrder/'+img_name+'.png'
    plt.savefig(filename)
    return grad_img

def zeroCrossing(grad_img,img_name):
    img_no_neg = np.where(grad_img!=0,grad_img,-500)
    img_no_neg2 = np.where(img_no_neg ==-500,img_no_neg, 0)
    plt.plot(img_no_neg2)
    filename = 'Outputs/zero_crossing/'+img_name+'.png'
    plt.savefig(filename)
    return img_no_neg2

def denoisedImage(img,img_name):
    np_img = np.asarray(img)
    y = np_img.shape[1]
    np_sum = np.sum(np_img, axis=1)
    np_img3 = np_sum[438:458,0]
    window=np_img3/y
    avg = np.average(window)                                                                                                                                                           
    im_np_subed = np_img - (avg -2)
    im_np_subed_good = np.where(im_np_subed>0,im_np_subed,0)
    im_np_img = Image.fromarray(im_np_subed_good.astype('uint8'))
    filename = 'Outputs/denoised_image/'+img_name+'.png'
    im_np_img.save(filename)
    return im_np_img

def enhanched(img,img_name):
    enhanced_img = ImageEnhance.Contrast(img).enhance(3)
    filename = 'Outputs/enhanced_image/'+img_name+'.png'
    enhanced_img.save(filename)
    return enhanced_img

def median_subtracting_img(img,img_name):
    median_img = img.filter(ImageFilter.MedianFilter(size=15))
    filename = 'Outputs/median_image/'+img_name+'.png'
    median_img.save(filename)

    np_median = np.asarray(median_img)
    xy = np.where(np_median[:,:,0]==0)

    np_enhance = np.array(img)
    e = np.array(xy)
    k = e.shape[1]

    for i in range(k):
        np_enhance[e[0,i],e[1,i],0] = 0
        np_enhance[e[0,i],e[1,i],1] = 0
        np_enhance[e[0,i],e[1,i],2] = 0
    enhanced_changed_img = Image.fromarray(np_enhance)
    filename_e = 'Outputs/enhanced_change_image/'+img_name+'.png'
    enhanced_changed_img.save(filename_e)
    return enhanced_changed_img

def median_image(img,img_name):
    median_img_l2 = img.filter(ImageFilter.MedianFilter(size=3))
    filename = 'Outputs/median_image2/'+img_name+'.png'
    median_img_l2.save(filename)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--dir', type=str, required=False, help='path/to/directory',default='Images')
    args = parser.parse_args()
    print(args.dir)
    for i in os.listdir(args.dir):
        
        img_name, _ = i.split('.')
        filepath = args.dir+'/'+i
        img = Image.open(filepath)
        np_sum = sum1dsignal(img,img_name)
        sigma = 30
        gauss_img = gaussain1d(np_sum,sigma,img_name)
        grad_img = gradient2ndOrder(gauss_img,img_name)
        img_no_neg2 = zeroCrossing(grad_img,img_name)
        im_np_img = denoisedImage(img,img_name)
        enhanced_img = enhanched(im_np_img,img_name)
        enhanced_changed_img = median_subtracting_img(enhanced_img,img_name)
        median_image(enhanced_changed_img,img_name)