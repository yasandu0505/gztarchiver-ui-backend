import json
import binascii
from google.protobuf.wrappers_pb2 import StringValue


def decode_protobuf(name: str) -> str:
    """
    Decode protobuf encoded string from JSON format.
    
    Args:
        name: JSON string containing hex-encoded protobuf data
        
    Returns:
        Decoded string value, or empty string on error
    """
    try:
        data = json.loads(name)
        hex_value = data.get("value")
        if not hex_value:
            return ""

        decoded_bytes = binascii.unhexlify(hex_value)
        sv = StringValue()
        try:
            sv.ParseFromString(decoded_bytes)
            return sv.value.strip()
        except Exception:
            decoded_str = decoded_bytes.decode("utf-8", errors="ignore")
            cleaned = ''.join(ch for ch in decoded_str if ch.isprintable())
            return cleaned.strip()
    except Exception as e:
        logging.error(f"Error decoding protobuf: {e}")
        return ""

