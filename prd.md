Product Requirements Document (PRD)
Personal Process Tracker - Life Manager System

1. Project Overview
1.1 Product Name
Personal Process Tracker (PPT) / Life Manager
1.2 Vision Statement
Tamamen lokal, kişiye özel bir yaşam yönetim sistemi. Kullanıcının günlük görevlerini, hedeflerini, alışkanlıklarını ve kişisel gelişimini takip etmesini sağlayan, "kendine karşı accountability" sunan bir platform.
1.3 Target User

Primary: Batuhan (self-manager, DevOps/Backend developer)
Secondary: Kişisel gelişime önem veren, sistemli çalışmak isteyen bireyler
Kullanıcı Sayısı: Tek kullanıcı (v1.0), çok kullanıcılı yapıya genişletilebilir

1.4 Success Metrics

Günlük login oranı: %80+
Görev tamamlama oranı: %70+
Sistem uptime: %99.9 (lokal)
Aylık retrospective tamamlama: %100


2. Technical Architecture
2.1 Tech Stack
LayerTechnologyRationaleFrontendNext.js 14+ (App Router)SSR, routing, modern ReactUI FrameworkTailwind CSSHızlı geliştirme, responsiveChartsRecharts / Chart.jsGörselleştirmeBackendFastAPI (Python 3.11+)Batuhan'ın uzmanlık alanıDatabasePostgreSQL 15+Relational data, güçlü queryingAuthJWT (optional for v1.0)Gelecekte multi-user hazırlığıContainerizationDocker + Docker ComposeKolay deploy, izolasyonOrchestrationKubernetes (optional v2.0)DevOps practice
2.2 System Architecture
┌─────────────────────────────────────────────┐
│          Frontend (Next.js)                 │
│  - Dashboard                                │
│  - Task Manager                             │
│  - Goals & Habits                           │
│  - Analytics                                │
└──────────────┬──────────────────────────────┘
               │ HTTP/REST API
               ▼
┌─────────────────────────────────────────────┐
│          Backend (FastAPI)                  │
│  - Authentication                           │
│  - CRUD Operations                          │
│  - Business Logic                           │
│  - Analytics Engine                         │
└──────────────┬──────────────────────────────┘
               │ SQL
               ▼
┌─────────────────────────────────────────────┐
│       Database (PostgreSQL)                 │
│  - Users, Tasks, Goals                      │
│  - Habits, Logs, Summaries                  │
└─────────────────────────────────────────────┘
2.3 Deployment

Lokal: Docker Compose ile tek komutta ayağa kalkma
Network: Localhost only (port expose yok)
Data: Volume mount ile persist


3. Core Modules & Features
3.1 Module 1: Authentication & User Management
Features

 User login/logout
 Session management (JWT optional)
 User settings (timezone, preferences)
 Profile management

User Stories
AS A user
I WANT TO login securely
SO THAT only I can access my personal data

AS A user
I WANT TO customize my dashboard
SO THAT I see the metrics that matter to me

3.2 Module 2: Daily Task Management
Features

 Task CRUD (Create, Read, Update, Delete)
 Task status: Pending → Done → Skipped
 Task categories: Work, Sport, Personal, Learning
 Task postpone (bugün → yarın)
 Task notes
 Daily view & weekly view

Data Model
pythonTask:
  - id: UUID
  - title: String (max 200 char)
  - description: Text (optional)
  - category: Enum(WORK, SPORT, PERSONAL, LEARNING)
  - status: Enum(PENDING, DONE, SKIPPED)
  - scheduled_date: Date
  - completed_at: DateTime (nullable)
  - user_id: FK → User
```

#### UI Mockup Concept
```
📅 12 Ocak 2026, Pazar
─────────────────────────────────
☑ Kubernetes concepts çalış      [Work]
☐ 30 dk koşu                      [Sport]
☑ 20 İngilizce kelime             [Learning]
☐ Blog post yaz                   [Personal]

