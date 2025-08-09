module.exports = {
  apps: [
    {
      name: 'projectmeats-django',
      cwd: '/opt/projectmeats/backend',
      script: '/opt/projectmeats/venv/bin/gunicorn',
      args: [
        '--bind', '127.0.0.1:8000',
        '--workers', '3',
        '--worker-class', 'gthread',
        '--threads', '2',
        '--worker-connections', '1000',
        '--max-requests', '1000',
        '--max-requests-jitter', '100',
        '--preload',
        '--access-logfile', '/var/log/projectmeats/access.log',
        '--error-logfile', '/var/log/projectmeats/error.log',
        '--log-level', 'info',
        '--pid', '/var/run/projectmeats/gunicorn.pid',
        'projectmeats.wsgi:application'
      ],
      interpreter: '/opt/projectmeats/venv/bin/python',
      env: {
        DJANGO_SETTINGS_MODULE: 'apps.settings.production'
      },
      env_file: '/etc/projectmeats/projectmeats.env',
      instances: 1,
      exec_mode: 'fork',
      watch: false,
      max_memory_restart: '500M',
      error_file: '/var/log/projectmeats/pm2_error.log',
      out_file: '/var/log/projectmeats/pm2_out.log',
      log_file: '/var/log/projectmeats/pm2_combined.log',
      time: true,
      autorestart: true,
      max_restarts: 10,
      min_uptime: '10s',
      restart_delay: 5000
    }
  ]
};