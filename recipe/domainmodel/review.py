from datetime import datetime
class Review:
# TODO: Complete the implementation of the Review class.
    def __init__(self, review_id: int, user, recipe_id, rating: float, review_text: str, date_submitted: datetime = None):
        if not (0 <= rating <= 5):
            raise ValueError("Rating must be between 0 and 5.")
        
        self.__review_id = review_id
        self.__user = user
        self.__recipe_id = recipe_id
        self.__rating = rating
        self.__review_text = review_text
        self.__date_submitted = date_submitted if date_submitted else datetime.now()

    def __repr__(self):
        return f"<Review {self.__review_id} by {self.__user} for {self.__recipe}: {self.__rating} stars>"
    
    def __eq__(self, other):
        if not isinstance(other, Review):
            return False
        return self.__review_id == other.id

    def __lt__(self, other):
        if not isinstance(other, Review):
            raise TypeError("Comparison must be between Review instances")
        return self.__review_id < other.id

    def __hash__(self):
        return hash(self.__review_id)

    @property
    def id(self) -> int:
        return self.__review_id

    @property
    def user(self):
        return self.__user

    @property
    def recipe(self):
        return self.__recipe
    
    @property
    def recipe_id(self):
        return self.__recipe_id
    
    @property
    def rating(self) -> float:
        return self.__rating

    @property
    def review_text(self) -> str:
        return self.__review_text
    
    @property
    def date_submitted(self):
        return self.__date_submitted