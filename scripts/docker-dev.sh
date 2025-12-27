#!/bin/bash
# Docker development helper script

case "$1" in
  start)
    echo "🚀 Starting TaskFlow development environment..."
    docker-compose up -d
    echo "✅ Services started!"
    echo "   Backend: http://localhost:8000"
    echo "   Admin: http://localhost:8000/admin"
    ;;
  
  stop)
    echo "🛑 Stopping TaskFlow..."
    docker-compose down
    ;;
  
  restart)
    echo "🔄 Restarting TaskFlow..."
    docker-compose restart
    ;;
  
  logs)
    if [ -z "$2" ]; then
      docker-compose logs -f
    else
      docker-compose logs -f $2
    fi
    ;;
  
  shell)
    docker-compose exec backend bash
    ;;
  
  django-shell)
    docker-compose exec backend python manage.py shell
    ;;
  
  migrate)
    echo "🗄️  Running migrations..."
    docker-compose exec backend python manage.py makemigrations
    docker-compose exec backend python manage.py migrate
    ;;
  
  test)
    echo "🧪 Running tests..."
    docker-compose exec backend pytest
    ;;
  
  superuser)
    docker-compose exec backend python manage.py createsuperuser
    ;;
  
  clean)
    echo "🧹 Cleaning up Docker resources..."
    docker-compose down -v
    docker system prune -f
    echo "✅ Cleanup complete!"
    ;;
  
  rebuild)
    echo "🏗️  Rebuilding containers..."
    docker-compose build --no-cache
    docker-compose up -d
    ;;
  
  *)
    echo "TaskFlow Docker Helper"
    echo ""
    echo "Usage: ./scripts/docker-dev.sh [command]"
    echo ""
    echo "Commands:"
    echo "  start       - Start all services"
    echo "  stop        - Stop all services"
    echo "  restart     - Restart all services"
    echo "  logs [svc]  - View logs (optional: specify service)"
    echo "  shell       - Open bash in backend container"
    echo "  django-shell - Open Django shell"
    echo "  migrate     - Run database migrations"
    echo "  test        - Run test suite"
    echo "  superuser   - Create Django superuser"
    echo "  clean       - Remove all containers and volumes"
    echo "  rebuild     - Rebuild images from scratch"
    ;;
esac