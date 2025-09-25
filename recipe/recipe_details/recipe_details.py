from flask import Blueprint, render_template, request, session, flash, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired, NumberRange
from recipe.adapters.datareader.csvdatareader import CSVDataReader
from recipe.adapters.memory_repo import MemoryRepository
from recipe.domainmodel.review import Review
from recipe.authentication.authentication import login_required
from datetime import datetime
import random
import uuid

recipe_details_bp = Blueprint('recipe_details', __name__, template_folder='../templates')
repo = MemoryRepository()

class ReviewForm(FlaskForm):
    comment = TextAreaField('Comment', validators=[DataRequired(message='Comment here.')])
    rating = SelectField('Rating', choices=[1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5], coerce=float, validators=[DataRequired(message='Select Ratings.'), NumberRange(min=1, max=5)])
    submit = SubmitField('Send Review')
    

def seed_sample_reviews(repo, recipe_id):
    
    user_lists = ["Alice", "Bob", "Charlie", "David", "Eve"]
    date_times = [
        datetime(2024, 9, 12, 12, 0),
        datetime(2025, 2, 1, 15, 30),
        datetime(2025, 2, 15, 8, 45)
    ]
    review_texts = [
        "This dish is incredibly tasty and satisfying.",
        "The flavors blend together perfectly.",
        "It's a bit too salty for my liking.",
        "Absolutely delicious and worth trying again!",
        "The texture is just right, not too chewy."
    ]
    ratings = [3, 4, 5, 3.5, 4.5]
    
    num_reviews = random.randint(1, 3)  
    for i in range(num_reviews):
        user = random.choice(user_lists)
        rating = random.choice(ratings)
        review_text = random.choice(review_texts)
        date_submitted = random.choice(date_times)
        
        review_obj = Review(
            review_id=str(uuid.uuid4()),  
            user=user,
            recipe_id=recipe_id,
            rating=rating,
            review_text=review_text,
            date_submitted=date_submitted
        )
        repo.add_review(review_obj)

@recipe_details_bp.route('/recipe_details/<int:recipe_id>', methods=['GET', 'POST'])
def display_recipe(recipe_id):
    recipe = repo.get_recipe(recipe_id)
    if recipe is None:
        return "Recipe not found", 404
    
    back_url = request.referrer or '/browse'
    
    ingredient_pairs = zip(recipe.ingredient_quantities, recipe.ingredients)
    
    if recipe_id not in repo._reviews or not repo._reviews[recipe_id]:
       seed_sample_reviews(repo, recipe_id)
       
    reviews = repo.get_reviews_for_recipe(recipe_id=recipe_id)
    
    is_authenticated = 'user_name' in session
    form = ReviewForm() if is_authenticated else None
    
    if is_authenticated and request.method == 'POST':
        form = ReviewForm()
        if form.validate_on_submit():
            new_review = Review(
                review_id=str(uuid.uuid4()),
                review_text=form.comment.data,
                recipe_id=recipe_id,
                user=session['user_name'],
                rating=form.rating.data,
                date_submitted=datetime.now()
            )
            if recipe_id not in repo._reviews:
                repo._reviews[recipe_id] = []
            repo._reviews[recipe_id].append(new_review)
            flash('Your review have been added.', 'success')
            return redirect(url_for('recipe_details.display_recipe', recipe_id=recipe_id))
    else:
        redirect(url_for('recipe_details.display_recipe', recipe_id=recipe_id))
    return render_template('recipe.html', recipe=recipe, ingredient_pairs=ingredient_pairs, back_url=back_url, reviews=reviews, form=form)