[+ Yeni Görev Ekle]

3.3 Module 3: Goals & Targets
Features

 Goal creation (daily, weekly, monthly, yearly)
 Goal tracking (progress %)
 Goal deadline warnings
 Automatic calculation (task completion → goal progress)

Data Model
pythonGoal:
  - id: UUID
  - title: String
  - description: Text
  - period: Enum(DAILY, WEEKLY, MONTHLY, YEARLY)
  - target_count: Integer (kaç kez yapılmalı)
  - current_count: Integer (şu ana kadar)
  - start_date: Date
  - end_date: Date
  - category: FK → Category (optional)
```

#### Examples
```
🎯 Ocak 2026 Hedefleri
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Kubernetes orta seviye bitir    [▓▓▓▓▓░░░░░] 50%
15 gün spor yap                  [▓▓▓▓░░░░░░] 40% (6/15)
10 teknik makale oku             [▓▓▓▓▓▓▓░░░] 70% (7/10)

3.4 Module 4: Habit Tracker
Features

 Habit definition (name, frequency)
 Streak tracking (21-day rule)
 Habit completion calendar (visual)
 Break warnings ("3 gün üst üste miss → alert")

Data Model
pythonHabit:
  - id: UUID
  - name: String
  - frequency: Enum(DAILY, WEEKLY)
  - target_days: Integer (per week)
  - current_streak: Integer
  - longest_streak: Integer
  - last_completed: Date

HabitLog:
  - habit_id: FK
  - completed_date: Date
  - notes: Text (optional)
```

#### UI Concept
```
🔥 Günlük Spor
Current Streak: 12 gün 🔥
Longest: 18 gün

Ocak 2026
Su Mo Tu We Th Fr Sa
          ✓  ✓  ✓  ✓
✓  ✓  ✗  ✓  ✓  ✓  ✓
```

---

### 3.5 Module 5: Analytics & Dashboard

#### Features
- [x] Daily completion rate
- [x] Weekly trends (line chart)
- [x] Monthly summary (bar chart)
- [x] Category breakdown (pie chart)
- [x] Most completed / most skipped tasks
- [x] Productivity heatmap (GitHub-style)

#### Metrics
```
📊 Bu Ay (Ocak 2026)
━━━━━━━━━━━━━━━━━━━━━━━━━━━
Görev Tamamlama: 78%
Spor Günleri: 9/15
En Çok Yapılan: Kubernetes çalışma (12 kez)
En Çok Atlanan: Blog yazma (5 kez)
Charts

Line Chart: Günlük başarı oranı (son 30 gün)
Bar Chart: Kategori bazlı task dağılımı
Heatmap: GitHub-style aktivite takvimi


3.6 Module 6: Monthly Retrospective
Features

 Ay sonu notları
 "Ne iyi gitti?" / "Ne kötü gitti?" / "Neyi değiştirmeliyim?"
 Mood tracking (optional)
 AI-generated insights (v2.0)

Data Model
pythonMonthlySummary:
  - id: UUID
  - month: Date (YYYY-MM)
  - success_rate: Float
  - total_tasks: Integer
  - completed_tasks: Integer
  - what_went_well: Text
  - what_went_bad: Text
  - what_to_change: Text
  - average_mood: Float (1-10)

4. Database Schema
4.1 Core Tables
sql-- Users
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Categories
CREATE TABLE categories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(50) NOT NULL,
    color VARCHAR(7) -- hex color
);

-- Tasks
CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    category_id UUID REFERENCES categories(id),
    title VARCHAR(200) NOT NULL,
    description TEXT,
    status VARCHAR(20) DEFAULT 'PENDING',
    scheduled_date DATE NOT NULL,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Goals
