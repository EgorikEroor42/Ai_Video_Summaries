import yt_dlp
from faster_whisper import WhisperModel
from pathlib import Path
import json
links = ['https://www.youtube.com/watch?v=Vu9FUxKFkYQ','https://www.youtube.com/watch?v=bb5dvg4_rms']
vidname = 'vid'
model_quality = 'tiny'
model = WhisperModel(model_quality,compute_type='int8',cpu_threads=8)
for link in links:
    yt_dlp.YoutubeDL({'format':'bestaudio/best','outtmpl':f'downvid/{vidname}.%(ext)s','verbose':True}).download([link])
    parts_text,info = model.transcribe(f'downvid/{vidname}.webm',beam_size=5)
    text = ''.join(part_text.text for part_text in parts_text)
    with open('aitrain/EducAi.txt', 'a', encoding="UTF-8") as file_par:
        file_par.write(json.dumps({"VideoText":text,"Summary":0},ensure_ascii=False) + '\n')
    file = Path(f'downvid/{vidname}.webm')
    file.unlink()
    print(link)