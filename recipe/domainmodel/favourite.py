from recipe.domainmodel.recipe import Recipe

class Favourite:
    def __init__(self, id: int, user, recipe: Recipe):
        if not isinstance(id, int):
            raise ValueError("id must be an integer.")
        
        if not isinstance(recipe, Recipe):
            raise TypeError("recipe must be a Recipe instance.")

        self.__id = id
        self.__user = user
        self.__recipe = recipe

    def __repr__(self) -> str:
        return f"<Favourite {self.id}: User {self.user.id} - Recipe {self.recipe.id}>"

    def __eq__(self, other) -> bool:
        if not isinstance(other, Favourite):
            return False
        return self.id == other.id and self.user == other.user and self.recipe == other.recipe

    def __lt__(self, other) -> bool:
        if not isinstance(other, Favourite):
            raise TypeError("Comparison must be between Favourite instances")
        return self.id < other.id

    def __hash__(self) -> int:
        return hash(self.id)

    @property
    def id(self) -> int:
        return self.__id

    @property
    def user(self):
        return self.__user

    @property
    def recipe(self) -> Recipe:
        return self.__recipe
        