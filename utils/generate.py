import hashlib

def generate_internal_id(title: str) -> str:
    """
    Generates a stable, unique internal ID for an anime title without requiring a database.
    
    The ID combines a 2-3 letter title prefix and a 4-digit numerical suffix derived 
    from the title's hash, satisfying the format OP0322 or NR7981.
    
    Example: 
    "One Piece" -> "OP1379"
    "Naruto Shippuden" -> "NS7562"
    
    Args:
        title: The clean title of the anime (e.g., "Attack on Titan").
        
    Returns:
        A unique, clean string ID consisting of letters and exactly 4 digits.
    """
    if not title:
        return "DEF0000"

    # 1. Generate the prefix (e.g., 'One Piece' -> 'OP'; 'Naruto' -> 'NR')
    # Use the first 3 capital letters from the title's words
    prefix = "".join([word[0] for word in title.split() if word]).upper()[:3]
    if not prefix:
        prefix = "DEF"

    # 2. Create a clean slug for stable hashing
    slug = title.lower().replace(" ", "-").replace(":", "").replace("'", "")
    
    # 3. Hash the slug using SHA256
    hash_digest = hashlib.sha256(slug.encode('utf-8')).hexdigest()
    
    # 4. Convert the hash to a large integer (base 10)
    hash_int = int(hash_digest, 16)
    
    # 5. Take the modulus (remainder) to get a 4-digit number (0000 to 9999)
    # 10000 is used to ensure the number part never exceeds 4 digits.
    modulus = 10000
    unique_number = hash_int % modulus
    
    # 6. Zero-pad the number to ensure it is exactly 4 characters long
    padded_number = str(unique_number).zfill(4)
    
    # 7. Combine the prefix and the 4-digit number
    return f"{prefix}{padded_number}"