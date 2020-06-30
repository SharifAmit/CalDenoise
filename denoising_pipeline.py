import numpy as np
from PIL import Image
from PIL import ImageEnhance
from PIL import ImageFilter
import matplotlib.pyplot as plt
from scipy import ndimage
import argparse
import time
import os
import warnings
warnings.filterwarnings("ignore")

def sum1dsignal(img,img_name,plot):
    np_img = np.asarray(img) 
    np_sum = np.sum(np_img, axis=1)
    if plot==True:
        plt.plot(np_sum[:,0])
        filename = 'Outputs/sum_signal1d/'+img_name+'.png'
        plt.savefig(filename)
        plt.close()
    return np_sum

def gaussain1d(sum1d,sigma,img_name,plot):
    gauss_img = ndimage.filters.gaussian_filter1d(sum1d[:,0],sigma)
    if plot==True:
        plt.plot(gauss_img)
        filename = 'Outputs/gaussian_1d/'+img_name+'.png'
        plt.savefig(filename)
        plt.close()
    return gauss_img

def gradient2ndOrder(gauss_img,img_name,filter,plot):
    if filter=='sobel':
        grad_img = ndimage.sobel(gauss_img,axis=0,mode='constant')
    elif filter=='laplacian':
        grad_img = np.gradient(gauss_img,2)
    if plot==True:
        plt.plot(grad_img)
        filename = 'Outputs/gradient_2ndOrder/'+img_name+'.png'
        plt.savefig(filename)
        plt.close()
    return grad_img

def zeroCrossing(grad_img,img_name,plot):
    #img_no_neg = np.where(grad_img!=0,grad_img,-500)
    #img_no_neg = np.where(img_no_neg<0.5,-500,0)
    min_beta= min(grad_img)
    min_beta = min_beta+0.5
    img_no_neg = np.where((grad_img<=min_beta) & (grad_img>=0),-500,0)
    if plot==True:
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
    return median_img_l2
def streak_of_light(median_img_l2,threshold,img_name):
    im = median_img_l2.point(lambda p: p > threshold and 255)  
    thres_im = np.array(im)
    main_im = np.array(median_img_l2)
    main_im[thres_im==0] = 0
    thres_out_img = Image.fromarray(main_im)
    thres_out_img.save('Outputs/streak_of_light/'+img_name+'.png')  

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--dir', type=str, required=True, help='path/to/directory',default='Images')
    parser.add_argument('--large_median',type=int, required=False, help='size of large median filter', default=15)
    parser.add_argument('--small_median',type=int, required=False, help='size of small median filter', default=3)
    parser.add_argument('--enhance',type=int, required=False, help='size of enhance filter', default=3)
    parser.add_argument('--SOL',type=bool, required=False, help='streak of light required', default=False)
    parser.add_argument('--threshold_SOL', type=int, required=False, help='threhsold for streak of light', default=65)
    parser.add_argument('--gradient_filter',type=str, required=False, help='Either Laplacian or Sobel', default='laplacian')
    parser.add_argument('--plot_signals',type=bool, required=False, help='Plot the signals for sum,gaussian,gradient,zero_crossings', default=False)

    args = parser.parse_args()
    start_time = time.time()
    dir_names = ['Outputs','Outputs/sum_signal1d','Outputs/gaussian_1d','Outputs/gradient_2ndOrder','Outputs/zero_crossing','Outputs/denoised_image','Outputs/enhanced_image','Outputs/median_image','Outputs/enhanced_change_image','Outputs/median_image2','Outputs/streak_of_light']
    for d in dir_names:
        if not os.path.exists(d):
            os.makedirs(d)
    for i in os.listdir(args.dir):
        img_name, _ = i.split('.')
        filepath = args.dir+'/'+i
        img = Image.open(filepath)
        np_sum = sum1dsignal(img,img_name,args.plot_signals)
        sigma = 30
        gauss_img = gaussain1d(np_sum,sigma,img_name,args.plot_signals)
        grad_img = gradient2ndOrder(gauss_img,img_name,args.gradient_filter,args.plot_signals)
        img_no_neg = zeroCrossing(grad_img,img_name,args.plot_signals)
        im_np_img = denoisedImage(img,img_no_neg,img_name)
        enhanced_img = enhanched(im_np_img,args.enhance,img_name)
        enhanced_changed_img = median_subtracting_img(enhanced_img,args.small_median,img_name)
        median_image_2 = median_image(enhanced_changed_img,args.large_median,img_name)
        if args.SOL==True:
            streak_of_light(median_image_2,args.threshold_SOL,img_name)

    end_time = time.time()
    print('Execution Time: ',(end_time-start_time)/(len(os.listdir(args.dir))))