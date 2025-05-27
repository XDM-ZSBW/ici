# ProtonMail Email Gateway Configuration

## Environment Variables for Cloud Run

Set these environment variables in your Cloud Run service:

```bash
# ProtonMail API Configuration
PROTONMAIL_API_KEY=your_protonmail_api_key_here
PROTONMAIL_SENDER=noreply@your-domain.com

# Admin notification email
ADMIN_EMAIL=admin@your-domain.com

# Optional: Request timestamp for logging
REQUEST_TIMESTAMP=auto_generated
```

## Cloud Run Deployment

### Option 1: Using gcloud CLI
```bash
gcloud run deploy ici-chat \
  --source . \
  --platform managed \
  --region us-central1 \
  --set-env-vars PROTONMAIL_API_KEY=your_key,ADMIN_EMAIL=admin@example.com
```

### Option 2: Using cloudbuild.yaml
```yaml
# Add to your existing cloudbuild.yaml
steps:
  - name: 'gcr.io/cloud-builders/gcloud'
    args:
      - 'run'
      - 'deploy'
      - 'ici-chat'
      - '--image'
      - 'gcr.io/$PROJECT_ID/ici-chat'
      - '--platform=managed'
      - '--region=us-central1'
      - '--set-env-vars=PROTONMAIL_API_KEY=$$PROTONMAIL_API_KEY,ADMIN_EMAIL=$$ADMIN_EMAIL'
    secretEnv: ['PROTONMAIL_API_KEY']

availableSecrets:
  secretManager:
    - versionName: projects/$PROJECT_ID/secrets/protonmail-api-key/versions/latest
      env: 'PROTONMAIL_API_KEY'
```

## ProtonMail API Setup

1. **Get ProtonMail API Access**
   - Sign up for ProtonMail Business/Professional
   - Contact ProtonMail support for API access
   - Generate API credentials

2. **Alternative: ProtonMail Bridge**
   - Install Bridge on a Compute Engine VM
   - Use SMTP connection from Cloud Run to VM
   - More complex but works with personal accounts

## Security Considerations

- ✅ **End-to-end encryption**: ProtonMail maintains encryption
- ✅ **API keys**: Store in Google Secret Manager
- ✅ **Network security**: Cloud Run to ProtonMail over HTTPS
- ✅ **Data minimization**: Only send necessary notification data

## Testing

Test email functionality locally:
```bash
# Set environment variables
export PROTONMAIL_API_KEY="your_test_key"
export ADMIN_EMAIL="test@example.com"

# Run the app
python app_http.py
```

## Benefits for ICI Chat

1. **Privacy-focused**: ProtonMail's zero-access encryption
2. **Compliance**: GDPR/HIPAA friendly email provider
3. **Reliability**: Enterprise-grade email delivery
4. **Integration**: Perfect for Cloud Run serverless architecture
