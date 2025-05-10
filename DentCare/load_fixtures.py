import os
import django
from django.core.management import call_command
import sys

def load_fixtures():
    # Setup Django environment
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DentCare.settings')
    django.setup()

    print("Running migrations...")
    try:
        call_command('makemigrations')
        call_command('migrate')
        print("✓ Migrations completed successfully")
    except Exception as e:
        print(f"✗ Error running migrations: {str(e)}")
        sys.exit(1)

    # List of fixtures in order of dependencies
    fixtures = [
        'positions.json',
        'conditions.json',
        'dentists.json',
        'services.json',
        'comments.json',
        'users.json',
        'appointments.json'
    ]

    success_count = 0
    failed_fixtures = []

    print("\nStarting to load fixtures...")
    print("-" * 50)

    # Load each fixture
    for fixture in fixtures:
        try:
            print(f"\nLoading fixture: {fixture}")
            call_command('loaddata', f'catalog/fixtures/{fixture}')
            print(f"✓ Successfully loaded {fixture}")
            success_count += 1
        except Exception as e:
            print(f"✗ Error loading {fixture}: {str(e)}")
            failed_fixtures.append((fixture, str(e)))

    print("\n" + "=" * 50)
    print(f"Loading complete: {success_count}/{len(fixtures)} fixtures loaded successfully")
    
    if failed_fixtures:
        print("\nFailed fixtures:")
        for fixture, error in failed_fixtures:
            print(f"- {fixture}: {error}")
        sys.exit(1)
    else:
        print("\nAll fixtures loaded successfully!")
        sys.exit(0)

if __name__ == '__main__':
    load_fixtures() 