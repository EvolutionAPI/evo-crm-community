#!/bin/sh
envsubst '$AUTH_UPSTREAM $CRM_UPSTREAM $CORE_UPSTREAM $PROCESSOR_UPSTREAM $BOT_RUNTIME_UPSTREAM' < /etc/nginx/nginx.conf.template > /etc/nginx/conf.d/default.conf
exec nginx -g "daemon off;"
