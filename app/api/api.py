import requests


def get_data():
    response = requests.get('https://jsonplaceholder.typicode.com/todos')
    return response.json()