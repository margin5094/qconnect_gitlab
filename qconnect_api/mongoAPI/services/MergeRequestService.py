from django.db.models import Q
from datetime import datetime
from mongoAPI.models.MergeRequestModel import MergeRequest
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count, F
import pytz

class MergeRequestService:
    @staticmethod
    def get_active_and_new_prs(start_date_str, end_date_str, repository_ids):
        # Parse the start and end dates
        start_date = datetime.fromisoformat(start_date_str).replace(tzinfo=pytz.UTC)
        end_date = datetime.fromisoformat(end_date_str).replace(tzinfo=pytz.UTC)

        # Fetch merge requests created or still active within the date range
        merge_requests = MergeRequest.objects.filter(
            Q(repositoryId__in=repository_ids) &
            (Q(created_at__lte=end_date) | Q(merged_at__isnull=True) | Q(merged_at__gte=start_date))
        )

        # Initialize response structure
        response = {
            "dates": [],
            "active": [],
            "newly_created": []
        }

        # Process each day in the range
        current_date = start_date
        while current_date <= end_date:
            current_date_str = current_date.strftime("%Y-%m-%d")
            day_start = current_date
            day_end = current_date + timedelta(days=1)

            # Filter and count in Python
            active_count = sum(
                1 for mr in merge_requests if mr.created_at < day_start and ((mr.merged_at is None and mr.state == 'opened') or (mr.merged_at is not None and mr.merged_at >= day_end))
            )

            newly_created_count = sum(
                1 for mr in merge_requests if day_start <= mr.created_at < day_end
            )

            if active_count > 0 or newly_created_count > 0:
                response["dates"].append(current_date_str)
                response["active"].append(active_count)
                response["newly_created"].append(newly_created_count)

            current_date += timedelta(days=1)

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

        # Calculate average duration per day in hours
        avg_durations_hours = {day: (sum(durations) / len(durations)) / 60 for day, durations in day_durations.items()}

        # Sort the avg_durations_hours dictionary by its keys (dates) from past to present
        sorted_avg_durations_hours = dict(sorted(avg_durations_hours.items(), key=lambda item: item[0]))

        # Prepare the sorted response with times in hours
        response = {
            "dates": [day.strftime("%Y-%m-%d") for day in sorted_avg_durations_hours.keys()],
            "times": [avg for avg in sorted_avg_durations_hours.values()]
        }

        return response

