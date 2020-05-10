import face_recognition
import numpy as np
import os

# This is a super simple (but slow) example of running face recognition on live video from your webcam.
# There's a second example that's a little more complicated but runs faster.

# PLEASE NOTE: This example requires OpenCV (the `cv2` library) to be installed only to read from your webcam.
# OpenCV is *not* required to use the face_recognition library. It's only required if you want to run this
# specific demo. If you have trouble installing it, try any of the other demos that don't require it instead.

# Get a reference to webcam #0 (the default one)

#frame = face_recognition.load_image_file("test.jpg")
def detect_faces_in_image(frame):
    files_image = {}
    files_face_encoding = []
    #relevant_path = "D:\\2019\\python\\face_recognition-master\\face_recognition-master\\examples"
    relevant_path = os.path.dirname(os.path.abspath(__file__))
    print(relevant_path)

    included_extensions = ['jpg']
    file_names = [fn for fn in os.listdir(relevant_path)
                  if any(fn.endswith(ext) for ext in included_extensions)]

    for i in file_names:
        files_image[i] = face_recognition.load_image_file(os.path.join(relevant_path,i))
        files_face_encoding.append(face_recognition.face_encodings(files_image[i])[0])

    known_face_encodings = [
        files_face_encoding[x] for x in range(len(files_face_encoding))
    ]

    known_face_names = [i[:i.index('.')] for i in file_names]

    # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
    rgb_frame = frame[:, :, ::-1]

    # Find all the faces and face enqcodings in the frame of video
    face_locations = face_recognition.face_locations(rgb_frame)
    face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
    face_names = []

    # Loop through each face in this frame of video
    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
        # See if the face is a match for the known face(s)
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding)

        name = "Unknown"

        # Or instead, use the known face with the smallest distance to the new face
        face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
        best_match_index = np.argmin(face_distances)
        if matches[best_match_index]:
            name = known_face_names[best_match_index]

        # Store the name in an array to display it later
        face_names.append(name)
        #print(name)
    return(face_names)


#detect_faces_in_image(frame)
