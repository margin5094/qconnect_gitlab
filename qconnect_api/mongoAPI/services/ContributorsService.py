from django.db.models import Q, Count
from mongoAPI.models.CommitsModel import Commit
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from datetime import datetime

def get_unique_contributors_count(start_date, end_date, repository_ids):
    start_date_parsed = parse_datetime(start_date)
    end_date_parsed = parse_datetime(end_date)

    if timezone.is_naive(start_date_parsed):
        start_date_parsed = timezone.make_aware(start_date_parsed, timezone.utc)
    if timezone.is_naive(end_date_parsed):
        end_date_parsed = timezone.make_aware(end_date_parsed, timezone.utc)

    # If start_date and end_date are the same, adjust end_date to the end of the day
    # if start_date_parsed.date() == end_date_parsed.date():
    end_date_parsed = timezone.make_aware(datetime.combine(end_date_parsed, datetime.max.time()), timezone.utc)

    contributors = Commit.objects.filter(
        Q(repositoryId__in=repository_ids) & 
        Q(committed_date__range=(start_date_parsed, end_date_parsed))
    ).values_list('committer_email', flat=True).distinct()

    return len(set(contributors))

#----------------------------------------------------------------------------------------------------
def get_contributors_data(start_date_str, end_date_str, repository_ids):
    start_date = parse_datetime(start_date_str)
    end_date = parse_datetime(end_date_str)

    if timezone.is_naive(start_date):
        start_date = timezone.make_aware(start_date, timezone.utc)
    if timezone.is_naive(end_date):
        end_date = timezone.make_aware(end_date, timezone.utc)

    end_date_adjusted = end_date + timezone.timedelta(days=1)

    # Fetching all commits once, instead of querying inside the loop.
    all_commits = Commit.objects.filter(
        Q(repositoryId__in=repository_ids) &
        Q(committed_date__gte=start_date) &
        Q(committed_date__lt=end_date_adjusted)
    ).order_by('committed_date').values('committer_email', 'committed_date')

    # Convert QuerySet to list to process it multiple times without hitting the database.
    all_commits_list = list(all_commits)

    dates_list = []
    active_users_list = []
    total_users_list = []

    # Pre-calculating all unique committers up to each date for efficiency.
    total_committers_so_far = set()
    total_committers_by_date = {}
    for commit in all_commits_list:
        commit_date_str = commit['committed_date'].date().strftime("%Y-%m-%d")
        total_committers_so_far.add(commit['committer_email'])
        total_committers_by_date[commit_date_str] = len(total_committers_so_far)

    for single_date in (start_date + timezone.timedelta(days=x) for x in range((end_date - start_date).days + 1)):
        single_date_str = single_date.strftime("%Y-%m-%d")
        daily_commits = [commit for commit in all_commits_list if commit['committed_date'].date() == single_date.date()]
        daily_active_emails = {commit['committer_email'] for commit in daily_commits}

        dates_list.append(single_date_str)
        active_users_list.append(len(daily_active_emails))
        total_users_list.append(total_committers_by_date.get(single_date_str, 0))

    # Filter dates with active or total users.
    positive_indices = [i for i, (active, total) in enumerate(zip(active_users_list, total_users_list)) if active > 0 or total > 0]

    response = [{
        "dates": [dates_list[i] for i in positive_indices],
        "activeUsers": [active_users_list[i] for i in positive_indices],
        "totalUsers": [total_users_list[i] for i in positive_indices]
    }]

    return response



#--------------top-contributors-------------
def get_top_active_contributors(start_date_str, end_date_str, repository_ids):
    start_date = parse_datetime(start_date_str)
    end_date = parse_datetime(end_date_str)

    if timezone.is_naive(start_date):
        start_date = timezone.make_aware(start_date, timezone.utc)
    if timezone.is_naive(end_date):
        end_date = timezone.make_aware(end_date, timezone.utc)
    
    # Aggregate commits by committer_email
    commits_data = Commit.objects.filter(
        repositoryId__in=repository_ids,
        committed_date__gte=start_date,
        committed_date__lte=end_date
    ).values('committer_email').annotate(commits=Count('commitId')).order_by('-commits')[:5]

    # Enriching with committer_name and adjusting key names
    enriched_data = []
    for data in commits_data:
        latest_commit = Commit.objects.filter(committer_email=data['committer_email']).latest('committed_date')
        enriched_data.append({
            "email": data['committer_email'],
            "commits": data['commits'],
            "name": latest_commit.committer_name
        })

    return enriched_data