'''
python3 predict.py \
    --model_path = "C:/Users/ZZ01OE858/Documents/digit reader/source/weights/best.pt" \
    --img_path = "C:/Users/ZZ01OE858/Documents/digit reader/data/images/test/3.jpeg"
'''

from ultralytics import YOLO
import cv2
import numpy as np
import argparse

def main(args):

    #load model
    model = YOLO(args.model_path)

    #predict
    results = model.predict(args.img_path)
    
    # radius = 5
    # dot_color = (0, 0, 255)
    img = cv2.imread(args.img_path)

    #read out the results
    for result in results:
        boxes = result.boxes  # Boxes object for bbox outputs
        # masks = result.masks  # Masks object for segmentation masks outputs
        # keypoints = result.keypoints  # Keypoints object for pose outputs
        # probs = result.probs  # Probs object for classification outputs
    
    #find the display index
    display_flg = False
    for id in range(len(boxes.data)):
        if boxes.data[id][5] == 0:
            display = boxes.data[id]
            display_flg = True
            break
    
    #read all the digits if it is in the display screen
    boxes_x_lst = []
    boxes_id_lst = []

    #if display screen detected then only add digits in the screen
    if display_flg == True:
        for id in range(len(boxes.data)):
            if boxes.data[id][5] != 0:
                if (boxes.data[id][0] >= display[0] and boxes.data[id][0] <= display[2] \
                and boxes.data[id][1] >= display[1] and boxes.data[id][1] <= display[3] \
                and boxes.data[id][4] > 0.5): #select digit probability larger than 0.5
                    # cv2.line(img, (int(boxes.data[id][0].item()), int(boxes.data[id][1].item())), (int(boxes.data[id][0].item()), int(boxes.data[id][3].item())), (0, 255, 0), 2)
                    # cv2.line(img, (int(boxes.data[id][2].item()), int(boxes.data[id][1].item())), (int(boxes.data[id][2].item()), int(boxes.data[id][3].item())), (0, 255, 0), 2)
                    # cv2.line(img, (int(boxes.data[id][0].item()), int(boxes.data[id][1].item())), (int(boxes.data[id][2].item()), int(boxes.data[id][1].item())), (0, 255, 0), 2)
                    # cv2.line(img, (int(boxes.data[id][0].item()), int(boxes.data[id][3].item())), (int(boxes.data[id][2].item()), int(boxes.data[id][3].item())), (0, 255, 0), 2)
                    boxes_x_lst.append(boxes.data[id][0].item())
                    if boxes.data[id][5].item() == 10.0:    #10.0 is the id of 0
                        boxes_id_lst.append(str(int(0)))
                    else:
                        boxes_id_lst.append(str(int(boxes.data[id][5].item())))
    else:
        for id in range(len(boxes.data)):
            if boxes.data[id][4] > 0.5: #select digit probability larger than 0.5
                # cv2.line(img, (int(boxes.data[id][0].item()), int(boxes.data[id][1].item())), (int(boxes.data[id][0].item()), int(boxes.data[id][3].item())), (0, 255, 0), 2)
                # cv2.line(img, (int(boxes.data[id][2].item()), int(boxes.data[id][1].item())), (int(boxes.data[id][2].item()), int(boxes.data[id][3].item())), (0, 255, 0), 2)
                # cv2.line(img, (int(boxes.data[id][0].item()), int(boxes.data[id][1].item())), (int(boxes.data[id][2].item()), int(boxes.data[id][1].item())), (0, 255, 0), 2)
                # cv2.line(img, (int(boxes.data[id][0].item()), int(boxes.data[id][3].item())), (int(boxes.data[id][2].item()), int(boxes.data[id][3].item())), (0, 255, 0), 2)
                boxes_x_lst.append(boxes.data[id][0].item())
                if boxes.data[id][5].item() == 10.0:    #10.0 is the id of 0
                    boxes_id_lst.append(str(int(0)))
                else:
                    boxes_id_lst.append(str(int(boxes.data[id][5].item())))
  
    #sort the digits by its x-axis value
    order = np.argsort(boxes_x_lst) 
    sorted_boxes_id_lst = [boxes_id_lst[i] for i in order]
    
    #check whether the img has decimal
    if args.decimal != 0:
        decimal_str = ''.join(sorted_boxes_id_lst[-args.decimal:])
        integer_str = ''.join(sorted_boxes_id_lst[:-args.decimal])
        result_str = integer_str + '.' + decimal_str
    else:
        result_str = ''.join(sorted_boxes_id_lst)
    
    cv2.imwrite('test.jpg', img)
    return result_str

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--model_path', default = 'C:/Users/ZZ01OE858/Documents/gauge_digit_reader/digit_reader/source/weights/best.pt', type = str)
    parser.add_argument('--img_path', default = "C:/Users/ZZ01OE858/Documents/gauge_digit_reader/digit_reader/data/images/test/8.jpg", type = str)
    parser.add_argument('--decimal', default = 0, type = int)
    args = parser.parse_args()
    result = main(args)
    print(result)