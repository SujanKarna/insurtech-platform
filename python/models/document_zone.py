from enum import Enum


class DocumentZone(str, Enum):

    INTRO = "intro"
    TOC = "toc"
    MAIN_CONTENT = "main_content"