CREATE TABLE goals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    category_id UUID REFERENCES categories(id),
    title VARCHAR(200) NOT NULL,
    description TEXT,
    period VARCHAR(20) NOT NULL, -- DAILY, WEEKLY, MONTHLY, YEARLY
    target_count INTEGER NOT NULL,
    current_count INTEGER DEFAULT 0,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Habits
CREATE TABLE habits (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    frequency VARCHAR(20) NOT NULL, -- DAILY, WEEKLY
    target_days INTEGER, -- per week for WEEKLY
    current_streak INTEGER DEFAULT 0,
    longest_streak INTEGER DEFAULT 0,
    last_completed DATE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Habit Logs
CREATE TABLE habit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    habit_id UUID REFERENCES habits(id) ON DELETE CASCADE,
    completed_date DATE NOT NULL,
    notes TEXT,
    UNIQUE(habit_id, completed_date)
);

-- Monthly Summaries
CREATE TABLE monthly_summaries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    month DATE NOT NULL, -- YYYY-MM-01
    success_rate DECIMAL(5,2),
    total_tasks INTEGER,
    completed_tasks INTEGER,
    what_went_well TEXT,
    what_went_bad TEXT,
    what_to_change TEXT,
    average_mood DECIMAL(3,1),
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, month)
);

