"""EVREN LLM API (https://evren-llmapi.ssyz.org.tr/v1) istemcisi.

Yalnız Python standart kütüphanesi:
- Kullanım şartları kapısı (/v1/terms/status, /v1/terms/text, /v1/terms/accept)
- Düşünen modeller (deepseek-v4.1-flash, glm-5.3, mimo-v2.6-pro, qwen3.8-flash-next) için max_tokens >= 4096
- SSE akışında `: keep-alive` kalp atışı filtreleme ve `delta.reasoning` / `delta.reasoning_content` ayrıştırma
- 429 / 503 durumlarında `Retry-After` ile otomatik yeniden deneme
- `GET /v1/quota` ve `x-evren-daily-remaining-tokens` ile 15M günlük kota izleme
- Claude Code için Anthropic geçidi (`ANTHROPIC_BASE_URL=https://evren-llmapi.ssyz.org.tr`) ortam hazırlayıcı
"""
import json
import os
import re
import time
import urllib.error
import urllib.request

import ortak  # noqa: F401 (.env yüklemesini garanti eder)

VARSAYILAN_BASE_URL = "https://evren-llmapi.ssyz.org.tr/v1"
ANTHROPIC_GECIT_URL = "https://evren-llmapi.ssyz.org.tr"
VARSAYILAN_MODEL = "deepseek-v4.1-flash"
VARSAYILAN_CEO_MODEL = "glm-5.3"
MAKS_DENEME = 3
ASGAR_MAKS_TOKEN = 4096

# Eski Claude model adlarını EVREN filosuna eşleme
MODEL_ESLEME = {
    "opus": "glm-5.3",
    "sonnet": "deepseek-v4.1-flash",
    "haiku": "qwen3.8-flash-next",
}

_SARTLAR_ONAYLANDI = False
_SON_KALAN_KOTA = None


def api_anahtari():
    return (os.environ.get("EVREN_API_KEY") or os.environ.get("ANTHROPIC_AUTH_TOKEN") or "").strip()


def base_url():
    return (os.environ.get("EVREN_BASE_URL") or VARSAYILAN_BASE_URL).rstrip("/")


def aktif_mi():
    return bool(api_anahtari())


def model_coz(model_adi):
    m = (model_adi or "").strip()
    if not m:
        return os.environ.get("EVREN_DEFAULT_MODEL") or VARSAYILAN_MODEL
    return MODEL_ESLEME.get(m, m)


def _basliklar(anahtar=None):
    k = anahtar or api_anahtari()
    return {
        "Authorization": f"Bearer {k}",
        "X-API-Key": k,
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
        "User-Agent": "NidaZeytin-AjanOfisi/2.0",
    }


def think_kacis(metin):
    """DeepSeek modellerinde <think> ve </think> etiketlerinin düşünmeyi erken bitirmesini önler."""
    if not isinstance(metin, str):
        return ""
    return metin.replace("<think>", "&lt;think&gt;").replace("</think>", "&lt;/think&gt;")


def _kota_basliktan_guncelle(headers):
    global _SON_KALAN_KOTA
    if not headers:
        return
    kalan = headers.get("x-evren-daily-remaining-tokens") or headers.get("X-Evren-Daily-Remaining-Tokens")
    if kalan is not None:
        try:
            _SON_KALAN_KOTA = int(kalan)
        except ValueError:
            pass


