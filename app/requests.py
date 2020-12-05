import requests,json

def get_posts():
    response = requests.get('http://quotes.stormconsultancy.co.uk/random.json')
    if response.status_code == 200:
        post = response.json()
        return post