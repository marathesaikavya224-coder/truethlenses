import hashlib
from pathlib import Path
import tempfile
import os
import numpy as np
import cv2
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST, require_GET
from django.views.decorators.csrf import ensure_csrf_cookie
from django.middleware.csrf import get_token
from django.core.exceptions import ValidationError
from .models import TrustedReference

IMAGE_EXTS = {'.jpg', '.jpeg', '.png', '.webp', '.bmp'}
VIDEO_EXTS = {'.mp4', '.mov', '.avi', '.mkv', '.webm'}
CASCADE = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')


def index(request):
    return render(request, 'TruthLens_Django/index.html')


@ensure_csrf_cookie
@require_GET
def csrf_token(request):
    return JsonResponse({'csrfToken': get_token(request)})


def sha256_file(path):
    digest = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def image_metrics(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    h, w = gray.shape[:2]
    blur = float(cv2.Laplacian(gray, cv2.CV_64F).var())
    brightness = float(np.mean(gray))
    contrast = float(np.std(gray))
    faces = [] if CASCADE.empty() else CASCADE.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
    return {'width': int(w), 'height': int(h), 'blur_score': round(blur, 2),
            'mean_brightness': round(brightness, 2), 'contrast_std': round(contrast, 2),
            'face_count': int(len(faces))}


def review_image(path):
    image = cv2.imread(str(path))
    if image is None:
        raise ValueError('This image could not be opened. Try JPG or PNG.')
    m = image_metrics(image)
    score, reasons = 15, []
    if m['width'] < 400 or m['height'] < 400:
        score += 10; reasons.append('Low image dimensions may limit reliable visual inspection.')
    if m['blur_score'] < 35:
        score += 10; reasons.append('The image appears relatively soft or blurred.')
    if m['mean_brightness'] < 35 or m['mean_brightness'] > 225:
        score += 10; reasons.append('Very dark or bright pixels may make visual assessment harder.')
    if m['contrast_std'] < 25:
        score += 5; reasons.append('Low contrast may hide detail.')
    if not reasons:
        reasons.append('No strong issue was detected by these basic checks. This is not proof the image is authentic.')
    findings = [
        {'label':'Image dimensions','value':f"{m['width']} × {m['height']} pixels",'explanation':'Basic file properties do not establish authenticity.'},
        {'label':'Detected face regions','value':str(m['face_count']),'explanation':'A general-purpose face detector is not a deepfake detector.'},
        {'label':'Sharpness indicator','value':str(m['blur_score']),'explanation':'Laplacian variance is a rough sharpness measure; blur can be normal.'},
        {'label':'Brightness / contrast','value':f"{m['mean_brightness']} / {m['contrast_std']}",'explanation':'Simple visual statistics; unusual values are not proof of manipulation.'},
    ]
    return {'media_type':'Image','review_score':min(score,50),'review_label':'Needs closer review' if score >= 30 else 'Basic checks completed',
            'score_note':'This is a heuristic review-priority score, NOT a probability that the content is fake.',
            'findings':findings,'reasons':reasons,
            'limitations':['This version does not contain a trained deepfake/manipulation detection model.','Face detection, blur, brightness and contrast cannot reliably distinguish genuine media from AI-generated or edited media.','A low score does not mean real; a high score does not mean fake. Use trusted sources and human review.'],
            'width':m['width'],'height':m['height']}


def review_video(path):
    cap = cv2.VideoCapture(str(path))
    if not cap.isOpened(): raise ValueError('This video could not be opened. Try MP4, MOV, AVI or WEBM.')
    fps = float(cap.get(cv2.CAP_PROP_FPS) or 0)
    count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) or 0); height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) or 0)
    duration = count / fps if fps > 0 else 0
    indexes = np.linspace(0, max(count-1,0), num=min(12,max(1,count)), dtype=int)
    sharpness, face_counts, diffs, summaries = [], [], [], []
    prev = None
    for idx in indexes:
        cap.set(cv2.CAP_PROP_POS_FRAMES, int(idx)); ok, frame = cap.read()
        if not ok or frame is None: continue
        m = image_metrics(frame); timestamp = idx/fps if fps > 0 else 0
        sharpness.append(m['blur_score']); face_counts.append(m['face_count'])
        small = cv2.resize(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY), (64,64))
        if prev is not None: diffs.append(float(np.mean(cv2.absdiff(prev, small))))
        prev = small
        summaries.append({'time':round(timestamp,2),'face_count':m['face_count'],'sharpness':m['blur_score'],'brightness':m['mean_brightness']})
    cap.release()
    if not summaries: raise ValueError('No readable frames were found in this video.')
    score, reasons = 15, []
    if width < 400 or height < 300: score += 10; reasons.append('Low video resolution may limit inspection.')
    if np.mean(sharpness) < 35: score += 10; reasons.append('Sampled frames appear relatively soft or blurred.')
    if diffs and np.std(diffs) > 30: score += 5; reasons.append('Large visual changes occur between sampled frames; this can be normal motion or scene cuts.')
    if not reasons: reasons.append('No strong issue was detected by these basic checks. This is not proof the video is authentic.')
    return {'media_type':'Video','review_score':min(score,50),'review_label':'Needs closer review' if score >= 30 else 'Basic checks completed',
            'score_note':'This is a heuristic review-priority score, NOT a probability that the content is fake.',
            'findings':[{'label':'Video properties','value':f'{width} × {height} pixels','explanation':'Frame dimensions do not establish authenticity.'},
                        {'label':'Duration','value':f'{duration:.2f} seconds','explanation':'Duration is read from video metadata and may be approximate.'},
                        {'label':'Frames sampled','value':str(len(summaries)),'explanation':'Up to 12 evenly spaced frames are sampled, not every frame.'},
                        {'label':'Face counts in sampled frames','value':', '.join(map(str,face_counts)),'explanation':'Counts vary naturally due to motion, cuts, occlusion and missed detections.'},
                        {'label':'Average frame sharpness','value':f'{np.mean(sharpness):.2f}','explanation':'A basic statistic, not a manipulation detector.'}],
            'reasons':reasons,'frame_summaries':summaries,
            'limitations':['This version does not contain a trained deepfake/video manipulation detection model.','Frame sampling, face counts and sharpness cannot reliably determine whether a video is manipulated.','Sampling may miss short events or manipulation between sampled frames.','A low score does not mean real; a high score does not mean fake.'],
            'width':width,'height':height,'duration':round(duration,2)}


