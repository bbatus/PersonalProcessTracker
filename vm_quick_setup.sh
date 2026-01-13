#!/bin/bash

# Personal Process Tracker - VM Quick Setup
# Bu script VM'de tek komutla tüm setup'ı yapar

set -e

echo "🚀 Personal Process Tracker - Quick Setup"
echo "=========================================="
echo ""

# Renk kodları
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Hata yakalama
trap 'echo -e "${RED}❌ Hata oluştu! Script durduruluyor.${NC}"; exit 1' ERR

# Root kontrolü
if [ "$EUID" -eq 0 ]; then 
    echo -e "${RED}❌ Bu script'i root olarak çalıştırmayın!${NC}"
    exit 1
fi

echo -e "${YELLOW}📦 Sistem güncelleniyor...${NC}"
sudo apt-get update -qq

# Git kontrolü ve kurulumu
if ! command -v git &> /dev/null; then
    echo -e "${YELLOW}📦 Git kuruluyor...${NC}"
    sudo apt-get install -y git
    echo -e "${GREEN}✅ Git kuruldu${NC}"
else
    echo -e "${GREEN}✅ Git zaten kurulu${NC}"
fi

# Docker kontrolü ve kurulumu
if ! command -v docker &> /dev/null; then
    echo -e "${YELLOW}📦 Docker kuruluyor...${NC}"
    sudo apt-get install -y docker.io docker-compose
    sudo systemctl start docker
    sudo systemctl enable docker
    sudo usermod -aG docker $USER
    echo -e "${GREEN}✅ Docker kuruldu${NC}"
    echo -e "${YELLOW}⚠️  Docker grubuna eklendi. Değişikliklerin geçerli olması için logout/login yapın.${NC}"
else
    echo -e "${GREEN}✅ Docker zaten kurulu${NC}"
fi

# Proje dizini kontrolü
PROJECT_DIR="$HOME/personal-process-tracker"
if [ -d "$PROJECT_DIR" ]; then
    echo -e "${YELLOW}📁 Proje dizini mevcut. Güncelleniyor...${NC}"
    cd "$PROJECT_DIR"
    git pull
else
    echo -e "${YELLOW}📥 Proje GitHub'dan clone ediliyor...${NC}"
    git clone https://github.com/bbatus/personal-process-tracker.git "$PROJECT_DIR"
    cd "$PROJECT_DIR"
fi

echo -e "${GREEN}✅ Proje hazır: $PROJECT_DIR${NC}"
echo ""

# .env dosyası kontrolü
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚙️  .env dosyası oluşturuluyor...${NC}"
    cat > .env << 'EOF'
# Database
DB_PASSWORD=change_this_password

# JWT Secret (değiştir!)
JWT_SECRET=change_this_to_a_random_32_character_string

# Email Configuration
EMAIL_USERNAME=your-email@gmail.com
EMAIL_PASSWORD=your-gmail-app-password
EMAIL_FROM=your-email@gmail.com

# Google OAuth (opsiyonel)
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
GOOGLE_REDIRECT_URI=http://localhost:8001/api/auth/google/callback

# CORS Origins
CORS_ORIGINS=http://localhost:3000

# Frontend API URL
NEXT_PUBLIC_API_URL=http://localhost:8001
EOF
    echo -e "${GREEN}✅ .env dosyası oluşturuldu${NC}"
    echo -e "${RED}⚠️  DİKKAT: .env dosyasındaki değerleri düzenlemeyi unutma!${NC}"
    echo -e "${YELLOW}   nano .env${NC}"
else
    echo -e "${GREEN}✅ .env dosyası mevcut${NC}"
fi

echo ""
echo -e "${YELLOW}🐳 Docker image'ları indiriliyor...${NC}"
docker compose pull

echo ""
echo -e "${YELLOW}🔨 Servisler build ediliyor ve başlatılıyor...${NC}"
docker compose up -d --build

echo ""
echo -e "${YELLOW}⏳ Servislerin başlaması bekleniyor...${NC}"
sleep 10

echo ""
echo -e "${YELLOW}🗄️  Veritabanı migration'ları çalıştırılıyor...${NC}"
docker compose exec -T backend alembic upgrade head

echo ""
echo -e "${YELLOW}📦 Kategoriler seed ediliyor...${NC}"
docker compose exec -T backend python seed_categories.py

echo ""
echo -e "${YELLOW}👤 Test kullanıcısı oluşturuluyor...${NC}"
docker compose exec -T backend python create_test_user.py

echo ""
echo -e "${GREEN}=========================================="
echo "✅ Setup tamamlandı!"
echo "==========================================${NC}"
echo ""
echo -e "${GREEN}📊 Servis Durumu:${NC}"
docker compose ps
echo ""
echo -e "${GREEN}🌐 Erişim Bilgileri:${NC}"
echo "   Frontend: http://$(curl -s ifconfig.me):3000"
echo "   Backend API: http://$(curl -s ifconfig.me):8001"
echo "   API Docs: http://$(curl -s ifconfig.me):8001/docs"
echo ""
echo -e "${GREEN}👤 Test Kullanıcısı:${NC}"
echo "   Email: test@example.com"
echo "   Password: Test123!"
echo ""
echo -e "${YELLOW}📝 Sonraki Adımlar:${NC}"
echo "   1. .env dosyasını düzenle: nano .env"
echo "   2. Servisleri yeniden başlat: docker compose restart"
echo "   3. Firewall kurallarını ayarla (local'den):"
echo "      gcloud compute firewall-rules create allow-ppt --allow tcp:3000,tcp:8001"
echo ""
echo -e "${YELLOW}📚 Faydalı Komutlar:${NC}"
echo "   - Logları izle: docker compose logs -f"
echo "   - Servisleri yeniden başlat: docker compose restart"
echo "   - Güncel kodu çek: git pull && docker compose up -d --build"
echo "   - Backup al: docker compose exec db pg_dump -U ppt_user personal_process_tracker > backup.sql"
echo ""
