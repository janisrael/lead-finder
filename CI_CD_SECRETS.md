# Lead Finder - CI/CD Secrets and Variables

This document lists all required GitHub Actions secrets and environment variables for deploying Lead Finder to Hetzner Kubernetes.

---

## GitHub Actions Secrets

Add these secrets in your GitHub repository settings: **Settings → Secrets and variables → Actions**

### Required Secrets

| Secret Name | Description | Example Value | Required |
|------------|-------------|---------------|----------|
| `HETZNER_SSH_PRIVATE_KEY` | SSH private key for Hetzner server access | `-----BEGIN OPENSSH PRIVATE KEY-----...` | ✅ Yes |
| `HETZNER_HOST` | Hetzner server IP address | `178.156.162.135` | ✅ Yes |
| `GOOGLE_PLACES_API_KEY` | Google Places API key for location searches | `AIzaSy...` | ✅ Yes |
| `FLASK_SECRET_KEY` | Flask secret key for session security (generate with `openssl rand -hex 32`) | `a1b2c3d4e5f6...` | ✅ Yes |

### Optional Secrets

| Secret Name | Description | Example Value | Required |
|------------|-------------|---------------|----------|
| `HETZNER_APP_URL` | Application URL for health checks | `https://leadfinder.janisrael.com` | ❌ No |

---

## Kubernetes Secrets

These will be created automatically by the CI/CD workflow or can be created manually:

### Secret: `leadfinder-secrets`

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: leadfinder-secrets
  namespace: leadfinder
type: Opaque
stringData:
  secret-key: "CHANGE_THIS_TO_A_RANDOM_SECRET_KEY"
  flask-env: "production"
  port: "5000"
  google-places-api-key: "YOUR_GOOGLE_PLACES_API_KEY"
  debug: "false"
```

**To create manually:**
```bash
kubectl create secret generic leadfinder-secrets \
  --from-literal=secret-key='your-secret-key-here' \
  --from-literal=flask-env='production' \
  --from-literal=port='5000' \
  --from-literal=google-places-api-key='your-google-places-api-key' \
  --from-literal=debug='false' \
  -n leadfinder \
  --dry-run=client -o yaml | kubectl apply -f -
```

---

## Environment Variables

### Application Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `PORT` | Application port | `6005` (local), `5000` (Docker) | ❌ No |
| `DEBUG` | Flask debug mode | `False` | ❌ No |
| `GOOGLE_PLACES_API_KEY` | Google Places API key | None | ✅ Yes |
| `FLASK_ENV` | Flask environment | `production` | ❌ No |
| `SECRET_KEY` | Flask secret key | None | ✅ Yes (for production) |

### Database Configuration

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `DB_PATH` | SQLite database path | `places.db` | ❌ No |

---

## Setup Instructions

### 1. GitHub Actions Secrets

1. Go to your GitHub repository
2. Navigate to **Settings → Secrets and variables → Actions**
3. Click **New repository secret**
4. Add each secret listed above

### 2. Google Places API Key

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing project
3. Enable **Places API**
4. Create credentials (API Key)
5. Restrict the API key to **Places API** only
6. Add the key to GitHub Secrets as `GOOGLE_PLACES_API_KEY`

### 3. Hetzner SSH Key

1. Generate SSH key pair (if not exists):
   ```bash
   ssh-keygen -t ed25519 -C "github-actions" -f ~/.ssh/hetzner_deploy
   ```

2. Copy public key to Hetzner server:
   ```bash
   ssh-copy-id -i ~/.ssh/hetzner_deploy.pub root@178.156.162.135
   ```

3. Copy private key content:
   ```bash
   cat ~/.ssh/hetzner_deploy
   ```

4. Add to GitHub Secrets as `HETZNER_SSH_PRIVATE_KEY` (include BEGIN/END lines)

### 4. Verify Secrets

After adding secrets, verify they're set correctly:
- Go to **Settings → Secrets and variables → Actions**
- All secrets should be listed
- Values are hidden (showing only `••••••••`)

---

## CI/CD Workflow Variables

The workflow uses these variables automatically:

| Variable | Value | Description |
|----------|-------|-------------|
| `PYTHON_VERSION` | `3.11` | Python version for tests |
| `GITHUB_TOKEN` | Auto-provided | GitHub API token |
| `GITHUB_REF` | Auto-provided | Git branch reference |

---

## Security Best Practices

1. **Never commit secrets** to the repository
2. **Rotate secrets regularly** (especially API keys)
3. **Use least privilege** for API keys (restrict to specific APIs/IPs)
4. **Monitor API usage** in Google Cloud Console
5. **Use separate API keys** for development and production
6. **Enable API key restrictions** in Google Cloud Console

---

## Troubleshooting

### Secret Not Found Error
- Verify secret name matches exactly (case-sensitive)
- Check secret is added to the correct repository
- Ensure workflow has permission to read secrets

### API Key Invalid Error
- Verify API key is correct in GitHub Secrets
- Check API key restrictions in Google Cloud Console
- Ensure Places API is enabled for the project

### SSH Connection Failed
- Verify SSH key format (must include BEGIN/END lines)
- Check Hetzner server IP is correct
- Ensure public key is added to server's `~/.ssh/authorized_keys`

---

## Next Steps

After setting up secrets:
1. Create Kubernetes manifests (deployment, service, ingress)
2. Set up CI/CD workflow file
3. Push to `main` branch to trigger deployment
4. Monitor deployment in GitHub Actions

---

**Last Updated**: 2025-01-08  
**Maintained By**: Jan Francis Israel

