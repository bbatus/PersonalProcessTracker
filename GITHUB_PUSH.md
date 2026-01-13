# 🚀 GitHub'a Push Etme Rehberi

## İlk Kez Push (Yeni Repo)

### 1. GitHub'da Repo Oluştur
1. https://github.com/new adresine git
2. Repository name: `personal-process-tracker`
3. Description: `Personal productivity tracking system`
4. Public veya Private seç
5. **Initialize this repository with a README seçme** (zaten var)
6. "Create repository" tıkla

### 2. Local'de Git Başlat ve Push Et
```bash
# Git repository'si başlat (henüz yoksa)
git init

# Tüm dosyaları ekle
git add .

# İlk commit
git commit -m "Initial commit: Personal Process Tracker with Docker deployment"

# Ana branch'i main yap
git branch -M main

# Remote ekle (GitHub username'ini değiştir)
git remote add origin https://github.com/bbatus/personal-process-tracker.git

# Push et
git push -u origin main
```

---

## Sonraki Push'lar (Güncellemeler)

```bash
# Değişiklikleri kontrol et
git status

# Tüm değişiklikleri ekle
git add .

# Commit et (açıklayıcı mesaj yaz)
git commit -m "Update: açıklama buraya"

# Push et
git push
```

---

## Faydalı Git Komutları

### Durum Kontrolü
```bash
# Değişiklikleri gör
git status

# Commit geçmişi
git log --oneline

# Son 5 commit
git log --oneline -5

# Değişiklikleri detaylı gör
git diff
```

### Branch Yönetimi
```bash
# Yeni branch oluştur
git checkout -b feature/yeni-ozellik

# Branch'ler arası geçiş
git checkout main

# Branch'leri listele
git branch

# Branch'i push et
git push -u origin feature/yeni-ozellik

# Branch'i sil
git branch -d feature/yeni-ozellik
```

### Geri Alma
```bash
# Son commit'i geri al (değişiklikler kalır)
git reset --soft HEAD~1

# Son commit'i tamamen geri al
git reset --hard HEAD~1

# Belirli dosyayı geri al
git checkout -- dosya.txt

# Tüm değişiklikleri geri al
git reset --hard
```

### Remote Yönetimi
```bash
# Remote'ları listele
git remote -v

# Remote ekle
git remote add origin https://github.com/bbatus/personal-process-tracker.git

# Remote değiştir
git remote set-url origin https://github.com/bbatus/personal-process-tracker.git

# Remote'dan çek
git pull
```

---

## .gitignore Kontrol

Hassas dosyaların push edilmediğinden emin ol:

```bash
# .gitignore'u kontrol et
cat .gitignore

# Şunlar ignore edilmeli:
# - .env
# - node_modules/
# - __pycache__/
# - venv/
# - .DS_Store
```

---

## GitHub Actions (CI/CD) - Opsiyonel

`.github/workflows/deploy.yml` oluştur:

```yaml
name: Deploy to VM

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to VM
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.VM_HOST }}
          username: ${{ secrets.VM_USER }}
          key: ${{ secrets.VM_SSH_KEY }}
          script: |
            cd ~/personal-process-tracker
            git pull
            docker compose up -d --build
            docker compose exec -T backend alembic upgrade head
```

GitHub Secrets ekle:
- `VM_HOST`: VM'in IP adresi
- `VM_USER`: SSH kullanıcı adı
- `VM_SSH_KEY`: SSH private key

---

## Commit Mesajı Standartları

İyi commit mesajları yaz:

```bash
# ✅ İyi örnekler
git commit -m "Add: User authentication with JWT"
git commit -m "Fix: Database connection timeout issue"
git commit -m "Update: Docker compose configuration for production"
git commit -m "Refactor: Task service for better performance"

# ❌ Kötü örnekler
git commit -m "update"
git commit -m "fix bug"
git commit -m "changes"
```

### Commit Mesajı Prefixleri
- `Add:` - Yeni özellik
- `Fix:` - Bug düzeltme
- `Update:` - Mevcut özellik güncelleme
- `Refactor:` - Kod iyileştirme
- `Remove:` - Kod/özellik silme
- `Docs:` - Dokümantasyon
- `Test:` - Test ekleme/güncelleme
- `Style:` - Kod formatı
- `Chore:` - Bakım işleri

---

## Hızlı Komutlar

### Tek Satırda Add, Commit, Push
```bash
git add . && git commit -m "Update: mesaj" && git push
```

### Alias Oluştur (Kısayollar)
```bash
# ~/.gitconfig veya ~/.zshrc'ye ekle
alias gs='git status'
alias ga='git add .'
alias gc='git commit -m'
alias gp='git push'
alias gl='git log --oneline'
alias gpl='git pull'

# Kullanım
gs              # git status
ga              # git add .
gc "mesaj"      # git commit -m "mesaj"
gp              # git push
```

---

## Troubleshooting

### Push Reddedilirse
```bash
# Remote'daki değişiklikleri çek
git pull --rebase

# Çakışmaları çöz (varsa)
# Sonra push et
git push
```

### Yanlış Commit'i Düzelt
```bash
# Son commit mesajını değiştir
git commit --amend -m "Yeni mesaj"

# Force push (dikkatli kullan!)
git push --force
```

### Büyük Dosya Hatası
```bash
# Git LFS kur
git lfs install

# Büyük dosyaları track et
git lfs track "*.psd"
git lfs track "*.zip"

# .gitattributes'u commit et
git add .gitattributes
git commit -m "Add: Git LFS configuration"
```

---

## GitHub'da Yapılacaklar

### 1. Repository Settings
- Description ekle
- Topics ekle: `productivity`, `task-management`, `docker`, `fastapi`, `nextjs`
- Website URL ekle (varsa)

### 2. README Badge'leri Ekle
```markdown
![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=flat&logo=docker&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=flat&logo=fastapi)
![Next.js](https://img.shields.io/badge/Next.js-black?style=flat&logo=next.js&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/postgres-%23316192.svg?style=flat&logo=postgresql&logoColor=white)
```

### 3. Branch Protection (Opsiyonel)
Settings → Branches → Add rule:
- Require pull request reviews
- Require status checks to pass

---

## Özet: İlk Push

```bash
# 1. GitHub'da repo oluştur
# 2. Local'de:
git init
git add .
git commit -m "Initial commit: Personal Process Tracker"
git branch -M main
git remote add origin https://github.com/bbatus/personal-process-tracker.git
git push -u origin main

# 3. VM'de:
curl -fsSL https://raw.githubusercontent.com/bbatus/personal-process-tracker/main/vm_quick_setup.sh | bash
```

Hepsi bu kadar! 🎉
