Weather
=======

Enables the response of weather-related queries from Eva.

Utilizes the [DarkSky](https://darksky.net) [API](https://darksky.net/dev/) to formulate weather query responses.

## Installation

Can be easily installed through the Web UI by using [Web UI Plugins](https://github.com/edouardpoitras/eva-web-ui-plugins).

Alternatively, add `weather` to your `eva.conf` file in the `enabled_plugins` option list and restart Eva.

## Usage

You will need to get a free API key [here](https://darksky.net/dev/) for this plugin to work properly.

You API key should be added to the weather plugin configuration using one of the following methods:

* Use the [Web UI Plugins](https://github.com/edouardpoitras/eva-web-ui-plugins) weather plugin configuration form at `https://<eva.domain:port>/plugins/configuration/weather`
* Add the following line to `weather.conf`:

    `darksky_api_key = "<key>"`

Note: You may need to create the `weather.conf` file in your plugin config path - usually `~/eva/configs`.

The weather plugin will attempt to determine your location based on IP address. This is required in order to give you accurate weather information.

If it fails to give an accurate location, you can specify the location manually using the same method mentioned above for the API key. You can use the `location` configuration option or a combination of the `latitude` and `longitude` configuration options.

## Configuration

Default configurations can be changed by adding a `weather.conf` file in your plugin configuration path (can be configured in `eva.conf`, but usually `~/eva/configs`).

To get an idea of what configuration options are available, you can take a look at the `weather.conf.spec` file in this repository, or use the [Web UI Plugins](https://github.com/edouardpoitras/eva-web-ui-plugins) plugin and view them at `/plugins/configuration/weather`.

Here is a breakdown of the available options:

    darksky_api_key
        Type: String
        Default: ''
        The DarkSky API key. Required for this plugin to be useful.
    location
        Type: String
        Default: ''
        The default location used when performing weather queries (for example: 'Ottawa, Ontario, Canada')
    latitude
        Type: Float (-90.0 to 90.0)
        Default:
        The default latitude used when looking up weather information (precedence over location)
        Also requires longitude to be available.
    longitude
        Type: Float (-180.0 to 180.0)
        Default:
        The default longitude used when looking up weather information (precedence over location)
        Also requires latitude to be available.
    metric
        Type: Boolean
        Default: True
        Whether or not to use the metric system (celcius, km/h, km).
        A value of False means the weather plugin will use the imperial system (fahrenheit, mph, miles).
