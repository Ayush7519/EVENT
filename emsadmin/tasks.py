from datetime import datetime, timedelta

from celery import shared_task

from .models import Event


@shared_task(bind=True)
def test_function(self):
    current_date = datetime.now().date()
    print(current_date)
    one_week_date = current_date - timedelta(7)
    print(one_week_date)
    current_time = datetime.now().time()
    print(current_time)

    for event in Event.objects.filter(date__range=[one_week_date, current_date]):
        if event.time <= current_time:
            event.event_completed = True
            event.save()
            related_artists = event.artist.all()
            for artist in related_artists:
                print(artist)
                print(artist.is_available)
                # Check for future events of the artist
                event_data = Event.objects.filter(
                    artist=artist,
                    date__gt=current_date,
                )
                if event_data.exists():
                    artist.is_available = False
                else:
                    artist.is_available = True
                artist.save()
        else:
            print("This is from the else condition...")

    return "done"
