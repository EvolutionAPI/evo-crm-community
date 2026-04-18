FROM nginx:alpine

COPY nginx.conf /etc/nginx/nginx.conf.template

ENV NGINX_ENVSUBST_OUTPUT_DIR=/etc/nginx
ENV AUTH_UPSTREAM=evo_auth:3001
ENV CRM_UPSTREAM=evo_crm:3000
ENV CORE_UPSTREAM=evo_core:5555
ENV PROCESSOR_UPSTREAM=evo_processor:8000
ENV BOT_RUNTIME_UPSTREAM=evo_bot_runtime:8080

CMD ["/bin/sh", "-c", "envsubst '\ \ \ \ ' < /etc/nginx/nginx.conf.template > /etc/nginx/conf.d/default.conf && nginx -g 'daemon off;'"]

EXPOSE 3030
