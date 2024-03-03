from django.db.models import Q
from mongoAPI.models.CommitsModel import Commit
from django.utils import timezone
from django.utils.dateparse import parse_datetime

from datetime import datetime

def get_unique_contributors_count(start_date, end_date, repository_ids):
    start_date_parsed = parse_datetime(start_date)
    end_date_parsed = parse_datetime(end_date)

    # Make datetime objects timezone-aware
    if timezone.is_naive(start_date_parsed):
        start_date_parsed = timezone.make_aware(start_date_parsed, timezone.utc)
    if timezone.is_naive(end_date_parsed):
        end_date_parsed = timezone.make_aware(end_date_parsed, timezone.utc)

    # If start_date and end_date are the same, adjust end_date to the end of the day
    if start_date_parsed.date() == end_date_parsed.date():
        end_date_parsed = timezone.make_aware(datetime.combine(end_date_parsed, datetime.max.time()), timezone.utc)

    contributors = Commit.objects.filter(
        Q(repositoryId__in=repository_ids) & 
        Q(committed_date__range=(start_date_parsed, end_date_parsed))
    ).values_list('committer_email', flat=True).distinct()

    return len(set(contributors))
