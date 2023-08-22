'''  
Copyright (c) 2017 Intel Corporation.
Licensed under the MIT license. See LICENSE file in the project root for full license information.
'''

import cv2
import numpy as np
import time
import argparse

def avg_circles(circles, b):
    avg_x=0
    avg_y=0
    avg_r=0
    for i in range(b):
        #optional - average for multiple circles (can happen when a gauge is at a slight angle)
        avg_x = avg_x + circles[0][i][0]
        avg_y = avg_y + circles[0][i][1]
        avg_r = avg_r + circles[0][i][2]
    avg_x = int(avg_x/(b))
    avg_y = int(avg_y/(b))
    avg_r = int(avg_r/(b))
    return avg_x, avg_y, avg_r

def dist_2_pts(x1, y1, x2, y2):
    #print np.sqrt((x2-x1)^2+(y2-y1)^2)
    return np.sqrt((x2 - x1)**2 + (y2 - y1)**2)

def calibrate_gauge(img):
    '''
        This function should be run using a test image in order to calibrate the range available to the dial as well as the
        units.  It works by first finding the center point and radius of the gauge.  Then it draws lines at hard coded intervals
        (separation) in degrees.  It then prompts the user to enter position in degrees of the lowest possible value of the gauge,
        as well as the starting value (which is probably zero in most cases but it won't assume that).  It will then ask for the
        position in degrees of the largest possible value of the gauge. Finally, it will ask for the units.  This assumes that
        the gauge is linear (as most probably are).
        It will return the min value with angle in degrees (as a tuple), the max value with angle in degrees (as a tuple),
        and the units (as a string).
    '''
    
    height, width = img.shape[:2]

    #convert gray
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  

    #detect circles
    #restricting the search from 35-48% of the possible radii gives fairly good results across different samples. 
    #Remember that these are pixel values which correspond to the possible radii search range.
    circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT_ALT, 1, 20, np.array([]), 100, 0.8, int(height*0.35), int(height*0.48))
    # average found circles, found it to be more accurate than trying to tune HoughCircles parameters to get just the right one
    a, b, c = circles.shape
    x,y,r = avg_circles(circles, b)

    #draw center and circle
    cv2.circle(img, (x, y), r, (0, 0, 255), 3, cv2.LINE_AA)  # draw circle
    cv2.circle(img, (x, y), 2, (0, 255, 0), 3, cv2.LINE_AA)  # draw center of circle

    #draw calibration
    #for calibration, plot lines from center going out at every 10 degrees and add marker
    #for i from 0 to 36 (every 10 deg)
    '''
    goes through the motion of a circle and sets x and y values based on the set separation spacing.  Also adds text to each
    line.  These lines and text labels serve as the reference point for the user to enter
    NOTE: by default this approach sets 0/360 to be the +x axis (if the image has a cartesian grid in the middle), the addition
    (i+9) in the text offset rotates the labels by 90 degrees so 0/360 is at the bottom (-y in cartesian).  So this assumes the
    gauge is aligned in the image, but it can be adjusted by changing the value of 9 to something else.
    '''
    separation = 10.0 #in degrees
    interval = int(360 / separation)
    p1 = np.zeros((interval,2))  #set empty arrays
    p2 = np.zeros((interval,2))
    p_text = np.zeros((interval,2))
    for i in range(0,interval):
        for j in range(0,2):
            if (j%2==0):
                p1[i][j] = x + 0.9 * r * np.cos(separation * i * 3.14 / 180) #point for lines
            else:
                p1[i][j] = y + 0.9 * r * np.sin(separation * i * 3.14 / 180)
    text_offset_x = 10
    text_offset_y = 5
    for i in range(0, interval):
        for j in range(0, 2):
            if (j % 2 == 0):
                p2[i][j] = x + r * np.cos(separation * i * 3.14 / 180)
                p_text[i][j] = x - text_offset_x + 1.2 * r * np.cos((separation) * (i+9) * 3.14 / 180) #point for text labels, i+9 rotates the labels by 90 degrees
            else:
                p2[i][j] = y + r * np.sin(separation * i * 3.14 / 180)
                p_text[i][j] = y + text_offset_y + 1.2* r * np.sin((separation) * (i+9) * 3.14 / 180)  # point for text labels, i+9 rotates the labels by 90 degrees

    #add the lines and labels to the image
    for i in range(0,interval):
        cv2.line(img, (int(p1[i][0]), int(p1[i][1])), (int(p2[i][0]), int(p2[i][1])),(0, 255, 0), 2)
        cv2.putText(img, '%s' %(int(i*separation)), (int(p_text[i][0]), int(p_text[i][1])), cv2.FONT_HERSHEY_SIMPLEX, 0.3,(0,0,0),1,cv2.LINE_AA)

    success, encoded_img = cv2.imencode('.jpg', img)
    if success:
        cal_img_bytes = encoded_img.tobytes()

    return x, y, r, cal_img_bytes

