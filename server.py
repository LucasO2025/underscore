"""
underscore — backend mínimo para gerar a waveform do slide de curiosidade.

Roda local em http://127.0.0.1:8765. Usado SÓ quando o usuário gera a
assinatura de áudio a partir de uma música no gerador. O HTML continua
funcionando 100% sem este servidor — só perde a extração de waveform
(que cai num placeholder neutro).

Setup (uma vez):
    pip install yt-dlp fastapi uvicorn
    ffmpeg precisa estar no PATH (winget install ffmpeg)

Uso:
    python server.py
"""
import array
import hashlib
import math
import shutil
import subprocess
import tempfile
import wave
from pathlib import Path

import uvicorn
import yt_dlp
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

PORT = 8765
CACHE_DIR = Path(tempfile.gettempdir()) / "underscore_video_cache"
CACHE_DIR.mkdir(exist_ok=True)
WAVEFORM_N = 56  # blocos fixos — garante consistência visual entre slides

app = FastAPI(title="underscore waveform backend")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Waveform por url (key = sha1(url)). O áudio é baixado, reduzido a 56 picos RMS
# e descartado — só o array sobrevive. Cache evita rebaixar a mesma faixa.
_waveform_cache: dict = {}


def _compute_waveform(wav_path: Path, n: int = WAVEFORM_N):
    """Lê um WAV mono 16-bit e devolve n picos RMS normalizados (0..1).

    A maior barra sempre chega a 1.0 (normaliza pelo máximo global) pra que
    faixas de volume baixo não fiquem achatadas. 3 casas decimais.
    """
    with wave.open(str(wav_path), "rb") as wf:
        nframes = wf.getnframes()
        sampwidth = wf.getsampwidth()
        raw = wf.readframes(nframes)

    if sampwidth != 2:
        raise ValueError("esperado PCM 16-bit (ffmpeg deveria ter forçado)")

    samples = array.array("h")
    samples.frombytes(raw)
    total = len(samples)
    if total == 0:
        return [0.0] * n

    block = total / n
    peaks = []
    for i in range(n):
        s = int(i * block)
        e = int((i + 1) * block)
        if e <= s:
            e = s + 1
        seg = samples[s:e]
        if not seg:
            peaks.append(0.0)
            continue
        acc = 0.0
        for v in seg:
            acc += v * v
        peaks.append(math.sqrt(acc / len(seg)))

    mx = max(peaks) or 1.0
    return [round(p / mx, 3) for p in peaks]


@app.get("/health")
def health():
    return {"ok": True, "service": "underscore"}


@app.get("/waveform")
def waveform(url: str):
    """Baixa só o áudio da url, reduz a 56 picos RMS e devolve o array.

    Usado pelo slide de curiosidade como assinatura de áudio. O .wav é
    temporário e apagado em seguida — nada de áudio persiste.
    """
    if not url:
        raise HTTPException(400, "url obrigatória")

    key = hashlib.sha1(url.encode()).hexdigest()
    if key in _waveform_cache:
        return {"waveform": _waveform_cache[key], "n": WAVEFORM_N, "cached": True}

    if not shutil.which("ffmpeg"):
        raise HTTPException(500, "ffmpeg não encontrado no PATH")

    src_prefix = CACHE_DIR / f"wave-{key}.src"
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": str(src_prefix) + ".%(ext)s",
        "quiet": True,
        "no_warnings": True,
        "noprogress": True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.extract_info(url, download=True)
    except Exception as e:
        raise HTTPException(500, f"yt-dlp falhou: {e}")

    candidates = list(CACHE_DIR.glob(f"wave-{key}.src.*"))
    if not candidates:
        raise HTTPException(500, "yt-dlp não produziu áudio")
    src = candidates[0]

    # ffmpeg reduz a mono 8 kHz 16-bit — leve o bastante pra ler em memória
    # e fino o bastante pra um envelope RMS de 56 blocos.
    wav_path = CACHE_DIR / f"wave-{key}.wav"
    try:
        subprocess.run(
            [
                "ffmpeg", "-y", "-loglevel", "error",
                "-i", str(src),
                "-ac", "1", "-ar", "8000",
                "-f", "wav",
                str(wav_path),
            ],
            check=True, capture_output=True,
        )
    except subprocess.CalledProcessError as e:
        msg = e.stderr.decode(errors="ignore")[:400]
        raise HTTPException(500, f"ffmpeg falhou: {msg}")
    finally:
        for f in candidates:
            f.unlink(missing_ok=True)

    try:
        peaks = _compute_waveform(wav_path)
    except Exception as e:
        raise HTTPException(500, f"falha ao computar waveform: {e}")
    finally:
        wav_path.unlink(missing_ok=True)

    _waveform_cache[key] = peaks
    return {"waveform": peaks, "n": WAVEFORM_N, "cached": False}


if __name__ == "__main__":
    print(f"underscore waveform backend -> http://127.0.0.1:{PORT}")
    print(f"cache: {CACHE_DIR}")
    uvicorn.run(app, host="127.0.0.1", port=PORT, log_level="warning")
