import os
import re
import mimetypes
from django.http import StreamingHttpResponse

def get_range_response(file_path, request_range):
    """
    Handles HTTP Range Requests (Status 206) for video seeking.
    """
    file_size = os.path.getsize(file_path)
    content_type, _ = mimetypes.guess_type(file_path)
    content_type = content_type or 'application/octet-stream'

    range_match = re.match(r'bytes=(\d+)-(\d*)', request_range)
    first_byte, last_byte = range_match.groups()
    
    first_byte = int(first_byte) if first_byte else 0
    last_byte = int(last_byte) if last_byte else file_size - 1
    
    if last_byte >= file_size:
        last_byte = file_size - 1
    
    length = last_byte - first_byte + 1

    def file_iterator(file_path, offset, length, chunk_size=8192):
        with open(file_path, 'rb') as f:
            f.seek(offset)
            remaining = length
            while remaining > 0:
                chunk = f.read(min(chunk_size, remaining))
                if not chunk:
                    break
                yield chunk
                remaining -= len(chunk)

    response = StreamingHttpResponse(
        file_iterator(file_path, first_byte, length),
        status=206,
        content_type=content_type
    )
    response['Content-Length'] = str(length)
    response['Content-Range'] = f'bytes {first_byte}-{last_byte}/{file_size}'
    response['Accept-Ranges'] = 'bytes'
    return response
