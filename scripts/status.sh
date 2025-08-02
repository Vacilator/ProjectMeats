#!/bin/bash
# ProjectMeats Status Check

echo "📊 ProjectMeats System Status"
echo "=========================="

echo "🐍 Django Application:"
systemctl status projectmeats --no-pager -l

echo ""
echo "🌐 Nginx Web Server:"
systemctl status nginx --no-pager -l

echo ""
echo "🔥 Firewall Status:"
ufw status verbose

echo ""
echo "💾 Disk Usage:"
df -h

echo ""
echo "🧠 Memory Usage:"
free -h

echo ""
echo "⚡ CPU Usage:"
top -bn1 | grep "Cpu(s)" | awk '{print $2 + $4}'

echo ""
echo "📈 Application Logs (last 10 lines):"
tail -10 /home/projectmeats/logs/gunicorn_error.log