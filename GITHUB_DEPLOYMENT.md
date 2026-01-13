# 🚀 GitHub Deployment Guide

## Avantajlar
- ✅ Version control
- ✅ Kolay güncelleme (git pull)
- ✅ VM'de direkt build
- ✅ Daha temiz workflow
- ✅ Collaboration için hazır

---

## 1. GitHub'a Push

### İlk Kurulum
```bash
# Git repository'si oluştur (henüz yoksa)
git init

# .gitignore kontrol et
cat .gitignore

# Tüm dosyaları ekle
git add .

# İlk commit
git commit -m "Initial commit: Personal Process Tracker"

# GitHub'da yeni repo oluştur (github.com'da)
# Sonra remote ekle
git remote add origin https://github.com/bbatus/personal-process-tracker.git

# Push et
git branch -M main
git push -u origin main
```

### Güncelleme (Sonraki Push'lar)
```bash
git add .
git commit -m "Update: açıklama buraya"
git push
```

---

## 2. Google Cloud VM Setup

### VM'e Bağlan
```bash
# SSH ile bağlan
gcloud compute ssh [VM_NAME] --zone=[ZONE]

# veya direkt SSH
ssh [USER]@[VM_IP]
```

### Gerekli Paketleri Kur
```bash
# Sistem güncellemesi
sudo apt-get update

# Git kur
sudo apt-get install -y git

# Docker kur
sudo apt-get install -y docker.io docker-compose

# Docker'ı başlat
sudo systemctl start docker
sudo systemctl enable docker

# Kullanıcıyı docker grubuna ekle
sudo usermod -aG docker $USER

# Logout/login gerekebilir
exit
# Tekrar bağlan
```

### Projeyi Clone Et
```bash
# GitHub'dan clone et
git clone https://github.com/bbatus/personal-process-tracker.git

# Proje dizinine gir
cd personal-process-tracker
```

### Environment Dosyası Oluştur
```bash
# .env dosyası oluştur
nano .env
```

**.env içeriği:**
```env
# Database
DB_PASSWORD=your_secure_password_here

# JWT
JWT_SECRET=your_super_secret_jwt_key_minimum_32_characters

# Email
EMAIL_USERNAME=your-email@gmail.com
EMAIL_PASSWORD=your-gmail-app-password
EMAIL_FROM=your-email@gmail.com

# Google OAuth (opsiyonel)
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
GOOGLE_REDIRECT_URI=http://YOUR_VM_IP:8001/api/auth/google/callback

# CORS (VM'in IP'si ile değiştir)
CORS_ORIGINS=http://YOUR_VM_IP:3000

# Frontend API URL
NEXT_PUBLIC_API_URL=http://YOUR_VM_IP:8001
```

### Docker Compose ile Başlat
```bash
# Build ve başlat
docker compose up -d --build

# Logları izle
docker compose logs -f
```

### Veritabanı Setup
```bash
# Migration'ları çalıştır
docker compose exec backend alembic upgrade head

# Kategorileri seed et
docker compose exec backend python seed_categories.py

# Test kullanıcısı oluştur
docker compose exec backend python create_test_user.py
```

---

## 3. Firewall Kuralları

```bash
# Local terminalden (VM'den çık)
exit

# Firewall kuralı oluştur
gcloud compute firewall-rules create allow-ppt \
    --allow tcp:3000,tcp:8001 \
    --source-ranges 0.0.0.0/0 \
    --description "Allow PPT Frontend and Backend"

# veya sadece belirli IP'lerden
gcloud compute firewall-rules create allow-ppt \
    --allow tcp:3000,tcp:8001 \
    --source-ranges YOUR_IP/32 \
    --description "Allow PPT from specific IP"
```

---

## 4. Test Et

```bash
# VM'in external IP'sini al
gcloud compute instances list

# Browser'da test et:
# Frontend: http://VM_IP:3000
# Backend API Docs: http://VM_IP:8001/docs
# Health Check: http://VM_IP:8001/health

# veya curl ile:
curl http://VM_IP:8001/health
```

---

## 5. Güncelleme (Yeni Kod Push'ladığında)

### Local'de:
```bash
# Değişiklikleri commit et
git add .
git commit -m "Update: yeni özellik"
git push
```

