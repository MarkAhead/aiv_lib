import requests
import os

server_uri = "http://localhost:5050/"
upload_to_insta_api = "upload_to_insta"

def upload_to_server(caption, video_path=None, images_path=None, thumbnail=None, username_key = None):
    # Define the URL of your Flask server
    server_url = server_uri + upload_to_insta_api

    # Prepare the files payload if files are provided
    files = []

    if video_path:
        with open(video_path, 'rb') as video_file:
            files.append(('video', (os.path.basename(video_path), video_file.read())))

    if thumbnail:
        with open(thumbnail, 'rb') as thumbnail_file:
            files.append(('thumbnail', (os.path.basename(thumbnail), thumbnail_file.read())))

    if images_path:
        image_files = []
        for image in images_path:
            with open(image, 'rb') as image_file:
                image_files.append(('images', (os.path.basename(image), image_file.read())))
        files.extend(image_files)

    # Prepare the data you want to send to the server
    data = {'caption': caption}

    # Make a POST request to the server
    response = requests.post(server_url, data=data, files=files)

    if response.status_code == 200:
        response_data = response.json()
        if "publish_response" in response_data:
            return response_data.get("publish_response")
        else:
            print("Upload failed. Response from server:", response.text)
            return None
    else:
        print("Upload failed with status code:", response.status_code)
        print("Response from server:", response.text)
        return None





if __name__ == "__main__" :
    hashtags = "#Nietzsche #Nihilism #Philosophy #Existentialism #Ubermensch #Culture"

    images_path = ['/Users/yadubhushan/Documents/media/python_space/output/caption_output/62c0c06d762d871d1fbaf3610cef7a360d1d6ff5c96919e2674b79661ac902e3/output_image_0.jpg', 
                '/Users/yadubhushan/Documents/media/python_space/output/caption_output/62c0c06d762d871d1fbaf3610cef7a360d1d6ff5c96919e2674b79661ac902e3/output_image_1.jpg', 
                '/Users/yadubhushan/Documents/media/python_space/output/caption_output/62c0c06d762d871d1fbaf3610cef7a360d1d6ff5c96919e2674b79661ac902e3/output_image_2.jpg', 
            '/Users/yadubhushan/Documents/media/python_space/output/caption_output/62c0c06d762d871d1fbaf3610cef7a360d1d6ff5c96919e2674b79661ac902e3/output_image_3.jpg',
                    '/Users/yadubhushan/Documents/media/python_space/output/caption_output/62c0c06d762d871d1fbaf3610cef7a360d1d6ff5c96919e2674b79661ac902e3/output_image_4.jpg', 
                    '/Users/yadubhushan/Documents/media/python_space/output/caption_output/62c0c06d762d871d1fbaf3610cef7a360d1d6ff5c96919e2674b79661ac902e3/output_image_5.jpg']
    
    caption = "Join us as we navigate through the provocative yet enlightening philosophy of Nietzsche, his understanding of nihilism, and its implications for existential thought. Hold tight; we're about to question everything we know."
    caption = caption + "\n\n\n\n" + " " + hashtags
   
    upload_response = upload_to_server(caption, images_path = images_path)

    if upload_response:
        print("Upload was successful. Server response:", upload_response)
    else:
        print("Upload failed.")



    
