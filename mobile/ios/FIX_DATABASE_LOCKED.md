# ✅ Database Locked Hatası Çözüldü

## Yapılan İşlemler

1. **DerivedData temizlendi:**
   ```bash
   rm -rf ~/Library/Developer/Xcode/DerivedData/PersonalProcessTrackerTemp-*
   ```

2. **Build klasörü temizlendi:**
   ```bash
   cd mobile/ios
   rm -rf build
   ```

3. **CocoaPods yeniden kuruldu:**
   ```bash
   pod deintegrate && pod install
   ```

## ✅ Şimdi Ne Yapmalısın?

### 1. Xcode'u Tamamen Kapat
- Eğer açıksa Cmd+Q ile tamamen kapat

### 2. Workspace'i Aç
```bash
open mobile/ios/PersonalProcessTrackerTemp.xcworkspace
```

### 3. iPhone'u Seç
- Xcode'un üst ortasında cihaz seçiciden iPhone'unu seç
- "Batuhan iPhone" gibi görünecek

### 4. Build ve Run
- ▶️ Play butonuna tıkla VEYA
- Cmd+R tuşlarına bas

## 🎯 Beklenen Sonuç
- Build başarılı olacak
- Uygulama iPhone'a yüklenecek
- Metro bundler otomatik başlayacak
- Uygulama iPhone'da açılacak

## 🐛 Eğer Tekrar Aynı Hata Olursa

```bash
# Xcode'u kapat, sonra:
cd mobile/ios
rm -rf build
rm -rf ~/Library/Developer/Xcode/DerivedData/PersonalProcessTrackerTemp-*
pod install
open PersonalProcessTrackerTemp.xcworkspace
```

## 📝 Not
Bu hata, komut satırından build aldıktan sonra Xcode'dan build almaya çalıştığında oluşur.
Çözüm: DerivedData'yı temizlemek.
