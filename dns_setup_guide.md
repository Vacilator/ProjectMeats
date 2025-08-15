# DNS Setup Guide for ProjectMeats

This guide helps you configure DNS for your ProjectMeats deployment to make it accessible via your domain name.

## Overview

For your ProjectMeats application to be accessible externally, you need to configure DNS records that point your domain to your server's IP address.

## Server Information
- **Server IP**: 167.99.155.140
- **Domain**: meatscentral.com (replace with your domain)

## DNS Configuration Steps

### Step 1: Access Your DNS Management

Choose your provider:

#### DigitalOcean Domains
1. Log in to DigitalOcean
2. Go to **Networking** → **Domains**
3. Select your domain
4. Manage DNS records

#### NameCheap
1. Log in to NameCheap
2. Go to **Domain List**
3. Click **Manage** next to your domain
4. Navigate to **Advanced DNS**

#### GoDaddy
1. Log in to GoDaddy
2. Go to **My Domains**
3. Click **DNS** next to your domain

#### Cloudflare
1. Log in to Cloudflare
2. Select your domain
3. Go to **DNS** tab

### Step 2: Configure DNS Records

Add the following DNS records:

#### A Record (Primary)
```
Type: A
Name: @ (or leave blank for root domain)
Value: 167.99.155.140
TTL: 300 (5 minutes) - for faster updates
```

#### A Record (WWW Subdomain) - Optional but recommended
```
Type: A
Name: www
Value: 167.99.155.140
TTL: 300
```

#### Alternative: CNAME for WWW
```
Type: CNAME
Name: www
Value: meatscentral.com (your root domain)
TTL: 300
```

### Step 3: Verify DNS Configuration

#### Using Command Line (Linux/Mac)
```bash
# Check A record for root domain
dig +short A meatscentral.com

# Check A record for www subdomain
dig +short A www.meatscentral.com

# Expected output: 167.99.155.140
```

#### Using Online Tools
- **DNSChecker**: https://dnschecker.org/
- **WhatsMyDNS**: https://whatsmydns.net/
- **DNS Lookup**: https://mxtoolbox.com/DNSLookup.aspx

#### Using Windows Command Prompt
```cmd
nslookup meatscentral.com
nslookup www.meatscentral.com
```

## DNS Propagation

### Timeline
- **Local Changes**: 5-15 minutes
- **Regional Propagation**: 1-4 hours  
- **Global Propagation**: Up to 48 hours (typically 24 hours)

### Factors Affecting Propagation
- TTL (Time To Live) values - lower values = faster updates
- Your ISP's DNS cache refresh rate
- Geographic location of DNS servers

## Common Issues and Solutions

### Issue 1: DNS Not Resolving
**Symptoms**: Domain doesn't resolve to any IP
**Solutions**:
- Verify A record is correctly configured
- Check if domain is properly registered
- Wait longer for propagation

### Issue 2: Wrong IP Address
**Symptoms**: Domain resolves to incorrect IP
**Solutions**:
- Double-check A record value is `167.99.155.140`
- Clear local DNS cache
- Wait for propagation to complete

### Issue 3: Partial Resolution
**Symptoms**: Root domain works but www doesn't (or vice versa)
**Solutions**:
- Add missing A record or CNAME
- Ensure both root and www records are configured

## DigitalOcean Specific Instructions

### Using DigitalOcean Domains (Recommended)
If your domain is registered elsewhere but you want to use DigitalOcean DNS:

1. **Add Domain to DigitalOcean**:
   ```bash
   # Using doctl CLI (if installed)
   doctl compute domain create meatscentral.com --ip-address 167.99.155.140
   ```

2. **Update Nameservers at Registrar**:
   - Point to DigitalOcean nameservers:
     - `ns1.digitalocean.com`
     - `ns2.digitalocean.com`
     - `ns3.digitalocean.com`

3. **Configure Records in DigitalOcean**:
   ```bash
   # Add A record
   doctl compute domain records create meatscentral.com --record-type A --record-name @ --record-data 167.99.155.140 --record-ttl 300
   
   # Add www A record
   doctl compute domain records create meatscentral.com --record-type A --record-name www --record-data 167.99.155.140 --record-ttl 300
   ```

### Using DigitalOcean API
If you want to automate DNS setup:

```python
import requests

# Example API call (requires API token)
url = "https://api.digitalocean.com/v2/domains/meatscentral.com/records"
headers = {
    "Authorization": "Bearer YOUR_DO_API_TOKEN",
    "Content-Type": "application/json"
}
data = {
    "type": "A",
    "name": "@",
    "data": "167.99.155.140",
    "ttl": 300
}
response = requests.post(url, headers=headers, json=data)
```

## Testing DNS Configuration

### 1. Basic Connectivity Test
```bash
# Test if domain resolves
ping meatscentral.com

# Test HTTP connectivity (after deployment)
curl -I http://meatscentral.com
```

### 2. Comprehensive DNS Check
```bash
# Check all record types
dig meatscentral.com ANY

# Check from specific DNS server
dig @8.8.8.8 meatscentral.com A
dig @1.1.1.1 meatscentral.com A
```

### 3. HTTP/HTTPS Testing
```bash
# Test HTTP (port 80)
curl -v http://meatscentral.com

# Test HTTPS (port 443) - after SSL setup
curl -v https://meatscentral.com

# Test with custom resolve (bypass DNS)
curl -H "Host: meatscentral.com" http://167.99.155.140
```

## Next Steps After DNS Setup

1. **Wait for Propagation** (at least 15 minutes)
2. **Run Deployment Script** - DNS checks will now pass
3. **Test External Access** - Try accessing your domain from different networks
4. **Set Up SSL Certificate** - For HTTPS access
5. **Configure Monitoring** - Set up uptime monitoring for your domain

## Troubleshooting Commands

```bash
# Clear local DNS cache (Linux)
sudo systemctl flush-dns

# Clear local DNS cache (Mac)
sudo dscacheutil -flushcache

# Clear local DNS cache (Windows)
ipconfig /flushdns

# Check DNS propagation status
curl -s "https://dns.google/resolve?name=meatscentral.com&type=A" | jq

# Test from multiple locations
for server in 8.8.8.8 1.1.1.1 208.67.222.222; do
    echo "Testing from $server:"
    dig @$server +short A meatscentral.com
done
```

## Support

If you encounter issues:

1. **Check DNS Status**: Use online tools like dnschecker.org
2. **Verify Configuration**: Double-check A records point to 167.99.155.140
3. **Wait for Propagation**: DNS changes can take up to 48 hours
4. **Test Different Networks**: Try accessing from mobile data vs WiFi
5. **Contact Provider Support**: If DNS records appear correct but don't resolve

## Security Considerations

- Use low TTL values (300 seconds) during initial setup for faster changes
- Increase TTL to 3600+ seconds once configuration is stable
- Consider using Cloudflare for DDoS protection and CDN benefits
- Set up CAA records if using SSL certificates