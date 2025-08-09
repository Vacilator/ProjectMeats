# HTTPS/SSL Setup Guide for ProjectMeats

This guide explains how to enable HTTPS/SSL for your ProjectMeats deployment.

## Overview

ProjectMeats now supports HTTPS/SSL connections through:
- **Nginx**: Handles SSL termination and HTTP→HTTPS redirects
- **Django**: Configured with security headers and secure cookies
- **Docker**: Exposes port 443 for HTTPS traffic

## Quick Start

### 1. Set Up SSL Certificates

Run the SSL setup script to generate or configure certificates:

```bash
# For development (self-signed certificate)
./setup_ssl.sh localhost

# For production (replace with your domain)
./setup_ssl.sh yourdomain.com
```

### 2. Configure Your Domain

Update `nginx/nginx.conf` and replace `your_droplet_ip` with your actual domain:

```nginx
server_name yourdomain.com www.yourdomain.com;
```

### 3. Start with HTTPS

Use the production Docker Compose configuration:

```bash
# Set environment variables
export SERVER_NAME=yourdomain.com
export SSL_CERT_PATH=./ssl

# Start with HTTPS enabled
docker-compose -f docker-compose.prod.yml up -d
```

## SSL Certificate Options

### Option 1: Self-Signed Certificates (Development)

For local development and testing:

```bash
./setup_ssl.sh localhost
```

**Pros**: Quick setup, works offline
**Cons**: Browser security warnings, not trusted by clients

### Option 2: Let's Encrypt (Production - Free)

For production deployments with valid domains:

```bash
# Ensure port 80 is free and domain points to your server
./setup_ssl.sh yourdomain.com
```

**Pros**: Free, trusted by all browsers, auto-renewal
**Cons**: Requires valid domain and internet access

### Option 3: Commercial SSL Certificate

For production with purchased certificates:

```bash
# Choose option 3 in setup script
./setup_ssl.sh
```

**Pros**: Full trust, extended validation options
**Cons**: Cost, manual renewal

## Environment Configuration

### Backend Environment Variables

Update your `.env` file with SSL settings:

```env
# Enable SSL/HTTPS
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True

# HSTS (HTTP Strict Transport Security)
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True

# Update allowed origins for HTTPS
CORS_ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
CSRF_TRUSTED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
```

### Frontend Environment Variables

Update `frontend/.env.production`:

```env
REACT_APP_API_BASE_URL=https://yourdomain.com/api/v1
REACT_APP_ENVIRONMENT=production
```

## Directory Structure

After setup, your SSL directory should look like:

```
ssl/
├── cert.pem    # SSL certificate
└── key.pem     # Private key
```

## Docker Compose Files

### Development (docker-compose.yml)
- HTTP on port 80 + HTTPS on port 443
- Self-signed certificates
- SSL volume commented out by default

### Production (docker-compose.prod.yml)
- Full SSL configuration
- Environment variables for customization
- Automatic HTTPS redirects
- Security headers enabled

## Security Features

### Nginx Security Configuration

- **HTTP → HTTPS redirect**: All HTTP traffic redirected to HTTPS
- **Modern SSL protocols**: TLS 1.2 and 1.3 only
- **Security headers**: HSTS, X-Frame-Options, CSP, etc.
- **Strong ciphers**: Secure cipher suites only

### Django Security Settings

- **SSL redirect**: `SECURE_SSL_REDIRECT=True`
- **Secure cookies**: Session and CSRF cookies marked secure
- **HSTS**: HTTP Strict Transport Security enabled
- **Security headers**: X-Content-Type-Options, X-XSS-Protection

## Testing HTTPS

### 1. Verify SSL Certificate

```bash
# Check certificate details
openssl x509 -in ssl/cert.pem -text -noout

# Test SSL connection
openssl s_client -connect yourdomain.com:443 -servername yourdomain.com
```

### 2. Test HTTP → HTTPS Redirect

```bash
curl -I http://yourdomain.com
# Should return: HTTP/1.1 301 Moved Permanently
# Location: https://yourdomain.com/
```

### 3. Verify Security Headers

```bash
curl -I https://yourdomain.com
# Should include:
# Strict-Transport-Security: max-age=31536000; includeSubDomains; preload
# X-Content-Type-Options: nosniff
# X-Frame-Options: DENY
```

### 4. Run SSL Tests

```bash
python /tmp/test_ssl_config.py
```

## Troubleshooting

### Common Issues

1. **Browser Security Warning**
   - **Cause**: Self-signed certificate
   - **Solution**: Click "Advanced" → "Proceed" or use valid certificate

2. **Connection Refused on Port 443**
   - **Cause**: HTTPS port not exposed or certificates missing
   - **Solution**: Check docker-compose ports and SSL directory

3. **Mixed Content Warnings**
   - **Cause**: HTTP resources loaded on HTTPS page
   - **Solution**: Update frontend API URLs to HTTPS

4. **Certificate Not Found**
   - **Cause**: SSL certificates not mounted correctly
   - **Solution**: Check volume mapping in docker-compose.yml

### Debug Commands

```bash
# Check nginx configuration
docker-compose exec nginx nginx -t

# View nginx error logs
docker-compose logs nginx

# Check certificate files
ls -la ssl/
openssl x509 -in ssl/cert.pem -text -noout

# Test SSL configuration
docker run --rm -it --network host curlimages/curl:latest \
    curl -k -I https://localhost
```

## Certificate Renewal

### Let's Encrypt Auto-Renewal

```bash
# Set up automatic renewal (crontab)
0 12 * * * /usr/bin/certbot renew --quiet && docker-compose restart nginx
```

### Manual Renewal

```bash
# Renew Let's Encrypt certificate
sudo certbot renew

# Copy new certificates
sudo cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem ssl/cert.pem
sudo cp /etc/letsencrypt/live/yourdomain.com/privkey.pem ssl/key.pem

# Restart nginx
docker-compose restart nginx
```

## Production Deployment Checklist

- [ ] Valid domain name configured in DNS
- [ ] SSL certificates obtained and configured
- [ ] Nginx server_name updated with actual domain
- [ ] Environment variables set for production
- [ ] HTTPS port (443) open in firewall
- [ ] HTTP to HTTPS redirect tested
- [ ] Security headers validated
- [ ] Certificate renewal configured (if using Let's Encrypt)

## Additional Security Considerations

1. **Firewall Configuration**
   ```bash
   # Open HTTPS port
   sudo ufw allow 443/tcp
   ```

2. **SSL/TLS Monitoring**
   - Monitor certificate expiration
   - Set up SSL health checks
   - Use tools like SSL Labs to test configuration

3. **Security Headers**
   - Content Security Policy (CSP)
   - HTTP Public Key Pinning (HPKP)
   - Certificate Transparency

For more information, see the [ProjectMeats Deployment Guide](PRODUCTION_DEPLOYMENT.md).