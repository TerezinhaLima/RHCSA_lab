#!/bin/bash

echo "🚀 Configurando ambiente RHCSA V10 Lab"

# Criar ambiente virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt

# Criar arquivo .env se não existir
if [ ! -f .env ]; then
    echo "GROQ_API_KEY=sua_chave_aqui" > .env
    echo "⚠️  Configure sua chave da Groq no arquivo .env"
fi

# Verificar VMs do Vagrant
if command -v vagrant &> /dev/null; then
    echo "✅ Vagrant encontrado"
    vagrant status
else
    echo "❌ Vagrant não instalado"
fi

echo ""
echo "📝 Para iniciar o laboratório:"
echo "1. vagrant up (para iniciar as VMs)"
echo "2. python3 app.py (para iniciar o servidor de dicas)"
echo "3. Abra index.html no navegador"
echo ""
echo "🔗 Acesse: http://localhost:5005 para verificar status do servidor"