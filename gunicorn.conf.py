import multiprocessing

# Configuración de workers
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "uvicorn.workers.UvicornWorker"

# Configuración de timeouts
timeout = 120
keepalive = 2
max_requests = 1000
max_requests_jitter = 100

# Configuración de logging
accesslog = "-"
errorlog = "-"
loglevel = "info"

# Configuración de seguridad
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# Configuración de performance
preload_app = True
worker_connections = 1000 