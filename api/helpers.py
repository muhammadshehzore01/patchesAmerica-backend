# helpers.py or in the same serializers file
# backend\api\helpers.py
def build_full_url(request, file_field):
    if not file_field:
        return None

    url_path = file_field.url  # e.g., /media/sliders/Utah_Raptor.png

    # Build full URL using request if available
    if request:
        full_url = request.build_absolute_uri(url_path)
    else:
        # fallback when request is None
        full_url = f"http://localhost:8000{url_path}"

    # Sanitize Docker hostnames → always point to localhost for browser
    full_url = full_url.replace("backend:8000", "localhost:8000") \
                       .replace("django_backend:8000", "localhost:8000")
    return full_url
