# -*- coding: utf-8 -*-
import sys, os
sys.path.append('/home/f/fediaz0y/fediaz0y.beget.tech/newproj') # указываем директорию с проектом
sys.path.append('/home/f/fediaz0y/fediaz0y.beget.tech/venv/bin/python') # указываем директорию с библиотеками, куда поставили Flask
from newproj import app as application # когда Flask стартует, он ищет application. Если не указать 'as application', сайт не заработает
from werkzeug.debug import DebuggedApplication # Опционально: подключение модуля отладки
application.wsgi_app = DebuggedApplication(application.wsgi_app, True) # Опционально: включение модуля отадки
application.debug = False  # Опционально: True/False устанавливается по необходимости в отладке