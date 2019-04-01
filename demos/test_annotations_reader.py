import os
import cv2
import json


annotations_name = 'annotation.json'
root =  os.path.dirname(os.getcwd())

photos_folder = os.path.join(root, 'photos')


try:
    with open(os.path.join(root, annotations_name)) as json_file:
        try:
            data = json.load(json_file)
        except:
            print('Annotation file is empty!')

    if len(data):
        for photo_name in data.keys():
            w, h, m = data[photo_name]
            annotation = 'width: {}, height: {}, mass: {}'.format(w, h, m)

            color_img = '_image.png'
            depth_img = '_depth.png'

            img_name = os.path.join(root, photos_folder, photo_name + color_img)
            depth_name = os.path.join(root, photos_folder, photo_name + depth_img)

            img = cv2.imread(img_name)
            depth = cv2.imread(depth_name)

            cv2.putText(img, annotation, (20, 40), 1, cv2.FONT_HERSHEY_COMPLEX, (255, 0, 100), 3)
            cv2.putText(depth, annotation, (20, 40), 1, cv2.FONT_HERSHEY_COMPLEX, (255, 0, 100), 3)

            cv2.imshow('img', img)
            cv2.imshow('depth', depth)
            if cv2.waitKey() & 0xFF == 27:
                break

        cv2.destroyAllWindows()

except:
    print('There is no anotation file!')