#!/bin/bash
#
# Deployment script for Invoice Resolver AI
# Supports Docker Compose with Traefik or Fly.io
#
# Usage:
#   ./deploy.sh [options]
#
# Options:
#   --staging       Deploy to staging environment
#   --production    Deploy to production (requires confirmation)
#   --fly           Deploy using Fly.io instead of Docker Compose
#   --backup        Create database backup before deploying
#   --no-build      Skip Docker image rebuild
#   --help          Show this help message
#
# Examples:
#   ./deploy.sh --production              # Full production deploy with backup
#   ./deploy.sh --staging --no-build      # Quick staging deploy without rebuild
#   ./deploy.sh --fly --production        # Deploy to Fly.io production

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
APP_NAME="invoice-resolver-ai"
DOCKER_COMPOSE_PROD="docker-compose.prod.yml"
DOCKER_COMPOSE_TRAEFIK="docker-compose.traefik.yml"
FLY_APP="invoice-resolver-ai"
BACKUP_DIR="./backups"
ENV_FILE=".env"

# Default flags
STAGING=false
PRODUCTION=false
FLY=false
BACKUP=false
BUILD=true

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --staging)
            STAGING=true
            shift
            ;;
        --production)
            PRODUCTION=true
            shift
            ;;
        --fly)
            FLY=true
            shift
            ;;
        --backup)
            BACKUP=true
            shift
            ;;
        --no-build)
            BUILD=false
            shift
            ;;
        --help)
            grep "^#" "$0" | cut -c4-
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Validate arguments
if [ "$STAGING" = true ] && [ "$PRODUCTION" = true ]; then
    echo -e "${RED}Error: Cannot specify both --staging and --production${NC}"
    exit 1
fi

if [ "$STAGING" = false ] && [ "$PRODUCTION" = false ] && [ "$FLY" = false ]; then
    echo -e "${YELLOW}No environment specified. Defaulting to staging.${NC}"
    STAGING=true
fi

# Check prerequisites
echo -e "${BLUE}=== Prerequisites Check ===${NC}"

if [ "$FLY" = false ]; then
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}Docker is not installed${NC}"
        exit 1
    fi
    if ! command -v docker-compose &> /dev/null; then
        echo -e "${RED}Docker Compose is not installed${NC}"
        exit 1
    fi
else
    if ! command -v flyctl &> /dev/null; then
        echo -e "${RED}flyctl is not installed${NC}"
        echo "Install with: curl -L https://fly.io/install.sh | sh"
        exit 1
    fi
    if ! flyctl auth whoami &> /dev/null; then
        echo -e "${RED}Not logged in to Fly.io${NC}"
        echo "Run: flyctl login"
        exit 1
    fi
fi

echo -e "${GREEN}✓ Prerequisites satisfied${NC}"

# Ensure .env exists
if [ ! -f "$ENV_FILE" ]; then
    echo -e "${YELLOW}No .env file found. Copying from .env.example...${NC}"
    cp .env.example .env
    echo -e "${RED}⚠️  Please edit .env and add required secrets before deploying!${NC}"
    read -p "Press Enter to continue or Ctrl+C to abort..."
fi

