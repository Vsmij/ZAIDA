# Do wykorzystania w python manage.py shell
from core.models import User
from django.db import connection

# Czyszczenie tabeli użytkowników
print("Usuwanie wszystkich obecnych użytkowników...")
User.objects.all().delete()
print("Wszyscy użytkownicy usunięci.")

# Resetowanie sekwencji ID dl
if connection.vendor == 'sqlite':
    cursor = connection.cursor()
    cursor.execute("DELETE FROM sqlite_sequence WHERE name='core_user';")
    print("Sekwencja ID zresetowana dla SQLite.")

# Tworzenie Administratora
admin = User.objects.create_superuser(
    email='admin@test.pl',
    password='aaaaaaa1!',
    username='admin@test.pl'
)

admin.is_staff = True
admin.is_superuser = True
admin.save()
print(f"Utworzono administratora: {admin.email}")

# Tworzenie Zwykłego Użytkownika
user = User.objects.create_user(
    email='user@test.pl',
    password='aaaaaaa1!',
    username='user@test.pl'
)
user.is_staff = False
user.is_superuser = False
user.save()
print(f"Utworzono użytkownika: {user.email}")

exit()
