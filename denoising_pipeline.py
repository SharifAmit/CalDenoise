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
    plt.close()
    return np_sum

def gaussain1d(sum1d,sigma,img_name):
    gauss_img = ndimage.filters.gaussian_filter1d(sum1d[:,0],sigma)
    plt.plot(gauss_img)
    filename = 'Outputs/gaussian_1d/'+img_name+'.png'
    plt.savefig(filename)
    plt.close()
    return gauss_img

def gradient2ndOrder(gauss_img,img_name):
    grad_img = np.gradient(gauss_img,2)
    plt.plot(grad_img)
    filename = 'Outputs/gradient_2ndOrder/'+img_name+'.png'
    plt.savefig(filename)
    plt.close()
    return grad_img

def zeroCrossing(grad_img,img_name):
    img_no_neg = np.where(grad_img!=0,grad_img,-500)
    #img_no_neg = np.where(grad_img==0,-500,0)
    img_no_neg = np.where(grad_img<0.5,-500,0)
    
    plt.plot(img_no_neg)
    filename = 'Outputs/zero_crossing/'+img_name+'.png'
    plt.savefig(filename)
    plt.close()
    return img_no_neg

def denoisedImage(img,img_no_neg,img_name):
    np_img = np.asarray(img)
    a = np.where(img_no_neg==-500)
    a = np.array(a)


    best_noise = a[:,0] 
    lower_bound = best_noise[0]-10
    upper_bound = best_noise[0]+10
    if lower_bound<0:
        lower_bound = 0
    if upper_bound>=np_img.shape[0]:
        upper_bound == np_img.shape[0]-1

    
    
    np_sum = np.sum(np_img, axis=1)
    np_img3 = np_sum[lower_bound:upper_bound,0]

    window= np_img3/np_img.shape[1]
    avg = np.average(window)                                                                                                                                                           
    im_np_subed = np_img - (avg -2)
    im_np_subed_good = np.where(im_np_subed>0,im_np_subed,0)
    im_np_img = Image.fromarray(im_np_subed_good.astype('uint8'))
    filename = 'Outputs/denoised_image/'+img_name+'.png'
    im_np_img.save(filename)
    return im_np_img

def enhanched(img,filter_size,img_name):
    enhanced_img = ImageEnhance.Contrast(img).enhance(filter_size)
    filename = 'Outputs/enhanced_image/'+img_name+'.png'
    enhanced_img.save(filename)
    return enhanced_img

def median_subtracting_img(img,filter_size,img_name):
    median_img = img.filter(ImageFilter.MedianFilter(size=filter_size))
    filename = 'Outputs/median_image/'+img_name+'.png'
    median_img.save(filename)

    np_median = np.asarray(median_img)
    xy = np.where(np_median[:,:,0]==0)

    np_enhance = np.array(img)
    e = np.array(xy)
    k = e.shape[1]

    if k==3:
        for i in range(k):
            np_enhance[e[0,i],e[1,i],0] = 0
            np_enhance[e[0,i],e[1,i],1] = 0
            np_enhance[e[0,i],e[1,i],2] = 0
    else:
        np_enhance[e[0,0],e[1,0],0] = 0

    enhanced_changed_img = Image.fromarray(np_enhance)
    filename_e = 'Outputs/enhanced_change_image/'+img_name+'.png'
    enhanced_changed_img.save(filename_e)
    return enhanced_changed_img

def median_image(img,filter_size,img_name):
    median_img_l2 = img.filter(ImageFilter.MedianFilter(size=filter_size))
    filename = 'Outputs/median_image2/'+img_name+'.png'
    median_img_l2.save(filename)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--dir', type=str, required=True, help='path/to/directory',default='Images')
    parser.add_argument('--large_median',type=int, required=False, help='size of large median filter', default=15)
    parser.add_argument('--small_median',type=int, required=False, help='size of small median filter', default=3)
    parser.add_argument('--enhance',type=int, required=False, help='size of enhance filter', default=3)

    args = parser.parse_args()
    #print(args.dir)
    
    dir_names = ['Outputs','Outputs/sum_signal1d','Outputs/gaussian_1d','Outputs/gradient_2ndOrder','Outputs/zero_crossing','Outputs/denoised_image','Outputs/enhanced_image','Outputs/median_image','Outputs/enhanced_change_image','Outputs/median_image2']
    for d in dir_names:
        if not os.path.exists(d):
            os.makedirs(d)
    #print(os.listdir(args.dir))
    for i in os.listdir(args.dir):
        
        
        img_name, _ = i.split('.')
        filepath = args.dir+'/'+i
        img = Image.open(filepath)
        np_sum = sum1dsignal(img,img_name)
        sigma = 30
        gauss_img = gaussain1d(np_sum,sigma,img_name)
        grad_img = gradient2ndOrder(gauss_img,img_name)
        img_no_neg = zeroCrossing(grad_img,img_name)
        im_np_img = denoisedImage(img,img_no_neg,img_name)
        enhanced_img = enhanched(im_np_img,args.enhance,img_name)
        enhanced_changed_img = median_subtracting_img(enhanced_img,args.small_median,img_name)
        median_image(enhanced_changed_img,args.large_median,img_name)