from sklearn.cluster import KMeans
from pymongo import MongoClient

# connect to MongoDB
client = MongoClient()
db = client["match-e"]
collection = db["users"]

# get all unique questions and answers from the database
questions = set()
answers = set()
for user in collection.find():
    for question in user["responses"]:
        questions.add(question)
        answers.add(user["responses"][question])

# create feature matrix from survey responses
X = []
for user in collection.find():
    x = []
    for question in questions:
        answer = user["responses"].get(question, None)
        if answer is not None:
            x.append(list(answers).index(answer))
        else:
            x.append(-1) # or some other value to indicate missing data
    X.append(x)

# perform k-means clustering
kmeans = KMeans(n_clusters=3, random_state=0, n_init=10).fit(X)

# update cluster label for each user in the collection
documents = collection.find()
for i, label in enumerate(kmeans.labels_):
    user_id = documents[i]["_id"]  # extract _id field
    collection.update_one({"_id": user_id}, {"$set": {"cluster": str(label+1)}})
    print(f"User {i+1} is in cluster {label+1}")