def _istek_yap(yontem, yol, veri=None, zaman_asimi=60):
    url = f"{base_url()}/{yol.lstrip('/')}"
    govde = json.dumps(veri, ensure_ascii=False).encode("utf-8") if veri is not None else None
    for deneme in range(MAKS_DENEME):
        req = urllib.request.Request(url, data=govde, headers=_basliklar(), method=yontem)
        try:
            with urllib.request.urlopen(req, timeout=zaman_asimi) as yanit:
                _kota_basliktan_guncelle(yanit.headers)
                ham = yanit.read().decode("utf-8", "replace")
                return json.loads(ham) if ham.strip() else {}
        except urllib.error.HTTPError as e:
            _kota_basliktan_guncelle(e.headers)
            hata_govde = e.read().decode("utf-8", "replace")
            if e.code == 403 and "terms_not_accepted" in hata_govde and not yol.startswith("terms/"):
                if sartlari_onayla(zorla=True):
                    continue
            if e.code in (429, 503) and deneme < MAKS_DENEME - 1:
                bekle = min(int(e.headers.get("Retry-After") or (4 * (deneme + 1))), 60)
                time.sleep(bekle)
                continue
            raise RuntimeError(f"EVREN HTTP {e.code}: {hata_govde[:300]}") from e
        except urllib.error.URLError as e:
            if deneme < MAKS_DENEME - 1:
                time.sleep(2 * (deneme + 1))
                continue
            raise RuntimeError(f"EVREN bağlantı hatası: {e}") from e


def sartlari_onayla(zorla=False):
    """EVREN Kullanım Şartları Kapısı (Adım 2):
    GET /v1/terms/status -> GET /v1/terms/text -> POST /v1/terms/accept
    """
    global _SARTLAR_ONAYLANDI
    if _SARTLAR_ONAYLANDI and not zorla:
        return True
    if not aktif_mi():
        return False
    try:
        durum = _istek_yap("GET", "/terms/status", zaman_asimi=15)
        if durum.get("accepted") is True:
            _SARTLAR_ONAYLANDI = True
            return True
        surum = durum.get("current_version")
        if surum is None:
            return False
        _istek_yap("GET", "/terms/text", zaman_asimi=15)
        onay = _istek_yap("POST", "/terms/accept", {"version": surum}, zaman_asimi=15)
        _SARTLAR_ONAYLANDI = bool(onay.get("accepted_version") == surum)
        return _SARTLAR_ONAYLANDI
    except Exception:
        return False


def kota_sorgula(model=None):
    """GET /v1/quota uç noktasından günlük 15M kotayı ve eşzamanlılık durumunu okur."""
    if not aktif_mi():
        return {"aktif": False, "kalan_gunluk_token": _SON_KALAN_KOTA}
    yol = f"/quota?model={model}" if model else "/quota"
    try:
        veri = _istek_yap("GET", yol, zaman_asimi=10)
        kalan = veri.get("daily_remaining_tokens") or veri.get("remaining_tokens") or _SON_KALAN_KOTA
        return {
            "aktif": True,
            "kalan_gunluk_token": kalan,
            "gunluk_limit": veri.get("daily_token_limit", 15_000_000),
            "eszamanlilik_limiti": veri.get("concurrency_limit"),
            "aktif_istek": veri.get("concurrent_requests"),
            "sifirlanma": veri.get("resets_at"),
            "ucretsiz_bitis": "2026-12-01",
        }
    except Exception:
        return {
            "aktif": True,
            "kalan_gunluk_token": _SON_KALAN_KOTA,
            "gunluk_limit": 15_000_000,
            "ucretsiz_bitis": "2026-12-01",
        }


def _usage_donustur(evren_usage):
    """OpenAI/EVREN usage alanlarını Ajan Ofisi'nin 4 alanlı token_sayac biçimine çevirir."""
    if not isinstance(evren_usage, dict):
        return {"input_tokens": 0, "output_tokens": 0, "cache_creation_input_tokens": 0, "cache_read_input_tokens": 0}
    prompt_tok = int(evren_usage.get("prompt_tokens") or evren_usage.get("input_tokens") or 0)
    comp_tok = int(evren_usage.get("completion_tokens") or evren_usage.get("output_tokens") or 0)
    detay = evren_usage.get("prompt_tokens_details") or {}
    cached = int(detay.get("cached_tokens") or evren_usage.get("cache_read_input_tokens") or 0)
    yeni_girdi = max(0, prompt_tok - cached)
    return {
        "input_tokens": yeni_girdi,
        "output_tokens": comp_tok,
        "cache_creation_input_tokens": 0,
        "cache_read_input_tokens": cached,
    }


