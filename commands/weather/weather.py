import requests


def initialize(sentence):
    sentence = ' '.join(word[0] for word in sentence)
    try:
        sentence = sentence.split('in')
        city_name = sentence[1]
    except:
        city_name = 'Sofia'

    api_address = f"http://api.openweathermap.org/data/2.5/weather?appid=b68a826aef0732d3015ea008065af9ef&q={city_name}&units=metric"
    response = requests.get(api_address).json()
    # print(response)

    return_value = ''

    if response['cod'] == 200:
        if 'humidity' in sentence:
            humidity = response['main']['humidity']
            return_value += f'Humidity is {humidity}%.'
        elif 'pressure' in sentence:
            pressure = response['main']['pressure']
            return_value += f'Pressure is {pressure} hydro-pascals.'
        else:
            temp = round(response['main']['temp'], 2)
            return_value += f'It\'s {temp} degrees Celsius.'
    else:
        return_value = "Sorry. Could not get weather information."

    return return_value
