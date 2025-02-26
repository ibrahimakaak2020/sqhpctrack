import face_recognition

# Load images
image1 = face_recognition.load_image_file("person1.jpg")
image2 = face_recognition.load_image_file("person2.jpg")

# Compute face encodings
encoding1 = face_recognition.face_encodings(image1)[0]
encoding2 = face_recognition.face_encodings(image2)[0]

# Compare faces
results = face_recognition.compare_faces([encoding1], encoding2, tolerance=0.6)
print("Faces match:", results[0])