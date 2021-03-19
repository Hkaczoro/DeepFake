import numpy as np
import cv2
import dlib

img = cv2.imread("prez.jpg")
img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) #konieczne dla lepszych rezultatów
mask = np.zeros_like(img_gray)

detector = dlib.get_frontal_face_detector() 
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat") #ten plik robi dużą robotę
faces = detector(img_gray)

for point in faces:
    landmarks = predictor(img_gray, point) #mapowanie punktów charakterystycznych twarzy i dodanie ich do arraya
    landmarks_points = []

    for n in range(0, 68):
        x = landmarks.part(n).x
        y = landmarks.part(n).y
        landmarks_points.append((x, y))

        #cv2.circle(img, (x, y), 3, (0, 0 ,255), -1) #pokazanie landmarków na wejściowym obrazku

    points = np.array(landmarks_points, np.int32)  #inaczej TypeError
    convexhull = cv2.convexHull(points)        #otoczka punktów twarzy (tak jakby "krawędzie")

    #cv2.polylines(img, [convexhull], True, (255, 0, 0), 2) #otoczka (linie)
    cv2.fillConvexPoly(mask, convexhull, 255)

    face_cutout = cv2.bitwise_and(img, img, mask=mask)




cv2.imshow("Image", img)
cv2.imshow("Face cutout", face_cutout)
cv2.waitKey(0)
cv2.destroyAllWindows