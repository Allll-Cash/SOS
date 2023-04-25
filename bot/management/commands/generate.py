import random
import string

from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.core.management import BaseCommand

from bot.config import FACULTIES, OTHER_PROBLEMS


class Command(BaseCommand):

    def get_password(self):
        letters = string.ascii_lowercase + string.ascii_uppercase + string.digits
        return ''.join([random.choice(letters) for _ in range(20)])

    def handle(self, *args, **options):
        for faculty in list(FACULTIES.values()) + list(OTHER_PROBLEMS.values()):
            try:
                User.objects.get(username=faculty)
                print(f"User {faculty} already exist, skipping")
            except ObjectDoesNotExist:
                password = self.get_password()
                User.objects.create_user(
                    username=faculty,
                    password=password
                )
                print(f'username: {faculty}')
                print(f'password: {password}')
                print('\n\n')
        password = self.get_password()
        try:
            User.objects.create_superuser(
                username='admin',
                password=password
            )
        except:
            print('admin already exist')
            return
        print(f'username: admin')
        print(f'password: {password}')
        print('\n\n')