def sohbet_akis(model, mesajlar, max_tokens=ASGAR_MAKS_TOKEN, thinking=True,
                on_dusunme=None, on_metin=None, on_usage=None, zaman_asimi=180):
    """POST /v1/chat/completions (stream: true, include_usage: true).
    - `: keep-alive` yorum satırlarını atlar.
    - `delta.reasoning` ve `delta.reasoning_content` alanlarını ayrıştırır.
    - `max_tokens` en az 4096 olarak gönderilir.
    """
    sartlari_onayla()
    hedef_model = model_coz(model)
    yuk = {
        "model": hedef_model,
        "messages": [
            {"role": m["role"], "content": think_kacis(m["content"])}
            for m in mesajlar
        ],
        "max_tokens": max(int(max_tokens or ASGAR_MAKS_TOKEN), ASGAR_MAKS_TOKEN),
        "stream": True,
        "stream_options": {"include_usage": True},
    }
    if thinking is False:
        yuk["thinking"] = False

    url = f"{base_url()}/chat/completions"
    govde = json.dumps(yuk, ensure_ascii=False).encode("utf-8")

    for deneme in range(MAKS_DENEME):
        req = urllib.request.Request(url, data=govde, headers=_basliklar(), method="POST")
        try:
            with urllib.request.urlopen(req, timeout=zaman_asimi) as yanit:
                _kota_basliktan_guncelle(yanit.headers)
                metin_parcalari = []
                dusunme_parcalari = []
                son_usage = None
                mesaj_id = f"evren-{int(time.time() * 1000)}"

                for ham_satir in yanit:
                    satir = ham_satir.decode("utf-8", "replace").strip()
                    # : keep-alive (10sn heartbeat) ve boş satırlar atlanır
                    if not satir or satir.startswith(":"):
                        continue
                    if not satir.startswith("data:"):
                        continue
                    veri_str = satir[5:].strip()
                    if veri_str == "[DONE]":
                        break
                    try:
                        paket = json.loads(veri_str)
                    except json.JSONDecodeError:
                        continue

                    if paket.get("id"):
                        mesaj_id = paket["id"]

                    if isinstance(paket.get("usage"), dict):
                        son_usage = _usage_donustur(paket["usage"])
                        if on_usage:
                            on_usage(mesaj_id, son_usage)

                    secimler = paket.get("choices") or []
                    if not secimler:
                        continue
                    delta = secimler[0].get("delta") or {}
                    reasoning = delta.get("reasoning") or delta.get("reasoning_content")
                    if reasoning:
                        dusunme_parcalari.append(reasoning)
                        if on_dusunme:
                            on_dusunme(reasoning)
                    icerik = delta.get("content")
                    if icerik:
                        metin_parcalari.append(icerik)
                        if on_metin:
                            on_metin(icerik)

                tam_metin = "".join(metin_parcalari).strip()
                tam_dusunme = "".join(dusunme_parcalari).strip()
                if not son_usage:
                    # Sunucu stream sonunda usage göndermediyse yaklaşık hesapla
                    tahmini_girdi = sum(len(m.get("content", "")) for m in mesajlar) // 4
                    tahmini_cikti = (len(tam_metin) + len(tam_dusunme)) // 4
                    son_usage = {
                        "input_tokens": max(1, tahmini_girdi),
                        "output_tokens": max(1, tahmini_cikti),
                        "cache_creation_input_tokens": 0,
                        "cache_read_input_tokens": 0,
                    }
                return {
                    "id": mesaj_id,
                    "model": hedef_model,
                    "result": tam_metin,
                    "reasoning": tam_dusunme,
                    "usage": son_usage,
                    "total_cost_usd": 0.0,  # 1 Aralık 2026'ya kadar 0.00 CR ücretsiz
                }
        except urllib.error.HTTPError as e:
            _kota_basliktan_guncelle(e.headers)
            hata_govde = e.read().decode("utf-8", "replace")
            if e.code == 403 and "terms_not_accepted" in hata_govde:
                if sartlari_onayla(zorla=True):
                    continue
            if e.code in (429, 503) and deneme < MAKS_DENEME - 1:
                bekle = min(int(e.headers.get("Retry-After") or (4 * (deneme + 1))), 60)
                time.sleep(bekle)
                continue
            raise RuntimeError(f"EVREN HTTP {e.code}: {hata_govde[:300]}") from e
        except urllib.error.URLError as e:
            if deneme < MAKS_DENEME - 1:
                time.sleep(2 * (deneme + 1))
                continue
            raise RuntimeError(f"EVREN bağlantı hatası: {e}") from e


