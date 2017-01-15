"""
https://darksky.net/dev/docs/response#data-point

TODO: Implements a job that checks for severe weather warnings in user's area.
https://darksky.net/dev/docs/response#alerts
"""
import gossip
import requests
import geocoder
import forecastio
from eva.config import save_config
from eva import conf
from eva import log

@gossip.register('eva.interaction')
def eva_interaction(context):
    if not context.response_ready() and context.contains('weather'):
        response = get_basic_weather_response()
        context.set_output_text(response)

@gossip.register('eva.conversations.follow_up')
def eva_conversations_follow_up(plugin, context):
    if plugin == 'weather':
        log.info('Weather plugin handling follow-up question')
        response = get_follow_up_response(context)
        context.set_output_text(response)

def get_follow_up_response(context):
    forecast = get_forecast()
    if forecast is None:
        return 'I had some trouble getting the forecast, see the logs for more details'
    else:
        values = get_current_values(forecast, metric=conf['plugins']['weather']['config']['metric'])
        follow_up = []
        if context.contains('visibility'):
            follow_up.append('Current visibility is %s' %values['visibility'])
        if context.contains('storm'):
            follow_up.append('The nearest storm is %s' %values['nearest_storm'])
        if context.contains('wind') or context.contains('windspeed'):
            follow_up.append('The current wind speed is %s' %values['windspeed'])
        if context.contains('precipitation'):
            precip = values['precipitation_type']
            if precip is None:
                follow_up.append('There is currently no precipitation')
            else:
                follow_up.append('It is currently %sing' %precip)
        if context.contains('pressure'):
            follow_up.append('The current air pressure is %s' %values['pressure'])
        if context.contains('humidity'):
            follow_up.append('The current humidity is %s' %values['humidity'])
        if context.contains('cloud'):
            follow_up.append('The current cloud cover is %s' %values['cloud_cover'])
        return '. '.join(follow_up)

def get_basic_weather_response():
    forecast = get_forecast()
    if forecast is None:
        return 'I had some trouble getting the forecast, see the logs for more details'
    else:
        values = get_current_values(forecast, metric=conf['plugins']['weather']['config']['metric'])
        response = 'The current forecast for %s is %s with a temperature of %s' \
                   %(values['location'], values['summary'], values['temperature'])
        return response

def get_current_values(forecast, metric=True):
    current = forecast.currently()
    if metric:
        temp = '%s degrees celsius' %f_to_c(current.temperature)
        visibility = '%s kilometers' %m_to_km(current.visibility)
        nearest_storm = '%s kilometers away' %m_to_km(current.nearestStormDistance)
        windspeed = '%s kilometers per hour' %m_to_km(current.windSpeed)
    else:
        temp = '%s degrees fahrenheit' %current.temperature
        visibility = '%s miles' %current.visibility
        nearest_storm = '%s miles away' %current.nearestStormDistance
        windspeed = '%s miles per hour' %current.windSpeed
    if current.precipIntensity > 0:
        precip_type = current.precipType
    else:
        precip_type = None
    if conf['plugins']['weather']['config']['location'] == '':
        location = 'latitude %s, longitude %s,' % \
                   (conf['plugins']['weather']['config']['latitude'], \
                    conf['plugins']['weather']['config']['latitude'])
    else:
        location = conf['plugins']['weather']['config']['location']
        # Only use the city and state/province
        location = location.split(',')
        location = '%s, %s,' %(location[0].strip(), location[1].strip())
    pressure = '%s millibars' %current.pressure
    humidity = '%s percent' %round(current.humidity * 100, 0)
    cloud_cover = '%s percent' %round(current.cloudCover * 100)
    return {'location': location,
            'summary': current.summary,
            'temperature': temp,
            'visibility': visibility,
            'nearest_storm': nearest_storm,
            'windspeed': windspeed,
            'precipitation_type': precip_type,
            'pressure': pressure,
            'humidity': humidity,
            'cloud_cover': cloud_cover}

def get_lat_lng():
    lat, lng = (conf['plugins']['weather']['config'].get('latitude', None), \
                conf['plugins']['weather']['config'].get('longitude'))
    if lat is None or lat == '' or lng is None or lng == '':
        if conf['plugins']['weather']['config']['location'] == '':
            # Get by IP.
            g = geocoder.ip('me')
            location = '%s, %s, %s' %(g.city, g.state, g.country)
            conf['plugins']['weather']['config']['location'] = location
        else:
            # Get by Location.
            g = geocoder.google(conf['plugins']['weather']['config']['location'])
        lat, lng = g.latlng
        conf['plugins']['weather']['config']['latitude'] = lat
        conf['plugins']['weather']['config']['longitude'] = lng
        # Save for future queries.
        save_config('weather')
    return lat, lng

def get_forecast():
    lat, lng = get_lat_lng()
    if lat is None or lng is None:
        log.error('Invalid latitude or longitude: %s, %s' %(lat, lng))
        return None
    try:
        # Enable caching somehow?
        api_key = conf['plugins']['weather']['config']['darksky_api_key']
        forecast = forecastio.load_forecast(api_key, lat, lng)
        return forecast
    except requests.exceptions.HTTPError as err:
        log.error('Http error fetching weather - ensure you have set up your API key: %s' %err)
    except Exception as err:
        log.error('Unknown error fetching weather: %s' %err)
    return None

def f_to_c(temp):
    return round((temp - 32) * 5.0/9, 1)

def m_to_km(distance):
    return round(distance / 0.621371, 1)
