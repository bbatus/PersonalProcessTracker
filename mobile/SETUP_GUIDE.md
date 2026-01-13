# iOS Mobil Uygulama Kurulum Rehberi

## 🎯 Durum: Xcode Build Hazır! ✅

CocoaPods başarıyla kuruldu ve tüm konfigürasyon dosyaları oluşturuldu.

## ✅ Tamamlanan Adımlar

1. ✅ CocoaPods kuruldu (Homebrew ile)
2. ✅ npm bağımlılıkları yüklendi (minimal set)
3. ✅ iOS klasörü oluşturuldu
4. ✅ Metro bundler başlatıldı (process ID: 3)
5. ✅ Backend URL ayarlandı (192.168.1.153:8000)
6. ✅ `pod install` başarıyla tamamlandı
7. ✅ Workspace dosyası oluşturuldu
8. ✅ Tüm CocoaPods konfigürasyon dosyaları hazır

## 📱 Şimdi Xcode'da Build Alın

### Adım 1: Xcode'u Kapat ve Yeniden Aç
Eğer Xcode açıksa, **tamamen kapatın** (Cmd+Q).

### Adım 2: Workspace Dosyasını Açın
```bash
open mobile/ios/PersonalProcessTrackerTemp.xcworkspace
```

**ÖNEMLİ:** `.xcworkspace` dosyasını açın, `.xcodeproj` değil!

### Adım 3: Scheme ve Device Seçimi
1. Xcode'un üst kısmında scheme seçiciye bakın
2. "PersonalProcessTrackerTemp" scheme'ini seçin
3. Yanındaki device menüsünden iPhone'unuzu seçin

**Eğer scheme görünmüyorsa:**
- Product → Scheme → Manage Schemes
- "Autocreate Schemes Now" butonuna tıklayın
- "PersonalProcessTrackerTemp" scheme'ini seçin ve "Shared" kutusunu işaretleyin

### Adım 4: Signing Ayarları
1. Sol panelde "PersonalProcessTrackerTemp" projesine tıklayın
2. "Signing & Capabilities" sekmesine gidin
3. "Team" dropdown'ından Apple ID'nizi seçin
4. Bundle Identifier'ı değiştirin: `com.batuhan.ppt` (veya benzersiz bir isim)

### Adım 5: Build!
▶️ Play butonuna basın veya Cmd+R

## 🔧 Backend Bağlantısı

`.env` dosyası ayarlı:
```
API_URL=http://192.168.1.193:8000
```

**Önemli:** iPhone ve Mac aynı WiFi'de olmalı!

## 📦 Mevcut Kütüphaneler

Şu an minimal bir kurulum var:
- ✅ React Native 0.76.6 (core)
- ✅ Zustand (state management)
- ✅ Hermes (JavaScript engine)

**Kaldırılan kütüphaneler** (codegen uyumsuzluğu nedeniyle):
- ❌ Navigation libraries
- ❌ AsyncStorage
- ❌ DateTimePicker
- ❌ NetInfo
- ❌ MMKV
- ❌ Reanimated
- ❌ Config
- ❌ FastImage
- ❌ Haptic Feedback
- ❌ Notifee

## 🚀 Sonraki Adımlar

Build başarılı olduktan sonra:

1. **Kütüphaneleri Tek Tek Ekleyin:**
   ```bash
   npm install @react-navigation/native
   cd ios && pod install
   ```
   Her ekleme sonrası test edin.

2. **Uyumsuz Kütüphaneler İçin Alternatif Bulun:**
   - Bazı kütüphaneler React Native 0.76.6 ile uyumlu olmayabilir
   - Daha yeni versiyonlarını veya alternatiflerini araştırın

## 🐛 Sorun Giderme

**Build butonu hala gri ise:**
- Xcode'u tamamen kapatıp yeniden açın
- Workspace dosyasını açtığınızdan emin olun
- Scheme'in seçili olduğunu kontrol edin
- Device'ın seçili olduğunu kontrol edin

**"No signing certificate" hatası:**
- Xcode → Settings → Accounts → Apple ID ekleyin
- Signing & Capabilities'de Team seçin

**Metro bundler hatası:**
- Terminal'de: `cd mobile && npm start -- --reset-cache`