def ceo_planla(sistem_istemi, kullanici_istegi, model=None):
    """CEO karar çağrısı: thinking=False ve JSON çıktı zorlaması ile hızlı görev dağıtımı."""
    hedef_model = model_coz(model or os.environ.get("EVREN_CEO_MODEL") or VARSAYILAN_CEO_MODEL)
    mesajlar = [
        {"role": "system", "content": sistem_istemi},
        {"role": "user", "content": kullanici_istegi},
    ]
    sonuc = sohbet_akis(
        model=hedef_model,
        mesajlar=mesajlar,
        max_tokens=ASGAR_MAKS_TOKEN,
        thinking=False,
        zaman_asimi=90,
    )
    metin = sonuc["result"]
    # Markdown ```json ... ``` bloğu varsa temizle
    temiz = re.sub(r"^```(?:json)?\s*|\s*```$", "", metin.strip(), flags=re.I)
    eslesme = re.search(r"\{.*\}", temiz, re.S)
    if not eslesme:
        raise ValueError(f"CEO yanıtında JSON bulunamadı: {metin[:200]}")
    return {
        "structured_output": json.loads(eslesme.group(0)),
        "result": metin,
        "usage": sonuc["usage"],
        "total_cost_usd": 0.0,
        "model": hedef_model,
    }


def ses_uret(metin, ses="deniz", format="mp3"):
    """openbmb/VoxCPM2 (POST /v1/audio/speech) ile 48kHz Türkçe TTS ses üretimi.
    Hazır sesler: deniz, ece, emre, kaan.
    """
    sartlari_onayla()
    url = f"{base_url()}/audio/speech"
    yuk = {
        "model": "voxcpm2",
        "input": str(metin or "")[:4096],
        "voice": ses if ses in ("deniz", "ece", "emre", "kaan") else "deniz",
        "response_format": format,
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(yuk, ensure_ascii=False).encode("utf-8"),
        headers=_basliklar(),
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=60) as yanit:
        return yanit.read()


def claude_ortami(hedef_model=None):
    """Claude Code CLI için EVREN Anthropic Uyumluluk Geçidi ortam değişkenlerini döndürür."""
    anahtar = api_anahtari()
    if not anahtar:
        return {**os.environ}
    ana_model = model_coz(hedef_model or "glm-5.3")
    return {
        **os.environ,
        "ANTHROPIC_BASE_URL": os.environ.get("ANTHROPIC_BASE_URL") or ANTHROPIC_GECIT_URL,
        "ANTHROPIC_AUTH_TOKEN": anahtar,
        "ANTHROPIC_MODEL": ana_model,
        "ANTHROPIC_DEFAULT_OPUS_MODEL": "glm-5.3",
        "ANTHROPIC_DEFAULT_SONNET_MODEL": "deepseek-v4.1-flash",
        "ANTHROPIC_DEFAULT_HAIKU_MODEL": "qwen3.8-flash-next",
        "CLAUDE_CODE_SUBAGENT_MODEL": "deepseek-v4.1-flash",
        "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC": "1",
    }
