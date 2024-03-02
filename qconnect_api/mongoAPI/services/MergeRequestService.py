from django.db.models import Q
from datetime import datetime
from mongoAPI.models.MergeRequestModel import MergeRequest

from django.db.models import F
from datetime import datetime
import pytz

class MergeRequestService:
    @staticmethod
    def get_active_and_new_prs(start_date_str, end_date_str, repository_ids):
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d")

        # Count of active merge requests before the start date
        active_count = MergeRequest.objects.filter(
            Q(repositoryId__in=repository_ids) &
            Q(created_at__lt=start_date) &  # Dates before start_date
            Q(state='opened')
        ).count()

        # Count of newly created merge requests within the date range
        newly_created_count = MergeRequest.objects.filter(
            Q(repositoryId__in=repository_ids) &
            Q(created_at__range=(start_date, end_date))
        ).count()

        # Prepare the response in the desired format
        response = [
            {
                "dates": [start_date_str, end_date_str],
                "active": active_count,
                "newly_created": newly_created_count
            }
        ]

        return response

#-------------------------avg-close-time-----------------------------
    @staticmethod
    def get_avg_time_to_close(start_date_str, end_date_str, repository_ids):
        # Convert string dates to datetime objects
        start_date = datetime.fromisoformat(start_date_str).replace(tzinfo=pytz.UTC)
        end_date = datetime.fromisoformat(end_date_str).replace(tzinfo=pytz.UTC)

        # Fetch the merged PRs
        prs = MergeRequest.objects.filter(
            repositoryId__in=repository_ids,
            created_at__gte=start_date,
            merged_at__lte=end_date,
            merged_at__isnull=False
        )

        # Manual calculation of average times
        day_durations = {}
        for pr in prs:
            day = pr.created_at.date()
            duration = (pr.merged_at - pr.created_at).total_seconds() / 60  # duration in minutes
            if day not in day_durations:
                day_durations[day] = []
            day_durations[day].append(duration)

        # Calculate average duration per day
        avg_durations = {day: sum(durations) / len(durations) for day, durations in day_durations.items()}

        # Prepare the response
        response = {
            "dates": [day.strftime("%Y-%m-%d") for day in avg_durations.keys()],
            "times": [avg for avg in avg_durations.values()]
        }

        return response