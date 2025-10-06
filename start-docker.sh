#!/bin/bash

# Look@Me CMS - Docker Startup Script

set -e

echo "🚀 Avvio Look@Me CMS con Docker..."
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker non è installato. Installa Docker prima di continuare."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose non è installato. Installa Docker Compose prima di continuare."
    exit 1
fi

echo "✅ Docker e Docker Compose sono installati"
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  File .env non trovato. Uso configurazione di default."
    echo "   Per configurare le API keys social, copia .env.docker in .env"
    echo ""
fi

# Stop any existing containers
echo "🛑 Arresto eventuali container esistenti..."
docker-compose down 2>/dev/null || true
echo ""

# Build and start containers
echo "🔨 Build e avvio dei container..."
docker-compose up -d --build
echo ""

# Wait for services to be ready
echo "⏳ Attendo che i servizi siano pronti..."
sleep 10

# Check service health
echo "🏥 Verifica stato servizi:"
echo ""

if curl -f http://localhost:8001/api/health &> /dev/null; then
    echo "✅ Backend: ONLINE (http://localhost:8001)"
else
    echo "❌ Backend: OFFLINE"
fi

if curl -f http://localhost:3000 &> /dev/null; then
    echo "✅ Frontend: ONLINE (http://localhost:3000)"
else
    echo "❌ Frontend: OFFLINE"
fi

if docker exec lookatme-mongodb mongosh --eval "db.adminCommand('ping')" &> /dev/null; then
    echo "✅ MongoDB: ONLINE"
else
    echo "❌ MongoDB: OFFLINE"
fi

echo ""
echo "🎉 Look@Me CMS è pronto!"
echo ""
echo "📍 Accedi all'applicazione:"
echo "   Frontend: http://localhost:3000"
echo "   Backend API: http://localhost:8001"
echo "   API Docs: http://localhost:8001/docs"
echo ""
echo "📋 Comandi utili:"
echo "   Visualizza logs: docker-compose logs -f"
echo "   Ferma servizi: docker-compose down"
echo "   Riavvia servizi: docker-compose restart"
echo ""
echo "📖 Per maggiori informazioni, consulta DOCKER_DEPLOY.md"
echo ""