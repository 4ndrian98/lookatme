#!/bin/bash

# Look@Me CMS - Docker Stop Script

set -e

echo "🛑 Arresto Look@Me CMS..."
echo ""

# Stop containers
docker-compose down

echo ""
echo "✅ Tutti i servizi sono stati arrestati."
echo ""
echo "💾 I dati MongoDB sono stati preservati nel volume 'mongodb_data'"
echo ""
echo "Per riavviare: ./start-docker.sh"
echo "Per rimuovere anche i dati: docker-compose down -v"
echo ""