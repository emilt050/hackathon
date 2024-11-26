from django.http import StreamingHttpResponse
from django.shortcuts import render
from recognition_app.facial_recognition import video_stream

def video_page(request):
    return render(request, 'video_display.html')

def video_feed(request):
    return StreamingHttpResponse(video_stream(), content_type='multipart/x-mixed-replace; boundary=frame')