set -ev

service pgbouncer start

daphne project.asgi:application --port $PORT --bind 0.0.0.0
service pgbouncer stop
