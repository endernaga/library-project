# Library API project
> project created for testing my skills

an API of the library which can be connected to frontend

## Installing / Getting started

A quick introduction of the minimal setup you need to get a hello world up &
running.

```shell
$ pip install -r requirements.txt
$ python manage.py migrate
$ docker run -d -p 6379:6379 redis  
$ stripe listen --forward-to localhost:8000/api/payments/webhooks
$ celery -A library worker --loglevel=INFO --without-gossip --without-mingle --without-heartbeat -Ofair --pool=solo
$ celery -A proj beat -l INFO --scheduler django_celery_beat.schedulers:DatabaseScheduler
$ python manage.py runserver
```

Here you should say what actually happens when you execute the code above.

### Initial Configuration

You need to create a telegram bot, then add him to your chat and write that to .env file.
Also you need to generate stripe API key and also write it in .env file

## Developing

Here's a brief intro about what a developer must do in order to start developing
the project further:

```shell
$ git clone https://github.com/endernaga/library-project.git
$ docker run -d -p 6379:6379 redis
```

You clone that project and create a redis on your PC which project use to schedule tasks

## Features

What's all the bells and whistles this project can perform?
* Create books
* Create borrowings
* Create payments
* Send a notifications to telegram chat
* auto payments check and change status
* auto price calculate
