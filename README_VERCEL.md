# Twitter Blockchain Content Bot - Vercel Deployment

Bu bot otomatik olarak blockchain projeleri hakkında analitik içerik oluşturur ve Twitter'da paylaşır.

## Vercel'e Deploy Etme Adımları

### 1. GitHub Repository Hazırlama

Aşağıdaki dosyaları GitHub repository'nize yükleyin:

**Ana dosyalar:**
- `app.py` (Ana Flask uygulaması)
- `vercel.json` (Vercel konfigürasyonu)
- `requirements_vercel.txt` (Python bağımlılıkları - bunu requirements.txt olarak yeniden adlandırın)

**Bot bileşenleri:**
- `content_generator.py`
- `twitter_client.py`
- `database_vercel.py`
- `projects_data.py`
- `utils.py`

**Frontend:**
- `templates/index.html`
- `static/style.css`

### 2. Vercel'de Proje Oluşturma

1. Vercel'e gidin ve GitHub hesabınızı bağlayın
2. "New Project" butonuna tıklayın
3. GitHub repository'nizi seçin
4. "Deploy" butonuna tıklayın

### 3. Environment Variables Ekleme

Vercel dashboard'da projenize gidin ve Settings > Environment Variables'a gidin. Aşağıdaki değişkenleri ekleyin:

```
GEMINI_API_KEY=your_gemini_api_key_here
TWITTER_API_KEY=your_twitter_api_key_here
TWITTER_API_SECRET=your_twitter_api_secret_here
TWITTER_ACCESS_TOKEN=your_twitter_access_token_here
TWITTER_ACCESS_TOKEN_SECRET=your_twitter_access_token_secret_here
TWITTER_BEARER_TOKEN=your_twitter_bearer_token_here
```

### 4. Otomatik Tweet Atmak İçin Cron Job Kurma

Bot'un otomatik olarak çalışması için harici bir cron servis kullanmanız gerekiyor:

#### Seçenek 1: Cron-job.org (Ücretsiz)
1. https://cron-job.org sitesine gidin
2. Hesap oluşturun
3. Yeni cron job ekleyin:
   - URL: `https://your-vercel-app.vercel.app/api/cron`
   - Schedule: `0 */3 * * *` (Her 3 saatte bir)

#### Seçenek 2: EasyCron (Ücretsiz plan)
1. https://www.easycron.com sitesine gidin
2. Hesap oluşturun
3. Yeni cron job ekleyin:
   - URL: `https://your-vercel-app.vercel.app/api/cron`
   - Schedule: `0 */3 * * *`

#### Seçenek 3: GitHub Actions (Tamamen ücretsiz)

Repository'nizde `.github/workflows/cron.yml` dosyası oluşturun:

```yaml
name: Auto Tweet Bot
on:
  schedule:
    - cron: '0 */3 * * *'  # Her 3 saatte bir
  workflow_dispatch:  # Manuel tetikleme için

jobs:
  post-tweet:
    runs-on: ubuntu-latest
    steps:
      - name: Call Vercel endpoint
        run: |
          curl -X POST https://your-vercel-app.vercel.app/api/cron
```

### 5. Manuel Test

Deploy edildikten sonra şu URL'leri test edin:

- Ana dashboard: `https://your-vercel-app.vercel.app/`
- Manuel tweet: `https://your-vercel-app.vercel.app/api/generate`
- Bot durumu: `https://your-vercel-app.vercel.app/api/status`

### Önemli Notlar

- Bot ilk deploy'dan sonra hemen çalışmaya başlar
- Cron job kurulmadığı sürece sadece manuel tetikleme ile çalışır
- Twitter API limitlerini otomatik olarak yönetir
- Her 3.5 saatte bir farklı bir blockchain projesi hakkında içerik üretir

### Sorun Giderme

Eğer bot çalışmıyorsa:
1. Vercel dashboard'da Functions sekmesinden log'ları kontrol edin
2. Environment variables'ların doğru girildiğinden emin olun
3. API anahtarlarının geçerli olduğunu kontrol edin

## Bot Özellikleri

- 25 farklı blockchain projesi
- Gemini AI ile analitik içerik üretimi
- Otomatik Twitter thread'leri
- Rate limit yönetimi
- Web dashboard ile monitoring