-- Mood Logs (optional)
CREATE TABLE mood_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    mood_score INTEGER CHECK (mood_score BETWEEN 1 AND 10),
    notes TEXT,
    UNIQUE(user_id, date)
);
```

---

## 5. API Endpoints (FastAPI)

### 5.1 Authentication
```
POST   /api/auth/register      # Kayıt
POST   /api/auth/login         # Giriş
POST   /api/auth/logout        # Çıkış
GET    /api/auth/me            # Current user
```

### 5.2 Tasks
```
GET    /api/tasks              # List (query: date, status, category)
POST   /api/tasks              # Create
GET    /api/tasks/{id}         # Detail
PUT    /api/tasks/{id}         # Update
DELETE /api/tasks/{id}         # Delete
PATCH  /api/tasks/{id}/status  # Mark done/pending
PATCH  /api/tasks/{id}/postpone # Erteleme
```

### 5.3 Goals
```
GET    /api/goals              # List
POST   /api/goals              # Create
GET    /api/goals/{id}         # Detail
PUT    /api/goals/{id}         # Update
DELETE /api/goals/{id}         # Delete
GET    /api/goals/{id}/progress # Progress detail
```

### 5.4 Habits
```
GET    /api/habits             # List
POST   /api/habits             # Create
GET    /api/habits/{id}        # Detail
PUT    /api/habits/{id}        # Update
DELETE /api/habits/{id}        # Delete
POST   /api/habits/{id}/log    # Log completion
GET    /api/habits/{id}/streak # Streak info
```

### 5.5 Analytics
```
GET    /api/analytics/daily            # Günlük özet
GET    /api/analytics/weekly           # Haftalık trend
GET    /api/analytics/monthly/{month}  # Aylık özet
GET    /api/analytics/heatmap          # Aktivite takvimi
```

### 5.6 Retrospective
```
GET    /api/retrospective/{month}      # Aylık retro
POST   /api/retrospective              # Create/Update retro
```

---

## 6. UI/UX Requirements

### 6.1 Design Principles
- **Minimal & Clean**: Dikkat dağıtmayan, focus-friendly
- **Dark Mode First**: Göz yormayan tasarım
- **Mobile Responsive**: Telefonda da kullanılabilir
- **Fast Loading**: < 1 second page load

### 6.2 Key Screens

#### 1. Dashboard (Ana Sayfa)
```
┌─────────────────────────────────────────┐
│  📊 Dashboard         [12 Ocak 2026]   │
├─────────────────────────────────────────┤
│  Bugün                                  │
│  ☑ 3/5 görev tamamlandı (60%)          │
│  🔥 Spor streak: 12 gün                │
│                                         │
│  Bu Hafta                               │
│  ▓▓▓▓▓▓▓░░░ 72% completion             │
│                                         │
│  [Line Chart: Son 30 gün trend]        │
│                                         │
│  Yaklaşan Hedefler                      │
│  • Kubernetes bitir (5 gün kaldı)      │
│  • Aylık spor hedefi (6/15)            │
└─────────────────────────────────────────┘
```

#### 2. Task Manager
```
┌─────────────────────────────────────────┐
│  📅 Görevlerim        [+ Yeni Ekle]    │
├─────────────────────────────────────────┤
│  [Bugün] [Yarın] [Bu Hafta] [Hepsi]   │
│                                         │
│  ☑ Kubernetes çalış          [Work]    │
│     Tamamlandı: 10:30                   │
│                                         │
│  ☐ 30 dk koşu                [Sport]   │
│     [Tamamla] [Ertele] [Sil]           │
│                                         │
│  ☐ Blog post yaz             [Personal]│
│     Deadline: 2 gün kaldı               │
└─────────────────────────────────────────┘
```

#### 3. Goals & Habits
```
┌─────────────────────────────────────────┐
│  🎯 Hedefler & Alışkanlıklar           │
├─────────────────────────────────────────┤
│  Aylık Hedefler (Ocak 2026)            │
│                                         │
│  Kubernetes bitir                       │
│  ▓▓▓▓▓░░░░░ 50% (5 gün kaldı)         │
│                                         │
│  15 gün spor                            │
│  ▓▓▓▓░░░░░░ 40% (6/15 gün)            │
│                                         │
│  ─────────────────────────────────────  │
│                                         │
│  Alışkanlıklar                          │
│                                         │
│  🔥 Günlük Spor                         │
│  Current: 12 gün | Best: 18 gün        │
│  [Bugün Tamamlandı ✓]                  │
│                                         │
│  📚 Günlük Okuma                        │
│  Current: 3 gün | Best: 7 gün          │
│  [Bugün Yap]                            │
└─────────────────────────────────────────┘
```

#### 4. Analytics
```
┌─────────────────────────────────────────┐
│  📊 İstatistikler                      │
├─────────────────────────────────────────┤
│  [Bu Ay] [Son 3 Ay] [Bu Yıl]          │
│                                         │
│  Ocak 2026 Özeti                        │
│  • Başarı Oranı: 78%                   │
│  • Toplam Görev: 89                     │
│  • Tamamlanan: 69                       │
│  • Atlanan: 20                          │
│                                         │
│  [Line Chart: Günlük completion rate]  │
│                                         │
│  Kategori Dağılımı                      │
│  [Pie Chart]                            │
│  • Work: 45%                            │
│  • Sport: 25%                           │
│  • Learning: 20%                        │
│  • Personal: 10%                        │
│                                         │
│  [Heatmap: GitHub-style calendar]      │
└─────────────────────────────────────────┘
```

#### 5. Monthly Retrospective
```
┌─────────────────────────────────────────┐
│  📝 Aylık Değerlendirme - Ocak 2026    │
├─────────────────────────────────────────┤
│  Başarı Oranı: 78%                      │
│  Ortalama Ruh Hali: 7.5/10              │
│                                         │
│  ✅ Ne İyi Gitti?                       │
│  [Kubernetes'i sistematik çalıştım,     │
│   spor alışkanlığı oturdu...]           │
│                                         │
│  ❌ Ne Kötü Gitti?                      │
│  [Blog yazmayı ihmal ettim, hafta       │
│   sonları düzensizdi...]                │
│                                         │
│  🔄 Şubat'ta Değiştirilecekler          │
│  [Hafta sonu planlaması yapacağım,      │
│   blog için özel slot...]               │
│                                         │
│  [Kaydet]                               │
└─────────────────────────────────────────┘

7. Non-Functional Requirements
7.1 Performance

API response time: < 200ms (local)
Page load: < 1s
Database query optimization (indexing)

