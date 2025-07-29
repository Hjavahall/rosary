from django.shortcuts import render, redirect
from django.http import JsonResponse, Http404
from django.utils import timezone
from django.contrib.auth.forms import UserCreationForm
from django.db.models import Count
from django.db.models.functions import TruncDate
from .models import (
    PrayerActivity, PrayerSession, MysterySet,
    Prayer, Mystery, DecadeStep, PrayerSequence, PrayerSequenceStep
)

def homepage(request):
    return render(request, 'rosary/home.html')

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'rosary/register.html', {'form': form})

def active_users(request):
    window = timezone.now() - timezone.timedelta(minutes=10)
    recent = PrayerActivity.objects.filter(last_active__gte=window)
    return render(request, 'rosary/active.html', {
        'count': recent.count(),
        'regions': recent.values_list('region', flat=True).distinct(),
    })

def stats_page(request):
    if not request.user.is_authenticated:
        return redirect('login')

    user_sessions = PrayerSession.objects.filter(user=request.user)
    prayers_by_day = user_sessions.annotate(day=TruncDate('started_at')).values('day').annotate(count=Count('id'))
    prayers_by_mystery = user_sessions.values('mystery').annotate(count=Count('id'))
    global_stats = PrayerSession.objects.annotate(day=TruncDate('started_at')).values('day').annotate(count=Count('id'))

    context = {
        'user_days': list(prayers_by_day),
        'user_mysteries': list(prayers_by_mystery),
        'global_days': list(global_stats),
    }
    return render(request, 'rosary/stats.html', context)

def prayer_heatmap_data(request):
    recent = PrayerActivity.objects.filter(
        last_active__gte=timezone.now() - timezone.timedelta(minutes=15)
    )

    region_coords = {
        'California': [36.7783, -119.4179],
        'England': [52.3555, -1.1743],
        'Ontario': [51.2538, -85.3232],
        'Nigeria': [9.0820, 8.6753],
        'Unknown': [0, 0],
    }

    data = []
    for region, count in recent.values_list('region').annotate(count=Count('region')):
        coords = region_coords.get(region, [0, 0])
        data.append({'lat': coords[0], 'lng': coords[1], 'count': count})

    return JsonResponse(data, safe=False)

def heatmap_page(request):
    return render(request, 'rosary/heatmap.html')

def dashboard(request):
    if request.method == 'POST':
        return redirect('rosary_start')
    return render(request, 'rosary/dashboard.html')

def rosary_start(request):
    weekday = timezone.now().strftime('%A')
    try:
        mystery_set = MysterySet.objects.get(days__icontains=weekday)
    except MysterySet.DoesNotExist:
        mystery_set = None

    if mystery_set:
        request.session['mystery_set_id'] = mystery_set.id
        return redirect('rosary_intro')
    else:
        return render(request, 'rosary/missing_mystery.html', {'day': weekday})

def rosary_intro(request):
    request.session['rosary_progress'] = 0
    return redirect('rosary_flow')

def rosary_flow(request):
    if 'rosary_progress' not in request.session:
        return redirect('dashboard')

    steps = build_full_rosary_sequence(request)
    current_index = request.session.get('rosary_progress', 0)

    if current_index >= len(steps):
        if request.user.is_authenticated:
            mystery_set_id = request.session.get('mystery_set_id')
            mystery_label = "Full Rosary"
            PrayerSession.objects.create(
                user=request.user,
                mystery=mystery_label,
                completed=True
            )
        del request.session['rosary_progress']
        return render(request, 'rosary/complete.html')

    current_step = steps[current_index]
    prayer = current_step["prayer"]

    if request.method == 'POST':
        request.session['rosary_progress'] = current_index + 1
        return redirect('rosary_flow')

    # Group decades for display
    decades = []
    current_decade = []
    current_label = None
    for bead in steps:
        if bead["part"].startswith("mystery-"):
            if bead["mystery_title"] != current_label:
                if current_decade:
                    decades.append((current_label, current_decade))
                current_decade = []
                current_label = bead["mystery_title"]
            current_decade.append(bead)
    if current_decade:
        decades.append((current_label, current_decade))

    return render(request, 'rosary/step_by_step.html', {
        'step': prayer,
        'part': current_step['part'],
        'mystery_title': current_step['mystery_title'],
        'current_index': current_index + 1,
        'total_steps': len(steps),
        'beads': steps,
        'decades': decades,
    })

def build_full_rosary_sequence(request):
    sequence = []

    intro = PrayerSequence.objects.get(name="Introductory Prayers")
    for step in intro.steps.all():
        for _ in range(step.repeat):
            sequence.append({
                "prayer": step.prayer,
                "part": "intro",
                "mystery_title": None
            })

    mystery_set_id = request.session.get('mystery_set_id')
    mysteries = Mystery.objects.filter(set_id=mystery_set_id).order_by('id')

    for idx, mystery in enumerate(mysteries, start=1):
        for step in mystery.steps.all():
            for _ in range(step.repeat):
                sequence.append({
                    "prayer": step.prayer,
                    "part": f"mystery-{idx}",
                    "mystery_title": mystery.title
                })

    conclusion = PrayerSequence.objects.get(name="Concluding Prayers")
    for step in conclusion.steps.all():
        for _ in range(step.repeat):
            sequence.append({
                "prayer": step.prayer,
                "part": "conclusion",
                "mystery_title": None
            })

    return sequence
