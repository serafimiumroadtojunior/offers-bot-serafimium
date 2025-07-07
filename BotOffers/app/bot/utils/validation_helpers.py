from typing import Tuple, Optional
import re
import string
import random


def parse_admin_send(
    args: str
) -> Tuple[Optional[int], Optional[str]]:
    if not args:
        return None, None

    match: Optional[re.Match[str]] = re.match(r'^(\d+)\s*(.*)$', args.strip())

    if not match:
        return None, None
    
    send_id: Optional[int] = int(match.group(1))
    text: Optional[str] = match.group(2).strip()

    if not text or not send_id:
        return None, None

    return send_id, text


def generate_special_code() -> str:
    chars = string.ascii_uppercase + string.ascii_lowercase + string.digits + string.punctuation
    return ''.join(random.choice(chars) for _ in range(10))