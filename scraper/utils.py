from .models import CustomUser

def get_or_create_user_instance(user_data):
    """
    Fetch the CustomUser instance from the database or create it if missing.
    """
    if not user_data or not user_data.get("email"):
        return None  # Ensure valid data exists

    user, created = CustomUser.objects.get_or_create(
        email=user_data["email"],
        defaults={
            "first_name": user_data.get("first_name", ""),
            "last_name": user_data.get("last_name", "")
        }
    )
    return user