7.2 Security

Password hashing: bcrypt (min 12 rounds)
JWT expiration: 24 hours
SQL injection prevention (ORM usage)
CORS: localhost only

7.3 Reliability

Database backup: Daily (automated)
Error logging: Structured logging (JSON)
Graceful degradation (offline mode v2.0)

7.4 Scalability

Database: Ready for 10,000+ tasks per user
API: Pagination (default 50 items)
Image/file support: Future-proof (v2.0)


8. Development Phases
Phase 1: MVP (4 weeks)
Goal: Temel CRUD + Authentication + Dashboard

 Week 1: Setup (Docker, DB, FastAPI boilerplate, Next.js setup)
 Week 2: Authentication + Task CRUD
 Week 3: Dashboard + Basic analytics
 Week 4: UI polish + Testing

Deliverables:

Login/logout
Task create/read/update/delete
Günlük task listesi
Basit dashboard (completion rate)


Phase 2: Core Features (4 weeks)
Goal: Goals + Habits + Advanced Analytics

 Week 5-6: Goals module
 Week 7: Habit tracker
 Week 8: Advanced analytics (charts, heatmap)

Deliverables:

Hedef takibi
Alışkanlık streak sistemi
Görsel grafikler


Phase 3: Polish & Extras (2 weeks)
Goal: Retrospective + UX improvements + Extras

 Week 9: Monthly retrospective
 Week 10: Mood tracker, focus timer (optional)

Deliverables:

Ay sonu değerlendirme
Ekstra modüller


Phase 4: Production Ready (2 weeks)
Goal: Testing + Documentation + Deployment

 Week 11: Unit tests + Integration tests
 Week 12: Documentation + Docker Compose final

Deliverables:

README.md
API documentation (Swagger)
Deploy kılavuzu


9. Future Enhancements (v2.0)
9.1 Advanced Features

 AI Insights: "Bu ay spor günlerin azaldı, sebep ne olabilir?"
 Pomodoro Timer: Task'e timer bağlama
 Calendar Integration: Google Calendar sync
 Mobile App: React Native
 Collaboration: Çoklu kullanıcı (arkadaşlarla goal sharing)

9.2 Technical Improvements

 Kubernetes Deployment: K8s cluster'da çalıştırma
 CI/CD: GitHub Actions
 Monitoring: Prometheus + Grafana
 Offline Mode: PWA support


10. Success Criteria
For Batuhan

 Günlük kullanım: 30+ gün streak
 Portfolio projesi olarak kullanılabilir
 Mülakatta "gerçek kullandığım sistem" diyebilmek
 DevOps + Backend + Frontend pratiği

Technical

 Test coverage: > 70%
 API documentation: %100 complete
 Docker setup: Tek komutta çalışır
 Database migrations: Versiyon kontrolü


11. Risks & Mitigations
RiskProbabilityImpactMitigationScope creep (fazla özellik)HighHighMVP odaklı kal, v2.0'a erteleMotivasyon kaybıMediumHigh2 haftada bir demo, küçük kazanımlarDatabase design hatasıMediumMediumSchema review, migration planningUI/UX karmaşıklığıLowMediumTailwind + shadcn/ui kullan

12. Appendix
12.1 References

FastAPI docs: https://fastapi.tiangolo.com
Next.js docs: https://nextjs.org/docs
PostgreSQL best practices: https://wiki.postgresql.org

12.2 Glossary

Streak: Art arda başarılı gün sayısı
Retrospective: Geçmiş dönem değerlendirmesi
Habit: Düzenli tekrarlanan aktivite
Goal: Belirli sürede ulaşılması hedeflenen başarım


Document Control
VersionDateAuthorChanges1.02026-01-10ClaudeInitial PRD

Son Not: Bu PRD, proje boyunca "living document" olarak güncellenecek. Her sprint sonunda revize edilmeli.