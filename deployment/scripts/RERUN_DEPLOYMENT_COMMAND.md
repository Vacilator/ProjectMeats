# ProjectMeats Rerun Deployment Command

## Single command to rerun deployment script:

```bash
sudo /opt/projectmeats/one_click_deploy.sh
```

This command will:
- Execute the deployment script with proper sudo privileges
- Automatically handle any permission issues
- Re-run the complete deployment process
- Update all configurations and services

## Alternative using the script wrapper:

```bash
sudo /opt/projectmeats/deployment/scripts/rerun_deployment.sh
```

This wrapper provides:
- Enhanced error checking
- Verification that the script exists and is executable
- Better logging and status messages
- Automatic permission fixes if needed