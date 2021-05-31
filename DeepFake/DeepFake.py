import numpy as np
import cv2
import dlib
import pyvirtualcam
from tkinter import *
from tkinter import filedialog

def extract_index(nparray):
        nparray = nparray
        index = None
        for num in nparray[0]:
            index = num
            break
        return index

class Deepfake:

    def __init__(self):
        print("test")

    def swap(self, photo):
        self.photo = photo
        img = cv2.imread(self.photo)
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        mask = np.zeros_like(img_gray)

        capture = cv2.VideoCapture(0)

        detector = dlib.get_frontal_face_detector() 
        predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

        triangle_indexes = []

        # Pierwsza twarz

        faces = detector(img_gray)
        for face in faces:
            landmarks = predictor(img_gray, face) #mapowanie punktów charakterystycznych twarzy i dodanie ich do arraya
            landmarks_points = []
            for n in range(0, 68):
                x = landmarks.part(n).x
                y = landmarks.part(n).y
                landmarks_points.append((x, y))


            points = np.array(landmarks_points, np.int32)  
            convexhull = cv2.convexHull(points)        #otoczka punktów twarzy

            cv2.fillConvexPoly(mask, convexhull, 255)  #biała otoczka na czarnym tle

            face_cutout = cv2.bitwise_and(img, img, mask=mask)


            #Delone triangulacja
            rect = cv2.boundingRect(convexhull)
            subdiv = cv2.Subdiv2D(rect) #obszar który będzie dzielony na trójkąty
            subdiv.insert(landmarks_points)
            triangles = subdiv.getTriangleList()
            triangles = np.array(triangles, dtype = np.int32)


            for triangle in triangles:
                p1 = (triangle[0], triangle[1]) #mapowanie
                p2 = (triangle[2], triangle[3])
                p3 = (triangle[4], triangle[5])

                index_p1 = np.where((points == p1).all(axis = 1)) #przypisanie indeksów dla konkretnych punktów
                index_p1 = extract_index(index_p1)

                index_p2 = np.where((points == p2).all(axis = 1)) 
                index_p2 = extract_index(index_p2)

                index_p3 = np.where((points == p3).all(axis = 1)) 
                index_p3 = extract_index(index_p3)

                if index_p1 is not None and index_p2 is not None and index_p3 is not None:
                    triangle = [index_p1, index_p2, index_p3]
                    triangle_indexes.append(triangle)



        # Druga twarz (z kamery) i główna funkcjonalność
        with pyvirtualcam.Camera(width=1280, height=720, fps=20,fmt=pyvirtualcam.PixelFormat.BGR) as cam:
            while True:
                ret, img2 = capture.read()
                img2_gray = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
                img2_new_face = np.zeros_like(img2)
    
                faces2 = detector(img2_gray)
                for face in faces2:
                    landmarks = predictor(img2_gray, face)
                    landmarks_points2 = []
                    for n in range(0, 68):
                        x = landmarks.part(n).x
                        y = landmarks.part(n).y
                        landmarks_points2.append((x, y))
    
                    points2 = np.array(landmarks_points2, np.int32)
                    convexhull2 = cv2.convexHull(points2)
    
                lines_space_mask = np.zeros_like(img_gray)
                lines_space_new_face = np.zeros_like(img2)
                #Triangulacja
                for triangle_index in triangle_indexes:
                    t1p1 = landmarks_points[triangle_index[0]]
                    t1p2 = landmarks_points[triangle_index[1]]
                    t1p3 = landmarks_points[triangle_index[2]]
                    triangle1 = np.array([t1p1, t1p2, t1p3], np.int32)
    
                    rect1 = cv2.boundingRect(triangle1)
                    (x,y,w,h) = rect1;
                    cropped_triangle = img[y: y + h, x: x + w]
                    mask1 = np.zeros((h, w), np.uint8)
    
                    points = np.array([[t1p1[0] - x, t1p1[1] - y],
                                    [t1p2[0] - x, t1p2[1] - y],
                                    [t1p3[0] - x, t1p3[1] - y]], np.int32)
    
                    cv2.fillConvexPoly(mask1, points, 255)
    
    
                #triangle 2
                    t2p1 = landmarks_points2[triangle_index[0]]
                    t2p2 = landmarks_points2[triangle_index[1]]
                    t2p3 = landmarks_points2[triangle_index[2]]
                    triangle2 = np.array([t2p1, t2p2, t2p3], np.int32)
    
                    rect2 = cv2.boundingRect(triangle2)
                    (x,y,w,h) = rect2;
    
                    cropped_triangle2 = img2[y: y + h, x: x + w]
                    mask2 = np.zeros((h, w), np.uint8)
    
                    points2 = np.array([[t2p1[0] - x, t2p1[1] - y],
                                    [t2p2[0] - x, t2p2[1] - y],
                                    [t2p3[0] - x, t2p3[1] - y]], np.int32)
    
                    cv2.fillConvexPoly(mask2, points2, 255)
                    cropped_triangle2 = cv2.bitwise_and(cropped_triangle2, cropped_triangle2, mask = mask2)
    
    
                    #transformacja trójkątów
                    points = np.float32(points)
                    points2 = np.float32(points2)
                    M = cv2.getAffineTransform(points, points2)
                    warped_triangle = cv2.warpAffine(cropped_triangle, M, (w, h))
                    warped_triangle = cv2.bitwise_and(warped_triangle, warped_triangle, mask = mask2)
    
                    #zrekonstruowanie 2 twarzy
                    img2_new_face_rect = img2_new_face[y: y + h, x: x + w]
                    img2_new_face_rect_gray = cv2.cvtColor(img2_new_face_rect, cv2.COLOR_BGR2GRAY)
                    b, bg = cv2.threshold(img2_new_face_rect_gray, 1, 255, cv2.THRESH_BINARY_INV)  #biało-czarny background
                    warped_triangle = cv2.bitwise_and(warped_triangle, warped_triangle, mask=bg) 
                    #dodawanie każdego trójkąta na ten sam bg
                    img2_new_face_rect = cv2.add(img2_new_face_rect, warped_triangle)
                    img2_new_face[y: y + h, x: x + w] = img2_new_face_rect
    
    
                #wklejenie nowej twarzy
                img2_face_mask = np.zeros_like(img2_gray)
                img2_head_mask = cv2.fillConvexPoly(img2_face_mask, convexhull2, 255)
                img2_face_mask = cv2.bitwise_not(img2_head_mask)
    
                background = cv2.bitwise_and(img2, img2, mask=img2_face_mask)
                result = cv2.add(background, img2_new_face)
    
                (x, y, w, h) = cv2.boundingRect(convexhull2)
                center_face2 = (int((x + x + w) / 2), int((y + y + h) / 2))
    
                seamless_clone = cv2.seamlessClone(result, img2, img2_head_mask, center_face2, cv2.MONOCHROME_TRANSFER)
                seamless_clone2 = cv2.seamlessClone(result, img2, img2_head_mask, center_face2, cv2.NORMAL_CLONE) #nie działa?
                seamless_clone3 = cv2.seamlessClone(result, img2, img2_head_mask, center_face2, cv2.MIXED_CLONE) #najlepszy efekt
    
                #cv2.imshow("Face swap monochrome", seamless_clone)
                #cv2.imshow("Face swap normal", seamless_clone2)
                cv2.imshow("Face swap real time", seamless_clone3)
                

                frame = cv2.resize(seamless_clone3, (1280, 720), interpolation=cv2.BORDER_DEFAULT)
                cam.send(frame)
                cam.sleep_until_next_frame()
    
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break


        cv2.destroyAllWindows
        capture.release()

        

    def points(self):
        capture = cv2.VideoCapture(0)

        detector = dlib.get_frontal_face_detector() 
        predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

        triangle_indexes = []

        # Druga twarz (z kamery) i główna funkcjonalność
        with pyvirtualcam.Camera(width=1280, height=720, fps=20,fmt=pyvirtualcam.PixelFormat.BGR) as cam:
            while True:
                ret, img2 = capture.read()
                img2_gray = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
                img2_new_face = np.zeros_like(img2)
    
                faces2 = detector(img2_gray)
                for face in faces2:
                    landmarks = predictor(img2_gray, face)
                    landmarks_points2 = []
                    for n in range(0, 68):
                        x = landmarks.part(n).x
                        y = landmarks.part(n).y
                        landmarks_points2.append((x, y))
                        cv2.circle(img2, (x,y), 2, (0,0,255), -1)
    
                    
    
                lines_space_new_face = np.zeros_like(img2)
    
    
                cv2.imshow("Points", img2)
                frame = cv2.resize(img2, (1280, 720), interpolation=cv2.BORDER_DEFAULT)
                cam.send(frame)
                cam.sleep_until_next_frame()
    
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break


        cv2.destroyAllWindows
        capture.release()


    def change_face(self, photo1, photo2):
        self.photo1 = photo1
        self.photo2 = photo2
        print(self.photo1 + ", " + self.photo2)
        img = cv2.imread(photo1)
        img2 = cv2.imread(photo2)
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  # konieczne
        img2_gray = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
        mask = np.zeros_like(img_gray)

        img2_new_face = np.zeros_like(img2)

        detector = dlib.get_frontal_face_detector()
        predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

        # Pierwsza twarz

        faces = detector(img_gray)
        for face in faces:
            landmarks = predictor(img_gray, face)  # mapowanie punktów charakterystycznych twarzy i dodanie ich do arraya
            landmarks_points = []
            for n in range(0, 68):
                x = landmarks.part(n).x
                y = landmarks.part(n).y
                landmarks_points.append((x, y))

            points = np.array(landmarks_points, np.int32)
            convexhull = cv2.convexHull(points)  # otoczka punktów twarzy (tak jakby "krawędzie")

            # cv2.polylines(img, [convexhull], True, (255, 0, 0), 2) #otoczka (linie)
            cv2.fillConvexPoly(mask, convexhull, 255)

            face_cutout = cv2.bitwise_and(img, img, mask=mask)

            # Delone triang
            rect = cv2.boundingRect(convexhull)
            subdiv = cv2.Subdiv2D(rect)
            subdiv.insert(landmarks_points)
            triangles = subdiv.getTriangleList()
            triangles = np.array(triangles, dtype=np.int32)

            triangle_indexes = []
            for triangle in triangles:
                p1 = (triangle[0], triangle[1])
                p2 = (triangle[2], triangle[3])
                p3 = (triangle[4], triangle[5])

                index_p1 = np.where((points == p1).all(axis=1))  # przypisanie indeksów dla konkretnych punktów
                index_p1 = extract_index(index_p1)

                index_p2 = np.where((points == p2).all(axis=1))
                index_p2 = extract_index(index_p2)

                index_p3 = np.where((points == p3).all(axis=1))
                index_p3 = extract_index(index_p3)

                if index_p1 is not None and index_p2 is not None and index_p3 is not None:
                    triangle = [index_p1, index_p2, index_p3]
                    triangle_indexes.append(triangle)

                # cv2.line(img, p1, p2, (0, 0, 255), 1)
                # cv2.line(img, p2, p3, (0, 0, 255), 1)
                # cv2.line(img, p1, p3, (0, 0, 255), 1)

        # Druga twarz
        faces2 = detector(img2_gray)
        for face in faces2:
            landmarks = predictor(img2_gray, face)  # mapowanie punktów charakterystycznych twarzy i dodanie ich do arraya
            landmarks_points2 = []
            for n in range(0, 68):
                x = landmarks.part(n).x
                y = landmarks.part(n).y
                landmarks_points2.append((x, y))

            points2 = np.array(landmarks_points2, np.int32)
            convexhull2 = cv2.convexHull(points2)

        lines_space_mask = np.zeros_like(img_gray)
        lines_space_new_face = np.zeros_like(img2)
        # Triangulacja obu twarzy
        for triangle_index in triangle_indexes:
            # triangle 1
            t1p1 = landmarks_points[triangle_index[0]]
            t1p2 = landmarks_points[triangle_index[1]]
            t1p3 = landmarks_points[triangle_index[2]]
            triangle1 = np.array([t1p1, t1p2, t1p3], np.int32)

            rect1 = cv2.boundingRect(triangle1)
            (x, y, w, h) = rect1;
            cropped_triangle = img[y: y + h, x: x + w]
            mask1 = np.zeros((h, w), np.uint8)

            points = np.array([[t1p1[0] - x, t1p1[1] - y],
                            [t1p2[0] - x, t1p2[1] - y],
                            [t1p3[0] - x, t1p3[1] - y]], np.int32)

            cv2.fillConvexPoly(mask1, points, 255)

            cv2.line(lines_space_mask, t1p1, t1p2, (0, 0, 255), 1)
            cv2.line(lines_space_mask, t1p1, t1p3, (0, 0, 255), 1)
            cv2.line(lines_space_mask, t1p2, t1p3, (0, 0, 255), 1)
            lines_space = cv2.bitwise_and(img, img, mask=lines_space_mask)

            # triangle 2
            t2p1 = landmarks_points2[triangle_index[0]]
            t2p2 = landmarks_points2[triangle_index[1]]
            t2p3 = landmarks_points2[triangle_index[2]]
            triangle2 = np.array([t2p1, t2p2, t2p3], np.int32)

            rect2 = cv2.boundingRect(triangle2)
            (x, y, w, h) = rect2;

            cropped_triangle2 = img2[y: y + h, x: x + w]
            mask2 = np.zeros((h, w), np.uint8)

            points2 = np.array([[t2p1[0] - x, t2p1[1] - y],
                                [t2p2[0] - x, t2p2[1] - y],
                                [t2p3[0] - x, t2p3[1] - y]], np.int32)

            cv2.fillConvexPoly(mask2, points2, 255)
            cropped_triangle2 = cv2.bitwise_and(cropped_triangle2, cropped_triangle2, mask=mask2)

            # cv2.line(img2, t2p1, t2p2, (0, 0, 255), 1)
            # cv2.line(img2, t2p1, t2p3, (0, 0, 255), 1)
            # cv2.line(img2, t2p2, t2p3, (0, 0, 255), 1)

            # transformacja trójkątów
            points = np.float32(points)
            points2 = np.float32(points2)
            M = cv2.getAffineTransform(points, points2)
            warped_triangle = cv2.warpAffine(cropped_triangle, M, (w, h))
            warped_triangle = cv2.bitwise_and(warped_triangle, warped_triangle, mask=mask2)

            # zrekonstruowanie 2 twarzy
            img2_new_face_rect_area = img2_new_face[y: y + h, x: x + w]
            img2_new_face_rect_area_gray = cv2.cvtColor(img2_new_face_rect_area, cv2.COLOR_BGR2GRAY)
            b, bg = cv2.threshold(img2_new_face_rect_area_gray, 1, 255, cv2.THRESH_BINARY_INV)
            warped_triangle = cv2.bitwise_and(warped_triangle, warped_triangle, mask=bg)

            img2_new_face_rect_area = cv2.add(img2_new_face_rect_area, warped_triangle)
            img2_new_face[y: y + h, x: x + w] = img2_new_face_rect_area

        # wklejenie nowej twarzy
        img2_face_mask = np.zeros_like(img2_gray)
        img2_head_mask = cv2.fillConvexPoly(img2_face_mask, convexhull2, 255)
        img2_face_mask = cv2.bitwise_not(img2_head_mask)

        background = cv2.bitwise_and(img2, img2, mask=img2_face_mask)
        result = cv2.add(background, img2_new_face)

        (x, y, w, h) = cv2.boundingRect(convexhull2)
        center_face2 = (int((x + x + w) / 2), int((y + y + h) / 2))

        seamless_clone = cv2.seamlessClone(result, img2, img2_head_mask, center_face2, cv2.NORMAL_CLONE)

        cv2.imshow("Face", seamless_clone)
        
        
