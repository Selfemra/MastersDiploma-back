import face_recognition

class FaceComparator:
    def __init__(self):
        pass
    
    def find_face_encodings(image):
        # get face encodings from the image
        face_enc = face_recognition.face_encodings(image)
        # return face encodings
        return face_enc[0]
    
    def compare(img1, img2):
        img1 = FaceComparator.find_face_encodings(img1)
        img2 = FaceComparator.find_face_encodings(img2)
        is_same = face_recognition.compare_faces([img1], img2)[0]
        if is_same:
            # finding the distance level between images
            distance = face_recognition.face_distance([img1], img2)
            distance = round(distance[0] * 100)
            
            # calcuating accuracy level between images
            accuracy = 100 - round(distance)
            #print("The images are same")
            #print(f"Accuracy Level: {accuracy}%")
        #else:
            #print("The images are not same")

        return (is_same, accuracy)