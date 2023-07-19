# heaan-examples

## Introduction
A simple application written in Python powered by HEaaN.

## Setup
```
$ git clone https://github.com/sunchuljung/heaan-examples
$ cd ./heaan-examples
$ virtualenv -p python3 ./venv
$ source venv/bin/activate
$ pip install -r requirements.txt
```

For Linux users,
```
$ pip install dist/heaan-0.2.3-cp38-cp38-linux_x86_64.whl
```

## Running examples
Run server first;
```
$ python bob.py
```

Then you can run client with an arbitrary image file;
```
$ python alice.py -in <path to your image file>
```

## Wrap up
To exit from the virtual environment;
```
$ deactivate
```
