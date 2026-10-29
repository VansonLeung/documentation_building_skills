#!/usr/bin/env python3
"""Draw a measured PCM envelope; optional synthetic non-speech tone fixture."""
import argparse
import hashlib
import html
import json
import math
from pathlib import Path
import struct
import wave


def envelope(file, bins=400, channel=0):
    with wave.open(str(file), 'rb') as audio:
        channels, width, rate, count = audio.getnchannels(), audio.getsampwidth(), audio.getframerate(), audio.getnframes()
        if width != 2 or audio.getcomptype() != 'NONE':
            raise ValueError('Only uncompressed 16-bit PCM WAV is supported')
        if not count or not 0 <= channel < channels or not 1 <= bins <= 5000:
            raise ValueError('Empty audio or invalid channel/bin count')
        frames = audio.readframes(count)
    values = struct.unpack('<' + str(len(frames) // 2) + 'h', frames)[channel::channels]
    if len(values) != count:
        raise ValueError('Truncated WAV')
    bins = min(bins, count)
    rows = []
    for i in range(bins):
        start, end = i * count // bins, (i + 1) * count // bins
        section = values[start:end]
        rows.append({'start_s': start / rate, 'end_s': end / rate,
                     'min': min(section) / 32768, 'max': max(section) / 32768})
    return {'sample_rate': rate, 'channels': channels, 'channel': channel, 'frames': count,
            'duration_s': count / rate, 'amplitude_scale': 'fixed PCM full-scale, not per-file peak normalized', 'bins': rows}


def render(data, label):
    bars = []
    for i, row in enumerate(data['bins']):
        x = 40 + 720 * (i + .5) / len(data['bins'])
        bars.append(f'<line x1="{x:.2f}" x2="{x:.2f}" y1="{115 - row["max"] * 65:.2f}" y2="{115 - row["min"] * 65:.2f}" stroke="#237e78"/>')
    return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 230"><title>' + html.escape(label) + '</title><rect width="800" height="230" fill="white"/><text x="40" y="30" font-size="18">' + html.escape(label) + '</text><path d="M40 115H760" stroke="#bbb"/>' + ''.join(bars) + f'<text x="40" y="205" font-size="15">0 s</text><text x="700" y="205" font-size="15">{data["duration_s"]:.2f} s</text></svg>'


def example(file):
    rate = 16000
    # Constructed silence and modulated tones, not a voice or a model result.
    samples = []
    for i in range(rate * 4):
        t = i / rate
        value = .45 * math.sin(2 * math.pi * 220 * t) * (math.sin(math.pi * (t - 1) / 2) ** 2) if 1 <= t < 3 else 0
        samples.append(round(value * 32767))
    with wave.open(str(file), 'wb') as audio:
        audio.setnchannels(1); audio.setsampwidth(2); audio.setframerate(rate)
        audio.writeframes(struct.pack('<' + str(len(samples)) + 'h', *samples))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--input')
    mode.add_argument('--example', action='store_true')
    parser.add_argument('--output', required=True, help='New output directory')
    parser.add_argument('--channel', type=int, default=0)
    parser.add_argument('--bins', type=int, default=400)
    parser.add_argument('--label', default='PCM waveform')
    a = parser.parse_args()
    try:
        output = Path(a.output).absolute()
        output.mkdir()
        source = Path(a.input).resolve(strict=True) if a.input else output / 'synthetic-tones.wav'
        if a.example:
            example(source)
        data = envelope(source, a.bins, a.channel)
        label = 'Synthetic tones / 合成音調示意 — no VAD or ASR' if a.example else a.label
        (output / 'waveform.svg').write_text(render(data, label), encoding='utf-8')
        data.update({'source': source.name, 'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
                     'synthetic_non_speech': a.example, 'vad_asr_run': False})
        (output / 'waveform.json').write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')
        print(json.dumps({'passed': True, 'duration_s': data['duration_s'], 'output': str(output)}))
    except (OSError, ValueError, wave.Error) as error:
        print(json.dumps({'passed': False, 'error': str(error)})); raise SystemExit(1)
