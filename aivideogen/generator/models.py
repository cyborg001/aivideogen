from django.db import models
import os

class Asset(models.Model):
    file = models.FileField(upload_to='assets/')
    name = models.CharField(max_length=255, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.name and self.file:
            self.name = os.path.basename(self.file.name)
        super().save(*args, **kwargs)

    @property
    def file_exists(self):
        return self.file and os.path.exists(self.file.path)

    def __str__(self):
        return self.name

class Music(models.Model):
    file = models.FileField(upload_to='music/')
    name = models.CharField(max_length=255, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.name and self.file:
            self.name = os.path.basename(self.file.name)
        super().save(*args, **kwargs)

    @property
    def file_exists(self):
        return self.file and os.path.exists(self.file.path)

    def __str__(self):
        return self.name

class SFX(models.Model):
    file = models.FileField(upload_to='sfx/')
    name = models.CharField(max_length=255, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.name and self.file:
            self.name = os.path.basename(self.file.name)
        super().save(*args, **kwargs)

    @property
    def file_exists(self):
        return self.file and os.path.exists(self.file.path)

    def __str__(self):
        return self.name

class VideoProject(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('processing', 'Procesando'),
        ('completed', 'Completado'),
        ('failed', 'Fallido'),
        ('cancelled', 'Cancelado'),
    ]
    ENGINE_CHOICES = [
        ('edge', 'Edge TTS'),
        ('elevenlabs', 'ElevenLabs'),
    ]
    ASPECT_RATIO_CHOICES = [
        ('landscape', 'Horizontal (16:9)'),
        ('portrait', 'Vertical (9:16 - Shorts)'),
    ]

    title = models.CharField(max_length=255, default="Proyecto sin título")
    script_text = models.TextField()
    engine = models.CharField(max_length=20, choices=ENGINE_CHOICES, default='edge')
    aspect_ratio = models.CharField(max_length=20, choices=ASPECT_RATIO_CHOICES, default='landscape')
    voice_id = models.CharField(max_length=255, blank=True, null=True, help_text="ID de la voz o nombre (Edge/ElevenLabs)")
    
    background_music = models.ForeignKey(Music, on_delete=models.SET_NULL, null=True, blank=True, help_text="Música de fondo para el video")
    music_volume = models.FloatField(default=0.15, help_text="Volumen de la música (0.0 a 1.0)")
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    output_video = models.FileField(upload_to='videos/', blank=True, null=True)
    thumbnail = models.ImageField(upload_to='thumbnails/', blank=True, null=True)
    
    source_path = models.CharField(max_length=1024, blank=True, help_text="Path to local folder containing script and assets")
    
    visual_prompts = models.TextField(blank=True, help_text="Prompts generados para las imágenes y videos del guion")
    timestamps = models.TextField(blank=True, help_text="Timestamps de cada escena para capítulos de YouTube (formato: MM:SS - Título)")
    script_hashtags = models.TextField(blank=True, help_text="Hashtags extraídos del guion (# HASHTAGS: ...)")
    youtube_video_id = models.CharField(max_length=100, blank=True, null=True, help_text="YouTube video ID after upload (prevents duplicates)")
    auto_upload_youtube = models.BooleanField(default=False, help_text="Subir automáticamente a YouTube al finalizar la generación")
    
    log_output = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def status_label(self):
        return self.get_status_display()

    @property
    def output_exists(self):
        return self.output_video and os.path.exists(self.output_video.path)

    def __str__(self):
        return f"{self.title} ({self.status_label})"

class YouTubeToken(models.Model):
    token = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"YouTube Token (Último uso: {self.updated_at})"
