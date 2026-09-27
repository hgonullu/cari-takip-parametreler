# Cari Takip Gold — yayımlanan parametreler

Bu depoda tek bir dosya var: **`params.json`**. Uygulama bu dosyayı ayda bir
okuyor ve içindeki değerleri kendi içinde gömülü olanların üzerine yazıyor.
Böylece vergi ya da enflasyon rakamı değiştiğinde mağaza güncellemesi
gerekmiyor.

Bu depo **herkese açık** olmalı; uygulamanın kodu ayrı ve özel depoda duruyor.
Dosyada kişisel hiçbir veri yok, sadece kamuya açık rakamlar.

Uygulamanın okuduğu adres:

```
https://api.github.com/repos/hgonullu/cari-takip-parametreler/contents/params.json
```

(GitHub'ın `raw.githubusercontent.com` adresi dosyayı beş dakika önbellekte
tutuyor ve bunu aşmanın yolu yok; API adresi bir dakika tutuyor. Bu yüzden
API adresi kullanılıyor.)

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

Ayda bir, iki sayı. Toplam iki dakika.

1. **TÜİK:** [TÜİK enflasyon haberi](https://data.tuik.gov.tr) ya da herhangi bir
   haber kaynağından ayın rakamlarına bakın. İki rakam lazım:
   - **yıllık enflasyon** (manşet rakam) → `annual_percent`
   - **12 aylık ortalama** (kira artış tavanı olarak duyurulur) → `rent_cap_percent`
2. **ENAG:** [x.com/ENAGRUP](https://x.com/ENAGRUP) hesabından **yıllık** E-TÜFE
   rakamını alın (aylık olanı değil) → `annual_percent`
3. `params.json` dosyasını GitHub'da kalem simgesiyle açıp `inflation` bölümünü
   güncelleyin, `period` alanlarına ayı yazın:

```json
"inflation": {
  "tuik": { "annual_percent": 31.51, "rent_cap_percent": 31.79, "period": "2026-08" },
  "enag": { "annual_percent": 49.03, "period": "2026-08" }
}
```

4. Kaydedin. Birkaç dakika içinde yayına girer; telefonlardaki uygulama en geç
   bir ay içinde (ya da kullanıcı Ayarlar'dan isterse hemen) alır.

Bir ay atlanırsa bir şey bozulmaz: uygulamada eski tarih görünür, kullanıcı
verinin ne kadar güncel olduğunu zaten ekranda görür.

**Vergi değerleri: yılda bir, Ocak ayında.** Yeni yılın rakamları Resmî
Gazete'de yayımlanınca `years` dizisine yeni bir yıl ekleyin. Eski yılları
silmeyin: geçmiş tarihli bir hesap onları kullanıyor.

### Otomatik güncelleme neden yok

`update_tuik.py` ve `.github/workflows/update-tuik.yml` dosyaları TÜİK
rakamını TCMB'nin EVDS servisinden otomatik yazmak için hazırlandı, ama EVDS
GitHub'ın sunucularından gelen her isteği — anahtar başlıkta da adreste de
gönderilse — veri yerine kendi web sayfasıyla cevapladı. Anahtarın reddedilmesi
mi, yurt dışı erişimin engellenmesi mi olduğu dışarıdan ayırt edilemiyor.

Dosyalar duruyor ve elle çalıştırılabilir (Actions → Run workflow). Aylık
zamanlama bilerek kaldırıldı: her ay hata veren bir iş, kimsenin bakmadığı bir
iş hâline gelir.

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
