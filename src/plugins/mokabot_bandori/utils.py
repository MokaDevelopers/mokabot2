from .BandoriClient import BandoriClient
from .config import hash1, signature, user_id

client = BandoriClient(user_id=user_id, hash1=hash1, signature=signature)
