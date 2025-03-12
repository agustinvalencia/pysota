from lingua import Language, LanguageDetectorBuilder

from pysota.core import Publication


class Cleaner:
    english_detector = LanguageDetectorBuilder.from_all_languages().build()

    @staticmethod
    def remove_duplicates(db: list[Publication]) -> list[Publication]:
        for i in db:
            for j in db:
                if i == j:
                    db.remove(j)
        return db

    @staticmethod
    def is_english(text: str) -> bool:
        language = Cleaner.english_detector.detect_language_of(text)
        return language == Language.ENGLISH

    @staticmethod
    def remove_non_english(db: list[Publication]) -> list[Publication]:
        return [i for i in db if Cleaner.is_english(i.abstract)]
