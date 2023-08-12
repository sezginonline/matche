import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer
from pymongo import MongoClient
import joblib
from scipy.sparse import vstack
import os


# Load configuration from environment variables
MONGODB_URI = 'mongodb://localhost:27017/'
MODEL_DIR = os.environ.get('MODEL_DIR', '.')


def create_model():
    """Create a recommendation model and save it to disk"""
    # Connect to MongoDB
    with MongoClient(MONGODB_URI) as client:
        db = client.get_database('match-e')
        users_collection = db['profiles']
        # Load the user profiles
        users_df = pd.DataFrame(list(users_collection.find()))

    # Create model
    text = users_df[['sense_of_style', 'work_life_balance']].apply(lambda x: ' '.join(x.dropna().astype(str)), axis=1)
    vectorizer = CountVectorizer()
    vectorizer.fit(text)
    model = vectorizer.transform(text)

    # Save the model and vectorizer to disk
    joblib.dump(vectorizer, os.path.join(MODEL_DIR, 'vectorizer.joblib'))
    joblib.dump(dict(zip(users_df['_id'], model)), os.path.join(MODEL_DIR, 'model.joblib'))


def recommend_users(new_user_text):
    """Recommend similar users based on the input text"""
    # Validate the input
    if not isinstance(new_user_text, str) or not new_user_text.strip():
        raise ValueError("Input must be a non-empty string")

    # Load the model
    vectorizer = joblib.load(os.path.join(MODEL_DIR, 'vectorizer.joblib'))
    model = joblib.load(os.path.join(MODEL_DIR, 'model.joblib'))

    # Convert the new user's text into a matrix of token counts using the vectorizer
    new_user_vec = vectorizer.transform([new_user_text])

    # Calculate the cosine similarity between the new user's profile and other user profiles
    cosine_similarities = cosine_similarity(new_user_vec, vstack(list(model.values())))

    # Get the indices and user_ids of the top recommended users based on cosine similarity
    top_users = [(user_id, cosine_similarities[0][i]) for i, user_id in enumerate(model.keys()) if cosine_similarities[0][i] > 0]
    top_users = sorted(top_users, key=lambda x: x[1], reverse=True)[:100]

    # Return the user_ids
    return [str(user[0]) for user in top_users]


if __name__ == '__main__':
    create_model()
    print(recommend_users('Classic Balanced'))
