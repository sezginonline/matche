import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import joblib

# Define the columns that will be used for content-based recommendation as a constant variable
SELECTED_COLUMNS = ['hobbies', 'profession', 'city', 'state', 'country']

def generate_model(users_df):
    # Combine the selected columns into a single text column
    users_df['text'] = users_df[SELECTED_COLUMNS].apply(lambda x: ' '.join(x.dropna().astype(str)), axis=1)

    # Create a count vectorizer to convert the text into a matrix of token counts
    vectorizer = CountVectorizer()
    vectorizer.fit(users_df['text'])
    X = vectorizer.transform(users_df['text'])

    # Calculate the cosine similarity matrix between all user profiles
    # cosine_sim = cosine_similarity(X)

    # Save the model and the vectorizer to disk
    # joblib.dump(cosine_sim, 'model.pkl')
    joblib.dump(vectorizer, 'vectorizer.pkl')

    return X

if __name__ == '__main__':
    # Load the user profiles
    users_df = pd.read_csv('users.csv')

    # Save the vectorizer to disk
    X = generate_model(users_df)
