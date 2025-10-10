from django import template
from urllib.parse import urlparse, parse_qs, quote as urlquote

register = template.Library()

@register.filter
def normalize_image_url(value):
    """Normalize known image provider URLs to embeddable forms or proxy paths.

    - Convert Google Drive share links (/file/d/<id>/view or /open?id=) to uc?export=view&id=<id>
    - If host is photos.fife.usercontent.google.com, return proxied URL via /image-proxy/?url=...
    """
    if not value:
        return value
    try:
        parsed = urlparse(value)
        host = parsed.netloc.lower()
        path = parsed.path

        # Google Drive share link patterns
        if 'drive.google.com' in host:
            # file/d/<id>/view
            parts = path.split('/')
            if 'file' in parts and 'd' in parts:
                # find 'd' and get next segment
                try:
                    d_index = parts.index('d')
                    file_id = parts[d_index+1]
                    return f"/image-proxy/?url=https://drive.google.com/uc?export=view&id={file_id}"
                except Exception:
                    pass
            # ?id= pattern
            qs = parse_qs(parsed.query)
            if 'id' in qs:
                file_id = qs['id'][0]
                return f"/image-proxy/?url=https://drive.google.com/uc?export=view&id={file_id}"
            # fallback: use uc?export=view with the 'id' portion if the path contains /d/
            if '/d/' in path:
                try:
                    file_id = path.split('/d/')[1].split('/')[0]
                    return f"/image-proxy/?url=https://drive.google.com/uc?export=view&id={file_id}"
                except Exception:
                    pass

        # Google Photos host - use proxy
        if 'photos.fife.usercontent.google.com' in host:
            return f"/image-proxy/?url={urlquote(value)}"

        # Otherwise return original value
        return value
    except Exception:
        return value
