"""
Nida Zeytin Video Üretici (Hugging Face Video Generation Engine)
---------------------------------------------------------------
Hugging Face Access Token kullanarak metinden veya görselden video üretir.
Desteklenen modeller / Spaces:
  - Wan2.1 (Wan-AI/Wan2.1-T2V-1.3B)
  - CogVideoX (THUDM/CogVideoX-5b)
  - Text-to-Video Synthesis / Serverless Video Endpoints
"""

import os
import sys
import json
import time
import argparse
import urllib.request
import urllib.error
from pathlib import Path

# .env dosyasından token yükleme desteği
def env_yukle():
    env_yol = Path(__file__).resolve().parent / ".env"
    if env_yol.is_file():
        try:
            with open(env_yol, "r", encoding="utf-8") as f:
                for satir in f:
                    satir = satir.strip()
                    if satir and not satir.startswith("#") and "=" in satir:
                        k, v = satir.split("=", 1)
                        k = k.strip()
                        v = v.strip().strip("'\"")
                        if k and not os.environ.get(k):
                            os.environ[k] = v
        except Exception:
            pass

env_yukle()

HF_TOKEN = os.environ.get("HF_TOKEN") or os.environ.get("HUGGINGFACE_ACCESS_TOKEN") or ""
CIKTI_DIZINI = Path(__file__).resolve().parent / "cikti" / "videolar"

# Varsayılan video üretim modelleri
VARSAYILAN_MODELLER = [
    "Wan-AI/Wan2.1-T2V-1.3B",
    "THUDM/CogVideoX-5b",
    "damo-vilab/text-to-video-ms-1.7b"
]

def video_uret(prompt: str, model: str = None, cikti_adi: str = None, bekleme_suresi: int = 120) -> dict:
    """
    Verilen prompt ile Hugging Face üzerinden video üretir ve cikti/videolar/ dizinine kaydeder.
    """
    if not prompt:
        return {"durum": "hata", "mesaj": "Prompt boş olamaz"}
    if not HF_TOKEN:
        return {"durum": "hata", "mesaj": "HF_TOKEN tanımlı değil (.env veya ortam değişkeni)"}

    model = model or VARSAYILAN_MODELLER[0]
    CIKTI_DIZINI.mkdir(parents=True, exist_ok=True)

    if not cikti_adi:
        zaman_damgasi = int(time.time())
        temiz_baslik = "".join(c if c.isalnum() else "_" for c in prompt[:30]).strip("_")
        cikti_adi = f"video_{zaman_damgasi}_{temiz_baslik}.mp4"

    hedef_dosya = CIKTI_DIZINI / cikti_adi

    api_url = f"https://api-inference.huggingface.co/models/{model}"
    headers = {
        "Authorization": f"Bearer {HF_TOKEN}",
        "Content-Type": "application/json",
        "Accept": "video/mp4, application/json"
    }
    payload = json.dumps({"inputs": prompt}).encode("utf-8")

    print(f"🎬 Video üretimi başlatılıyor...")
    print(f"📌 Model: {model}")
    print(f"📝 Prompt: {prompt}")

    baslangic = time.time()
    req = urllib.request.Request(api_url, data=payload, headers=headers, method="POST")

    try:
        with urllib.request.urlopen(req, timeout=bekleme_suresi) as response:
            content_type = response.headers.get("Content-Type", "")
            data = response.read()

            if "json" in content_type:
                yanit = json.loads(data.decode("utf-8"))
                if "error" in yanit:
                    tahmini = yanit.get("estimated_time", 20)
                    print(f"⏳ Model yükleniyor (tahmini {tahmini:.0f}s), bekleniyor...")
                    time.sleep(min(tahmini, 30))
                    # Tekrar dene
                    return video_uret(prompt, model, cikti_adi, bekleme_suresi)
                return {"durum": "bilgi", "yanit": yanit}

            # Video ikili verisi geldi
            with open(hedef_dosya, "wb") as f:
                f.write(data)

            gecen_sure = round(time.time() - baslangic, 1)
            boyut_kb = round(len(data) / 1024, 1)
            print(f"✅ Video başarıyla kaydedildi: {hedef_dosya} ({boyut_kb} KB, {gecen_sure}s)")
            return {
                "durum": "basarili",
                "dosya": str(hedef_dosya),
                "boyut_kb": boyut_kb,
                "gecen_sure_sn": gecen_sure,
                "model": model,
                "prompt": prompt
            }

    except urllib.error.HTTPError as e:
        hata_govde = e.read().decode("utf-8", errors="ignore")
        try:
            hata_json = json.loads(hata_govde)
            hata_mesaji = hata_json.get("error", str(e))
        except Exception:
            hata_mesaji = hata_govde or str(e)

        print(f"❌ Video üretim hatası ({e.code}): {hata_mesaji}")
        return {
            "durum": "hata",
            "kod": e.code,
            "mesaj": hata_mesaji,
            "model": model
        }
    except Exception as e:
        print(f"❌ Beklenmeyen hata: {e}")
        return {"durum": "hata", "mesaj": str(e)}

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Nida Zeytin Hugging Face Video Üretici")
    parser.add_argument("--prompt", type=str, default="Golden extra virgin olive oil pouring gracefully into a rustic ceramic bowl, sunlight, 4k cinematic slow motion", help="Video üretim promptu")
    parser.add_argument("--model", type=str, default="Wan-AI/Wan2.1-T2V-1.3B", help="Hugging Face model adı")
    parser.add_argument("--cikti", type=str, default=None, help="Çıktı mp4 dosya adı")

    args = parser.parse_args()
    sonuc = video_uret(args.prompt, model=args.model, cikti_adi=args.cikti)
    print(json.dumps(sonuc, indent=2, ensure_ascii=False))
