#!/bin/bash
# Production secrets initialization script
# Run this script before starting docker-compose.prod.yml for the first time

set -e

SECRETS_DIR="./secrets"

echo "🔐 Initializing production secrets..."

# Create secrets directory if it doesn't exist
mkdir -p "$SECRETS_DIR"

# Generate random passwords and keys
generate_secret() {
    local file=$1
    local length=${2:-32}
    if [ ! -f "$SECRETS_DIR/$file" ]; then
        openssl rand -base64 $length | tr -d '\n' > "$SECRETS_DIR/$file"
        chmod 600 "$SECRETS_DIR/$file"
        echo "✓ Generated $file"
    else
        echo "✗ $file already exists, skipping"
    fi
}

# Generate required secrets
generate_secret "postgres_password.txt" 32
generate_secret "jwt_secret.txt" 64
generate_secret "stripe_webhook_secret.txt" 32
generate_secret "paypal_client_secret.txt" 32
generate_secret "openai_api_key.txt"  # You'll need to set this manually
generate_secret "redis_password.txt" 32
generate_secret "grafana_admin_password.txt" 32

echo ""
echo "⚠️  IMPORTANT: You must manually set the following secrets:"
echo "   - secrets/openai_api_key.txt (your actual OpenAI API key)"
echo "   - secrets/paypal_client_secret.txt (if using PayPal)"
echo ""
echo "You can change the generated Grafana admin password in:"
echo "   secrets/grafana_admin_password.txt"
echo ""
echo "Copy .env.example to .env and fill in non-secret environment variables:"
echo "   cp .env.example .env"
echo ""
echo "Then start the production stack:"
echo "   docker-compose -f docker-compose.prod.yml up -d"
echo ""
echo "✅ Secrets initialization complete!"
