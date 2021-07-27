from datetime import date
from typing import Optional, Union

from pydantic import BaseModel


class SearchResult(BaseModel):
    more: bool
    items: list
    num: int


class VNItemsBasic(BaseModel):
    id: int  # Visual novel ID
    title: str  # Main title
    original: Optional[str]  # Original/official title.
    released: Optional[Union[date, str]]  # Date of the first release.
    languages: list[str]  # Can be an empty array when nothing has been released yet.
    orig_lang: list[str]  # Original language of the VN. Always contains a single language.
    platforms: list[str]  # Can be an empty array when unknown or nothing has been released yet.


class CharItemsBasic(BaseModel):
    id: int  # Character ID
    name: str  # (romaji) name
    original: Optional[str]  # Original (kana/kanji) name
    gender: Optional[str]  # Character's sex (not gender); "m" (male), "f" (female) or "b" (both)
    spoil_gender: Optional[str]  # Actual sex, if this is a spoiler. Can also be "unknown" if their actual sex is not known but different from their apparent sex.
    bloodt: Optional[str]  # Blood type, "a", "b", "ab" or "o"
    birthday: list[Optional[int]]  # Array of two numbers: day of the month (1-31) and the month (1-12). Either can be null.


class StaffItemsBasic(BaseModel):
    id: int  # Staff ID
    name: str  # Primary (romaji) staff name
    original: Optional[str]  # Primary original name
    gender: Optional[str]
    language: str


class VNInfo(BaseModel):
    """flags=basic,details,relations,stats"""

    class Links(BaseModel):
        wikipedia: Optional[str]  # name of the related article on the English Wikipedia (deprecated, use wikidata instead).
        encubed: Optional[str]  # the URL-encoded tag used on encubed (deprecated).
        renai: Optional[str]  # the name part of the url on renai.us.
        wikidata: Optional[str]  # Wikidata identifier.

    class ImageFlagging(BaseModel):
        votecount: int  # number of flagging votes.
        sexual_avg: Optional[Union[int, str]]  # sexual score between 0 (safe) and 2 (explicit).
        violence_avg: Optional[Union[int, str]]  # violence score between 0 (tame) and 2 (brutal).

    class Relations(BaseModel):
        id: int
        relation: str  # relation to the VN
        title: str  # (romaji) title
        original: Optional[str]  # original/official title, can be null
        official: bool

    # basic
    id: int  # Visual novel ID
    title: str  # Main title
    original: Optional[str]  # Original/official title.
    released: Optional[Union[date, str]]  # Date of the first release.
    languages: list[Optional[str]]  # Can be an empty array when nothing has been released yet.
    orig_lang: list[str]  # Original language of the VN. Always contains a single language.
    platforms: list[Optional[str]]  # Can be an empty array when unknown or nothing has been released yet.

    # details
    aliases: Optional[str]  # Aliases, separated by newlines.
    length: Optional[int]  # Length of the game, 1-5
    description: Optional[str]  # Description of the VN. Can include formatting codes as described in d9#3.
    links: Links  # see d11 docs
    image: Optional[str]  # HTTP link to the VN image.
    image_nsfw: bool  # (deprecated) Whether the VN image is flagged as NSFW or not.
    image_flagging: Optional[ImageFlagging]  # Image flagging summary of the main VN image

    # relations
    relations: list[Optional[Relations]]  # (Possibly empty) list of related visual novels.

    # stats
    popularity: Union[int, float]  # Between 0 (unpopular) and 100 (most popular).
    rating: Union[int, float]  # Bayesian rating, between 1 and 10.
    votecount: int  # Number of votes.


class CharInfo(BaseModel):
    """flags=basic,details,meas,vns,voiced"""

    class ImageFlagging(BaseModel):
        votecount: int  # number of flagging votes.
        sexual_avg: Optional[Union[int, str]]  # sexual score between 0 (safe) and 2 (explicit).
        violence_avg: Optional[Union[int, str]]  # violence score between 0 (tame) and 2 (brutal).

    class Voiced(BaseModel):
        id: int  # staff ID
        aid: int  # the staff alias ID being used
        vid: int  # VN id
        note: Optional[str]

    # basic
    id: int  # Character ID
    name: str  # (romaji) name
    original: Optional[str]  # Original (kana/kanji) name
    gender: Optional[str]  # Character's sex (not gender); "m" (male), "f" (female) or "b" (both)
    spoil_gender: Optional[str]  # Actual sex, if this is a spoiler. Can also be "unknown" if their actual sex is not known but different from their apparent sex.
    bloodt: Optional[str]  # Blood type, "a", "b", "ab" or "o"
    birthday: list[Optional[int]]  # Array of two numbers: day of the month (1-31) and the month (1-12). Either can be null.

    # details
    aliases: Optional[str]  # Alternative names, separated with a newline.
    description: Optional[str]  # Description/notes, can contain formatting codes as described in d9#3. May also include [spoiler] tags!
    age: Optional[int]  # years
    image: Optional[str]  # HTTP link to the character image.
    image_flagging: Optional[ImageFlagging]  # Image flagging summary, see the similar "image_flagging" field of "get vn".

    # meas
    bust: Optional[int]  # cm
    waist: Optional[int]  # cm
    hip: Optional[int]  # cm
    height: Optional[int]  # cm
    weight: Optional[int]  # kg
    cup_size: Optional[str]

    # vns
    vns: list[list[Union[int, str]]]  # List of VNs linked to this character.

    # voiced
    voiced: list[Voiced]  # List of voice actresses (staff) that voiced this character


class StaffInfo(BaseModel):
    """flags=basic,details,aliases,vns,voiced"""

    class Voiced(BaseModel):
        id: int  # staff ID
        aid: int  # the staff alias ID being used
        cid: int  # character ID
        note: Optional[str]

    class Vns(BaseModel):
        id: int  # staff ID
        aid: int  # the staff alias ID being used
        role: str
        note: Optional[str]

    # basic
    id: int  # Staff ID
    name: str  # Primary (romaji) staff name
    original: Optional[str]  # Primary original name
    gender: Optional[str]
    language: str

    # details
    description: Optional[str]  # Description/notes of the staff, can contain formatting codes as described in d9#3

    # aliases
    aliases: list[list[Union[int, str]]]  # List of names and aliases.
    main_alias: int  # ID of the alias that is the "primary" name of the entry

    # vns
    vns: list[Vns]  # List of visual novels that this staff entry has been credited in (excluding character voicing).

    # voiced
    voiced: list[Voiced]  # List of voice actresses (staff) that voiced this character


class Char4VNsInfo(BaseModel):
    """flags=basic,voiced,vns"""

    class Voiced(BaseModel):
        id: int  # staff ID
        aid: int  # the staff alias ID being used
        vid: int  # VN id
        note: Optional[str]

    # basic
    id: int  # Character ID
    name: str  # (romaji) name
    original: Optional[str]  # Original (kana/kanji) name
    gender: Optional[str]  # Character's sex (not gender); "m" (male), "f" (female) or "b" (both)
    spoil_gender: Optional[str]  # Actual sex, if this is a spoiler. Can also be "unknown" if their actual sex is not known but different from their apparent sex.
    bloodt: Optional[str]  # Blood type, "a", "b", "ab" or "o"
    birthday: list[Optional[int]]  # Array of two numbers: day of the month (1-31) and the month (1-12). Either can be null.

    # voiced
    voiced: list[Voiced]  # List of voice actresses (staff) that voiced this character

    # vns
    vns: list[list[Union[int, str]]]  # List of VNs linked to this character.
