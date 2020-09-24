# Adzan Notification 

Adzan Noification is a background service to send adzan notification with sound based on your location. 
Available for Linux and Windows 10 (not tested for other windows version)

## Installation

### Windows
Download the installer [here](https://github.com/versa-syahptr/Adzan-Notification). Install the software and it will do the rest. 
This software will automatically start after computer reboots.

### Linux

~ installer available soon, for now just clone this repo to your machine


## Usage
start, stop, or restart service
```bash
$./adzan-notification/service.py [start|stop|restart]
```

change city
```bash
$./adzan-notification/service.py -s
```
run the command above and a pop-up will show to ask your city.

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
[GPLv3](https://choosealicense.com/licenses/mit/)