### VM'de:
```bash
# VM'e bağlan
ssh [USER]@[VM_IP]

# Proje dizinine gir
cd personal-process-tracker

# Yeni kodu çek
git pull

# Servisleri yeniden build et ve başlat
docker compose up -d --build

# Logları kontrol et
docker compose logs -f backend frontend

# Eğer migration varsa
docker compose exec backend alembic upgrade head
```

---

## 6. Hızlı Komutlar

### VM'de Sık Kullanılan Komutlar
```bash
# Proje dizinine git
cd ~/personal-process-tracker

# Güncel kodu çek
git pull

# Servisleri yeniden başlat
docker compose restart

# Logları izle
docker compose logs -f

# Container durumları
docker compose ps

# Veritabanı backup
docker compose exec db pg_dump -U ppt_user personal_process_tracker > backup_$(date +%Y%m%d).sql

# Servisleri durdur
docker compose down

# Servisleri başlat
docker compose up -d
```

---

## 7. Monitoring ve Bakım

### Log İzleme
```bash
# Tüm loglar
docker compose logs -f

# Sadece backend
docker compose logs -f backend

# Sadece frontend
docker compose logs -f frontend

# Son 100 satır
docker compose logs --tail=100 backend
```

### Resource Kullanımı
```bash
# Container resource kullanımı
docker stats

# Disk kullanımı
df -h

# Docker disk kullanımı
docker system df
```

### Temizlik
```bash
# Kullanılmayan image'ları temizle
docker image prune -a

# Kullanılmayan volume'ları temizle
docker volume prune

# Tüm sistemi temizle (DİKKAT!)
docker system prune -a --volumes
```

---

## 8. Backup Stratejisi

### Otomatik Backup Script
```bash
# backup.sh oluştur
nano ~/backup.sh
```

```bash
#!/bin/bash
BACKUP_DIR=~/backups
mkdir -p $BACKUP_DIR
DATE=$(date +%Y%m%d_%H%M%S)

cd ~/personal-process-tracker

# Veritabanı backup
docker compose exec -T db pg_dump -U ppt_user personal_process_tracker > $BACKUP_DIR/db_backup_$DATE.sql

# .env dosyası backup
cp .env $BACKUP_DIR/env_backup_$DATE

# Eski backup'ları temizle (30 günden eski)
find $BACKUP_DIR -name "*.sql" -mtime +30 -delete

echo "✅ Backup completed: $DATE"
```

```bash
# Script'i çalıştırılabilir yap
chmod +x ~/backup.sh

# Cron job ekle (her gün saat 02:00)
crontab -e
# Ekle: 0 2 * * * ~/backup.sh
```

---

## 9. SSL/HTTPS (Opsiyonel - Nginx ile)

### Nginx Kurulumu
```bash
sudo apt-get install -y nginx certbot python3-certbot-nginx

# Nginx config
sudo nano /etc/nginx/sites-available/ppt
```

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    location /api {
        proxy_pass http://localhost:8001;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

```bash
# Config'i aktif et
sudo ln -s /etc/nginx/sites-available/ppt /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# SSL sertifikası al
sudo certbot --nginx -d your-domain.com
```

---

## 10. Troubleshooting

### Container Başlamıyorsa
```bash
# Logları kontrol et
docker compose logs backend
docker compose logs frontend

# Container'ı yeniden başlat
docker compose restart backend

# Tamamen yeniden build et
docker compose down
docker compose up -d --build
```

### Veritabanı Bağlantı Hatası
```bash
# PostgreSQL container'ı kontrol et
docker compose ps db

# PostgreSQL logları
docker compose logs db

# Veritabanına bağlan
docker compose exec db psql -U ppt_user -d personal_process_tracker
```

### Port Çakışması
```bash
# Portları kontrol et
sudo netstat -tulpn | grep :3000
sudo netstat -tulpn | grep :8001

# Çakışan process'i durdur
sudo kill -9 [PID]
```

---

## Özet: Tek Komut Setup

```bash
# VM'de çalıştır
curl -fsSL https://raw.githubusercontent.com/bbatus/personal-process-tracker/main/vm_quick_setup.sh | bash
```

(Bu script'i oluşturacağız)