if [ "$FLY" = false ]; then
    # Docker Compose deployment

    echo -e "${BLUE}=== Docker Compose Deployment ===${NC}"

    # Create backup if requested
    if [ "$BACKUP" = true ]; then
        echo -e "${BLUE}Creating database backup...${NC}"
        mkdir -p "$BACKUP_DIR"
        TIMESTAMP=$(date +%Y%m%d_%H%M%S)
        docker-compose -f "$DOCKER_COMPOSE_PROD" exec -T postgres pg_dump -U postgres invoice_resolver > "$BACKUP_DIR/backup_${TIMESTAMP}.sql" 2>/dev/null || {
            echo -e "${RED}Backup failed!${NC}"
            exit 1
        }
        echo -e "${GREEN}✓ Backup created: $BACKUP_DIR/backup_${TIMESTAMP}.sql${NC}"
    fi

    # Build images if requested
    if [ "$BUILD" = true ]; then
        echo -e "${BLUE}Building Docker images...${NC}"
        docker-compose -f "$DOCKER_COMPOSE_PROD" build --no-cache api celery-worker

        if [ $? -ne 0 ]; then
            echo -e "${RED}Build failed!${NC}"
            exit 1
        fi
        echo -e "${GREEN}✓ Build successful${NC}"
    fi

    # Determine which compose files to use
    COMPOSE_FILES="-f $DOCKER_COMPOSE_PROD"
    if [ "$PRODUCTION" = true ]; then
        COMPOSE_FILES="$COMPOSE_FILES -f $DOCKER_COMPOSE_TRAEFIK"
    fi

    # Stop and remove existing containers
    echo -e "${BLUE}Stopping existing services...${NC}"
    docker-compose $COMPOSE_FILES down

    # Start services
    echo -e "${BLUE}Starting services...${NC}"
    docker-compose $COMPOSE_FILES up -d

    # Wait for services to be healthy
    echo -e "${BLUE}Waiting for services to be healthy...${NC}"
    sleep 10

    # Check API health
    API_URL="http://localhost:8000/health"
    if [ "$PRODUCTION" = true ]; then
        API_DOMAIN=${API_DOMAIN:-api.local}
        API_URL="https://$API_DOMAIN/health"
    fi

    echo -e "${BLUE}Checking health endpoint: $API_URL${NC}"
    for i in {1..30}; do
        if curl -f "$API_URL" >/dev/null 2>&1; then
            echo -e "${GREEN}✓ API is healthy${NC}"
            break
        fi
        echo -n "."
        sleep 2
        if [ $i -eq 30 ]; then
            echo -e "${RED}✗ API health check failed${NC}"
            docker-compose $COMPOSE_FILES logs api
            exit 1
        fi
    done

    # Run database migrations
    echo -e "${BLUE}Running database migrations...${NC}"
    docker-compose $COMPOSE_FILES exec api alembic upgrade head || {
        echo -e "${RED}Migrations failed!${NC}"
        docker-compose $COMPOSE_FILES logs api
        exit 1
    }
    echo -e "${GREEN}✓ Migrations applied${NC}"

    # Show service status
    echo -e "${BLUE}Service Status:${NC}"
    docker-compose $COMPOSE_FILES ps

    echo -e "${GREEN}=== Deployment Complete ===${NC}"
    if [ "$PRODUCTION" = true ]; then
        echo -e "API: https://${API_DOMAIN}"
        echo -e "Dashboard: https://${DASHBOARD_DOMAIN}"
        echo -e "Docs: https://${API_DOMAIN}/docs"
    else
        echo -e "API: http://localhost:8000"
        echo -e "Dashboard: http://localhost:8501"
        echo -e "Docs: http://localhost:8000/docs"
    fi

else
    # Fly.io deployment
    echo -e "${BLUE}=== Fly.io Deployment ===${NC}"

    # Create backup if requested (requires external DB access)
    if [ "$BACKUP" = true ]; then
        echo -e "${YELLOW}Backup skipped for Fly.io (use external DB backup mechanism)${NC}"
    fi

    # Determine environment
    if [ "$STAGING" = true ]; then
        FLY_APP="${FLY_APP}-staging"
        echo -e "${YELLOW}Deploying to staging app: $FLY_APP${NC}"
    else
        echo -e "${RED}⚠️  Deploying to PRODUCTION${NC}"
        read -p "Are you sure? (yes/no): " CONFIRM
        if [ "$CONFIRM" != "yes" ]; then
            echo "Deployment cancelled"
            exit 1
        fi
    fi

    # Deploy
    echo -e "${BLUE}Deploying to Fly.io...${NC}"
    flyctl --app "$FLY_APP" deploy --remote-only

    if [ $? -ne 0 ]; then
        echo -e "${RED}Deployment failed!${NC}"
        exit 1
    fi

    # Run migrations
    echo -e "${BLUE}Running database migrations...${NC}"
    flyctl --app "$FLY_APP" ssh console -C "alembic upgrade head" || {
        echo -e "${RED}Migrations failed!${NC}"
        exit 1
    }

    echo -e "${GREEN}=== Fly.io Deployment Complete ===${NC}"
    flyctl --app "$FLY_APP" open
fi

echo -e "${GREEN}✅ All done!${NC}"
