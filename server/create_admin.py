import os
import django
import sys

# Set up Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.contrib.auth.models import User

def promote_user(identifier):
    try:
        if '@' in identifier:
            user = User.objects.get(email=identifier)
        else:
            user = User.objects.get(username=identifier)
        
        user.is_staff = True
        user.is_superuser = True
        user.save()
        print(f"✅ User '{user.username}' ({user.email}) has been promoted to Admin.")
    except User.DoesNotExist:
        print(f"❌ Error: User with identifier '{identifier}' not found.")

def create_admin(username, email, password):
    try:
        User.objects.create_superuser(username=username, email=email, password=password)
        print(f"✅ Superuser '{username}' created successfully.")
    except Exception as e:
        print(f"❌ Error creating superuser: {e}")

if __name__ == "__main__":
    print("=== Eternelle aura Admin Management Utility ===")
    print("1. Promote existing user to Admin")
    print("2. Create new Admin (Superuser)")
    
    choice = input("Select an option (1/2): ")
    
    if choice == '1':
        id_val = input("Enter username or email: ")
        promote_user(id_val)
    elif choice == '2':
        u = input("Username: ")
        e = input("Email: ")
        p = input("Password: ")
        create_admin(u, e, p)
    else:
        print("Invalid choice.")
