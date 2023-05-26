
from google.cloud import storage
client = storage.Client.from_service_account_json('firebase/serviceAccount.json')

import pyrebase

config = {
    'apiKey': "AIzaSyA8KtGeNIWQHYx1dNMeaGSOl79yKE9XqIk",
    'authDomain': "carparkingsystem-8d374.firebaseapp.com",
    'databaseURL': "https://carparkingsystem-8d374-default-rtdb.asia-southeast1.firebasedatabase.app",
    'projectId': "carparkingsystem-8d374",
    'storageBucket': "carparkingsystem-8d374.appspot.com",
    'messagingSenderId': "1005066593906",
    'appId': "1:1005066593906:web:82d2553f9b090e7b64c4eb",
    'measurementId': "G-3Z7W45QS83",
    'serviceAccount': 'firebase/serviceAccount.json',
}
firebase = pyrebase.initialize_app(config)
authe = firebase.auth()
storage = firebase.storage()

filename = f"{license_plate}-{uuid4().hex}.jpg"
bucket_name = "gs://carparkingsystem-8d374.appspot.com"
bucket = client.bucket(bucket_name)
# folder_path = "car_images/"
blob = bucket.blob(filename)
blob.upload_from_file(image)

# Lấy URL của ảnh từ Firebase Storage
image_url = blob.public_url
print(image_url)