def get_current_value(img, min_angle, max_angle, min_value, max_value, x, y, r):
    
    gray2 = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    thresh_arr = np.arange(0, 260, 5)
    maxValue = 255
   
    #adjust the threshold for line detection
    for thresh in thresh_arr:
        th, dst2 = cv2.threshold(gray2, thresh, maxValue, cv2.THRESH_BINARY_INV)
        minLineLength = 0.4 * r
        maxLineGap = 0
        lines = cv2.HoughLinesP(image=dst2, rho=3, theta=np.pi / 180, threshold=100,minLineLength=minLineLength, maxLineGap=0)  # rho is set to 3 to detect more lines, easier to get more then filter them out later
        
        if lines is not None:
            final_line_list = []
            diff1LowerBound = 0.15 #diff1LowerBound and diff1UpperBound determine how close the line should be from the center
            diff1UpperBound = 0.25
            diff2LowerBound = 0.5 #diff2LowerBound and diff2UpperBound determine how close the other point of the line should be to the outside of the gauge
            diff2UpperBound = 1.0

            for i in range(0, len(lines)):
                for x1, y1, x2, y2 in lines[i]:
                    diff1 = dist_2_pts(x, y, x1, y1)  # x, y is center of circle
                    diff2 = dist_2_pts(x, y, x2, y2)  # x, y is center of circle
                    #set diff1 to be the smaller (closest to the center) of the two), makes the math easier
                    if (diff1 > diff2):
                        temp = diff1
                        diff1 = diff2
                        diff2 = temp
                    # check if line is within an acceptable range
                    if (((diff1<diff1UpperBound*r) and (diff1>diff1LowerBound*r) and (diff2<diff2UpperBound*r)) and (diff2>diff2LowerBound*r)):
                        line_length = dist_2_pts(x1, y1, x2, y2)
                        # add to final list
                        final_line_list.append([x1, y1, x2, y2])
    
            if len(final_line_list) > 0:
                #assume the first detected line is the best
                x1 = final_line_list[0][0]
                y1 = final_line_list[0][1]
                x2 = final_line_list[0][2]
                y2 = final_line_list[0][3]
                cv2.line(img, (x1, y1), (x2, y2), (0, 255, 0), 2)

                #find the end vector by the end point of the line
                dist_pt_0 = dist_2_pts(x, y, x1, y1)
                dist_pt_1 = dist_2_pts(x, y, x2, y2)
                if dist_pt_0 > dist_pt_1:
                    end_vector = [x1 - x, y1 - y]
                else:
                    end_vector = [x2 - x, y2 - y]

                #find the start vector by the min angle and 0 degree vector
                base_x = x + r * np.cos(0.5 * 3.14)
                base_y = y + r * np.sin(0.5 * 3.14)
                base_vector = [r * np.cos(0.5 * 3.14), r * np.sin(0.5 * 3.14)]
                
                angle_radians = np.radians(min_angle)
                rotation_matrix = np.array([[np.cos(angle_radians), -np.sin(angle_radians)],
                                            [np.sin(angle_radians), np.cos(angle_radians)]])
                start_vector = np.dot(rotation_matrix, base_vector)

                #calculate the degree within start vector and end vector
                norm_start_vector = np.linalg.norm(start_vector)
                norm_end_vector = np.linalg.norm(end_vector)
                cos_theta = np.dot(start_vector, end_vector) / (norm_start_vector * norm_end_vector)
                angle_rad = np.arccos(np.clip(cos_theta, -1.0, 1.0))
                process_angle = np.degrees(angle_rad)
                
                value = process_angle / (max_angle - min_angle) * (max_value - min_value) + min_value
                return value