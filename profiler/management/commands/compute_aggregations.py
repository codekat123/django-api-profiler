from django.core.management.base import BaseCommand
from ...services import compute_endpoint_summaries


class Command(BaseCommand):
    help = "Compute endpoint aggregation summaries for the last completed time window"

    def handle(self, *args, **options):
        self.stdout.write("Computing endpoint summaries...")

        count = compute_endpoint_summaries()

        if count == 0:
            self.stdout.write(self.style.WARNING(
                "No data found in the last completed window."
            ))
        else:
            self.stdout.write(self.style.SUCCESS(
                f"Successfully computed summaries for {count} endpoint(s)."
            ))