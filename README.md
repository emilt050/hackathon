
## Requirements APT
``` bash
sudo sh -c "apt update && apt install -y \
cmake python3-picamera2"

```

## Requirements Python 3.11
``` bash
python3 -m venv --system-site-packages .venv
source .venv/bin/activate
pip install -r requirements.txt
```


## Start
```
python3 manage.py runserver 0.0.0.0:8000
```
