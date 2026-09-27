# Cari Takip Gold — yayımlanan parametreler

Bu depoda tek bir dosya var: **`params.json`**. Uygulama bu dosyayı ayda bir
okuyor ve içindeki değerleri kendi içinde gömülü olanların üzerine yazıyor.
Böylece vergi ya da enflasyon rakamı değiştiğinde mağaza güncellemesi
gerekmiyor.

Bu depo **herkese açık** olmalı; uygulamanın kodu ayrı ve özel depoda duruyor.
Dosyada kişisel hiçbir veri yok, sadece kamuya açık rakamlar.

Uygulamanın okuduğu adres:

```
https://raw.githubusercontent.com/hgonullu/cari-takip-parametreler/main/params.json
```

## Dosyada neler var

- `years` — her vergi yılı için: konut kira istisnası, götürü gider oranı,
  gelir vergisi tarifesi, tapu harcı ve emlakçı oranları, mevduat stopajı,
  KKDF ve BSMV. Kaynak: GİB.
- `inflation.tuik` — TÜİK yıllık enflasyonu (`annual_percent`) ve kira artış
  tavanı (`rent_cap_percent`, 12 aylık ortalama).
- `inflation.enag` — ENAG yıllık enflasyonu. Kira tavanı yoktur, kanun TÜİK'e
  bağlı.
- `period` — rakamın ait olduğu ay (`YYYY-MM`). Uygulama bunu ekranda
  gösteriyor, kullanıcı verinin ne kadar güncel olduğunu görüyor.

## Her ay ne yapmak gerekiyor

**TÜİK: hiçbir şey.** `update-tuik.yml` işi her ayın 4'ünde çalışıp TCMB'nin
EVDS servisinden rakamı okuyor ve dosyaya yazıyor. Bir kerelik kurulum:

1. [evds2.tcmb.gov.tr](https://evds2.tcmb.gov.tr) adresinden ücretsiz hesap
   açıp API anahtarını alın (profil sayfasında "API Anahtarı").
2. Bu deponun **Settings → Secrets and variables → Actions → New repository
   secret** bölümüne `EVDS_API_KEY` adıyla yazın.
3. **Actions** sekmesinden işi bir kez elle çalıştırıp (Run workflow) sonucu
   görün.

İş, rakam bir önceki aya göre değişmediyse dosyaya dokunmuyor; rakam gerçek
olamayacak kadar büyük çıkarsa dosyayı değiştirmeden hata veriyor. Yani bozuk
bir rakamın uygulamaya ulaşma yolu yok.

**ENAG: ayda bir, tek sayı.** ENAG rakamını makineyle almak güvenli değil —
siteleri doğrudan erişimi engelliyor, X hesabı giriş istiyor, haber siteleri de
bazen yıllık enflasyon yerine çekirdek enflasyonu yazıyor. Bu yüzden elle:

1. [x.com/ENAGRUP](https://x.com/ENAGRUP) hesabından ayın rakamına bakın
   (**yıllık** E-TÜFE, aylık olan değil).
2. `params.json` içindeki `inflation.enag` bölümünü güncelleyin:

```json
"enag": { "annual_percent": 49.03, "period": "2026-08" }
```

3. Değişikliği kaydedin (GitHub'ın kalem simgesiyle doğrudan tarayıcıdan
   düzenleyebilirsiniz). Birkaç dakika içinde yayına girer.

**Vergi değerleri: yılda bir, Ocak ayında.** Yeni yılın rakamları Resmî
Gazete'de yayımlanınca `years` dizisine yeni bir yıl ekleyin. Eski yılları
silmeyin: geçmiş tarihli bir hesap onları kullanıyor.

## Bir şeyi bozarsam ne olur

Uygulama dosyayı temkinli okuyor:

- Dosya yoksa, bozuksa ya da internet yoksa uygulamanın içindeki değerler
  kullanılır.
- JSON geçersizse ya da dosya 64 KB'den büyükse hiç okunmaz.
- Bir yıl kaydı eksik veya tutarsızsa o yıl atlanır, diğerleri uygulanır.
- Son başarılı okuma telefonda saklanır; çevrimdışı açılışta o kullanılır.

Yani hatalı bir düzenleme uygulamayı bozmaz, sadece etkisiz kalır. Yine de
kaydetmeden önce JSON'un geçerli olduğunu kontrol etmek iyi olur:

```bash
python3 -m json.tool params.json > /dev/null && echo "geçerli"
```
