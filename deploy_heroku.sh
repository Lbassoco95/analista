#!/bin/bash

APP_NAME="nombre-de-tu-app-heroku"
heroku config:set OPENAI_API_KEY="TU_API_KEY_AQUI" --app $APP_NAME

echo "Variables de entorno configuradas en Heroku para $APP_NAME"
