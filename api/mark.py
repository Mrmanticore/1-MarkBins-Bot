from flask import Flask, request, jsonify
import tweepy
import os
from dotenv import load_dotenv
import base64
import smtplib
import ssl
from email.message import EmailMessage
import io

app = Flask(__name__)

load_dotenv() 

consumer_key = os.getenv('consumer_key')
consumer_secret = os.getenv('consumer_secret')
access_token = os.getenv('access_token')
access_token_secret = os.getenv('access_token_secret')

clientv2 = tweepy.Client(
    consumer_key=consumer_key, consumer_secret=consumer_secret,
    access_token=access_token, access_token_secret=access_token_secret
)

auth = tweepy.OAuth1UserHandler(consumer_key=consumer_key, consumer_secret=consumer_secret)
auth.set_access_token(
    access_token,
    access_token_secret,
)
clientv1 = tweepy.API(auth)

@app.route('/tweet', methods=['POST'])
def tweet():
    data = request.json
    tweet_text = data.get('tweet')
    email = data.get('email')
    image_data = data.get('image')  # Base64-encoded image data

    # Decode the base64 image data and save it to a file
    base64_bytes = image_data.encode('ascii')
    image_bytes = base64.b64decode(base64_bytes)
    with open('temp_image.jpg', 'wb') as f:
        f.write(image_bytes)

    # Upload the image
    with open('temp_image.jpg', 'rb') as image_file:
        media = clientv1.simple_upload(filename='temp_image.jpg', file=image_file)
        media_id = media.media_id

    # Tweet the message with the image
    response = clientv2.create_tweet(
        text=tweet_text,
        media_ids=[media_id]
    )
    print(f"Tweet sent successfully: https://twitter.com/user/status/{response.data['id']}")

    # Clean up the temporary image file
    os.remove('temp_image.jpg')

    # Send email
    email_sender = os.getenv('EMAIL_SENDER')
    email_password = os.getenv('EMAIL_PASSWORD')
    email_receiver = email
    subject = 'Tweet sent successfully, MarkBin team'
    body = f"Thank you for your contribution! Your tweet has been successfully sent and is now live on Twitter. This is a great initiative towards cleaning and we appreciate your effort. Together, we can make a difference. Keep up the good work! Click here to view your tweet: https://twitter.com/user/status/{response.data['id']}\n\nMarkBin team regards"
    
    em = EmailMessage()
    em['From'] = email_sender
    em['To'] = email_receiver
    em['Subject'] = subject
    em.set_content(body)

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
        smtp.login(email_sender, email_password)
        smtp.sendmail(email_sender, email_receiver, em.as_string())

    return jsonify({'message': 'Tweet sent successfully!!'})

@app.route('/')
def index():
    return 'Flask Server is running successfully! -markbins'

if __name__ == '__main__':
    app.run(debug=True)
