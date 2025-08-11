from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile

def compress_image(uploaded_image, max_size_kb=90, max_width=1024):
    image = Image.open(uploaded_image)
    image = image.convert("RGB")  # toujours en RGB pour JPEG

    # Redimensionner si largeur trop grande
    if image.width > max_width:
        ratio = max_width / float(image.width)
        new_height = int(image.height * ratio)
        image = image.resize((max_width, new_height), Image.Resampling.LANCZOS)

    # Compression progressive
    quality = 85
    while True:
        buffer = BytesIO()
        image.save(buffer, format='JPEG', quality=quality, optimize=True)
        size_kb = buffer.tell() / 1024
        if size_kb <= max_size_kb or quality <= 30:
            break
        quality -= 5

    buffer.seek(0)
    return InMemoryUploadedFile(
        buffer,
        'ImageField',
        f"{uploaded_image.name.split('.')[0]}.jpg",
        'image/jpeg',
        buffer.tell(),
        None
    )

import ffmpeg

import subprocess
import tempfile
import os
from django.core.files.uploadedfile import InMemoryUploadedFile
from io import BytesIO
import subprocess
import tempfile
import os
from django.core.files.uploadedfile import InMemoryUploadedFile
from io import BytesIO

import tempfile
import subprocess
import os
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile

def compresser_video(uploaded_video, max_duration_sec=30, max_size_mb=1.1):
    # Sauvegarde temporaire de la vidéo originale
    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as temp_input:
        for chunk in uploaded_video.chunks():
            temp_input.write(chunk)
        temp_input_path = temp_input.name

    # Fichier de sortie temporaire
    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as temp_output:
        temp_output_path = temp_output.name

    # Taille max en bits (1 Mo = 1 048 576 octets)
    max_bits = max_size_mb * 1024 * 1024 * 8  # bits
    bitrate_total = int(max_bits / max_duration_sec)  # bits/sec

    # Répartition bitrate : 80% vidéo, 20% audio
    bitrate_video = int(bitrate_total * 0.8 / 1000)  # en kbps
    bitrate_audio = int(bitrate_total * 0.2 / 1000)  # en kbps

    # Commande FFmpeg de compression
    command = [
        'ffmpeg',
        '-y',
        '-i', temp_input_path,
        '-t', str(max_duration_sec),
        '-vf', 'scale=-2:480',  # Hauteur 480px, largeur auto
        '-c:v', 'libx264',
        '-preset', 'fast',
        '-b:v', f'{bitrate_video}k',
        '-c:a', 'aac',
        '-b:a', f'{bitrate_audio}k',
        temp_output_path
    ]

    # Exécution de la commande
    subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)

    # Lecture du fichier compressé
    with open(temp_output_path, 'rb') as f:
        video_data = f.read()

    # Nettoyage des fichiers temporaires
    os.remove(temp_input_path)
    os.remove(temp_output_path)

    # Conversion en objet Django InMemoryUploadedFile
    buffer = BytesIO(video_data)
    return InMemoryUploadedFile(
        buffer,
        'FileField',
        uploaded_video.name,
        'video/mp4',
        len(video_data),
        None
    )