def get_uploaded_file(request, field='file'):
    uploaded = request.FILES.get(field)
    if not uploaded or not uploaded.name: raise ValueError('Choose a file first.')
    ext = Path(uploaded.name).suffix.lower()
    if ext not in IMAGE_EXTS | VIDEO_EXTS: raise ValueError('Unsupported file type. Use JPG, PNG, WEBP, BMP, MP4, MOV, AVI, MKV or WEBM.')
    if uploaded.size > settings.MAX_UPLOAD_MB * 1024 * 1024: raise ValueError('File too large. Maximum upload size is 100 MB.')
    return uploaded, ext


def with_temp_file(uploaded, ext):
    tmp = tempfile.NamedTemporaryFile(suffix=ext, delete=False, dir=settings.DATA_DIR)
    try:
        for chunk in uploaded.chunks(): tmp.write(chunk)
        tmp.close()
        return tmp.name
    except Exception:
        tmp.close()
        try: os.unlink(tmp.name)
        except OSError: pass
        raise


@require_POST
def analyze(request):
    try:
        uploaded, ext = get_uploaded_file(request)
        path = with_temp_file(uploaded, ext)
        try:
            digest = sha256_file(path)
            result = review_image(path) if ext in IMAGE_EXTS else review_video(path)
        finally:
            try: os.unlink(path)
            except OSError: pass
        matches = list(TrustedReference.objects.filter(sha256=digest).values('label','registered_at'))
        for m in matches: m['registered_at'] = m['registered_at'].isoformat()
        result.update({'filename':Path(uploaded.name).name,'sha256':digest,
            'reference_status':'MATCH' if matches else 'NO MATCHING REFERENCE',
            'reference_note':'This exact file matches a hash registered in the Django database.' if matches else 'No matching hash was found in the reference list. This does not mean the file is fake.',
            'matching_references':matches})
        return JsonResponse(result)
    except ValueError as e: return JsonResponse({'error':str(e)},status=400)
    except Exception as e:
        return JsonResponse({'error':'Analysis failed. Check the terminal for details.'},status=500)


@require_POST
def register_reference(request):
    try:
        uploaded, ext = get_uploaded_file(request)
        label = request.POST.get('label','').strip()
        if not label: raise ValueError('Give this trusted reference a clear label.')
        if len(label) > 100: raise ValueError('Reference label must be 100 characters or fewer.')
        path = with_temp_file(uploaded, ext)
        try: digest = sha256_file(path)
        finally:
            try: os.unlink(path)
            except OSError: pass
        record, created = TrustedReference.objects.get_or_create(sha256=digest, defaults={'label':label,'filename':Path(uploaded.name).name})
        if not created: return JsonResponse({'message':'This exact file is already registered.','sha256':digest})
        return JsonResponse({'message':'Reference registered in the Django database.','record':{'label':record.label,'filename':record.filename,'sha256':record.sha256,'registered_at':record.registered_at.isoformat()},'important':'This is not an on-chain blockchain transaction and does not prove the file is truthful.'})
    except ValueError as e: return JsonResponse({'error':str(e)},status=400)


@require_GET
def references(request):
    rows = TrustedReference.objects.order_by('-registered_at')
    return JsonResponse([{'id':r.id,'label':r.label,'filename':r.filename,'sha256':r.sha256,'registered_at':r.registered_at.isoformat(),'record_type':r.record_type} for r in rows],safe=False)
