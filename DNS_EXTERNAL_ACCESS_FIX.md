# DNS Setup and External Domain Access Fix

This document provides instructions for testing and fixing DNS configuration issues that prevent external access to your ProjectMeats deployment.

## Quick Test

Test your domain configuration with dig:
```bash
# Test if your domain resolves to the correct IP
dig +short A yourdomain.com

# Expected result: 167.99.155.140 (or your server IP)
# If no result or wrong IP, DNS needs configuration
```

## Automated DNS Setup

Use the provided DNS configuration script for automatic setup:

### With DigitalOcean API Token
```bash
# Set your DigitalOcean API token
export DO_TOKEN="your_digitalocean_api_token_here"

# Run automated DNS setup
./dns_config.sh --domain meatscentral.com --ip 167.99.155.140
```

### Manual Setup
```bash
# For manual configuration instructions
./dns_config.sh --domain meatscentral.com --ip 167.99.155.140
```

## Manual DNS Configuration

If automatic setup doesn't work, configure DNS manually:

1. **Go to your domain registrar** (GoDaddy, Namecheap, Cloudflare, etc.)
2. **Add A records:**
   - Name: `@` (root domain) → Value: `167.99.155.140`
   - Name: `www` → Value: `167.99.155.140`
3. **Set TTL:** 300 seconds (5 minutes) for faster propagation
4. **Wait for propagation:** 5 minutes to 48 hours

## Testing DNS Propagation

Check DNS propagation globally:
- https://dnschecker.org/#A/meatscentral.com
- https://www.whatsmydns.net/#A/meatscentral.com

## Troubleshooting

### Run Comprehensive Diagnostics
```bash
./diagnose_service.sh --domain meatscentral.com --ip 167.99.155.140
```

### Test Direct IP Access
If DNS isn't working yet, test if the server responds directly:
```bash
curl -I http://167.99.155.140
# Should return HTTP headers if server is working
```

### Test with DNS Bypass
Test if server works but DNS is the issue:
```bash
curl --resolve meatscentral.com:80:167.99.155.140 -I http://meatscentral.com
# Should work if server is fine but DNS isn't propagated
```

### Common Issues

1. **"No A record found"**
   - DNS not configured
   - Use dns_config.sh or configure manually at registrar

2. **"DNS resolves to wrong IP"**
   - Old A record pointing elsewhere
   - Update A record at registrar

3. **"Direct IP works but domain doesn't"**
   - DNS propagation in progress
   - Wait or use different DNS servers (8.8.8.8, 1.1.1.1)

4. **"Nothing responds"**
   - Server/nginx/firewall issue
   - Check: `systemctl status nginx`
   - Check: `ss -tuln | grep :80`
   - Check: `ufw status`

## Integration with Deployment

The enhanced deployment system now includes:

- **Automatic DNS detection** and configuration
- **DigitalOcean API integration** for automated A record setup
- **DNS propagation waiting** with 10-minute timeout
- **Enhanced port binding verification** for nginx
- **Bypass testing** to distinguish DNS vs server issues
- **Comprehensive diagnostics** for troubleshooting

## Files Added/Modified

- `dns_config.sh` - DNS automation script
- `diagnose_service.sh` - Comprehensive diagnostics
- `deploy_production.py` - Enhanced DNS verification
- `production_deploy.sh` - Improved nginx binding checks

## Support

If issues persist after following these steps:
1. Run `./diagnose_service.sh` for detailed analysis
2. Check the deployment logs for specific errors
3. Verify your server IP and domain registrar settings
4. Consider using a CDN like Cloudflare for additional DNS/proxy services