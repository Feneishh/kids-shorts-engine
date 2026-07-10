import os
import asyncio
import requests
from flask import Flask, request, send_file, jsonify
import edge_tts
from moviepy.editor import ImageClip, AudioFileClip, TextClip, CompositeVideoClip

app = Flask(__name__)

async def generate_audio(text, output_path):
    # Çocuk videolarına en uygun, en doğal Türkçe yapay zeka sesi (Ahmet)
    communicate = edge_tts.Communicate(text, "tr-TR-AhmetNeural")
    await communicate.save(output_path)

@app.route('/process-video', methods=['POST'])
def process_video():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "JSON verisi bulunamadı"}), 400
            
        image_url = data.get('image_url')
        caption_text = data.get('text')
        
        if not image_url or not caption_text:
            return jsonify({"error": "Eksik resim veya metin gönderildi"}), 400

        # 1. Görseli Arka Plana İndir
        img_res = requests.get(image_url)
        with open("input_img.jpg", "wb") as f:
            f.write(img_res.content)

        # 2. Ücretsiz ve Sınırsız Sesi Üret (Edge-TTS)
        asyncio.run(generate_audio(caption_text, "input_audio.mp3"))

        # 3. Video ve Sesi Birleştir
        audio_clip = AudioFileClip("input_audio.mp3")
        duration = audio_clip.duration

        # Resmi dikey (1080x1920) Shorts formatına getir ve ses süresi kadar ayarla
        image_clip = ImageClip("input_img.jpg").set_duration(duration).resize(newsize=(1080, 1920))
        image_clip = image_clip.set_audio(audio_clip)

        # 4. Alt Bölüme Dinamik Altyazı Çak (Shorts Formatı)
        txt_clip = TextClip(
            caption_text, 
            fontsize=65, 
            color='yellow', 
            font='Arial-Bold',
            stroke_color='black', 
            stroke_width=4,
            method='caption',
            size=(900, None)
        ).set_duration(duration).set_position(('center', 1350))

        # Katmanları üst üste bindir
        final_video = CompositeVideoClip([image_clip, txt_clip], size=(1080, 1920))
        
        output_filename = "output_shorts.mp4"
        final_video.write_videofile(
            output_filename, 
            fps=24, 
            codec="libx264", 
            audio_codec="aac",
            logger=None
        )

        # Ram temizliği yap
        audio_clip.close()
        image_clip.close()
        txt_clip.close()
        final_video.close()

        # Hazırlanan MP4 dosyasını doğrudan Make.com'a geri fırlat
        return send_file(output_filename, mimetype='video/mp4', as_attachment=True)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
