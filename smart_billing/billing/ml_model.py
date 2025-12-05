import os
import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors
from django.conf import settings
from .models import Product


INDEX_PATH = os.path.join(settings.BASE_DIR, 'ml_index')
VEC_PATH = os.path.join(INDEX_PATH, 'vectorizer.joblib')
NN_PATH = os.path.join(INDEX_PATH, 'nn.joblib')
PROD_CSV = os.path.join(INDEX_PATH, 'products.csv')


os.makedirs(INDEX_PATH, exist_ok=True)


def build_index():
    # read products from DB
    qs = Product.objects.all()
    df = pd.DataFrame([{'id': p.id, 'name': p.name} for p in qs])
    if df.empty:
        print('No products to build index on')
        return
    df.to_csv(PROD_CSV, index=False)


    vectorizer = TfidfVectorizer(analyzer='char_wb', ngram_range=(2,4))
    X = vectorizer.fit_transform(df['name'])
    nn = NearestNeighbors(n_neighbors=3, metric='cosine').fit(X)


    joblib.dump(vectorizer, VEC_PATH)
    joblib.dump(nn, NN_PATH)
    print('Index built:', VEC_PATH, NN_PATH)




def predict_item(query, topk=5):
    # return top-k product records (id, name)
    if not os.path.exists(VEC_PATH) or not os.path.exists(NN_PATH):
        build_index()
    vectorizer = joblib.load(VEC_PATH)
    nn = joblib.load(NN_PATH)
    df = pd.read_csv(PROD_CSV)
    q = vectorizer.transform([query])
    dists, idxs = nn.kneighbors(q, n_neighbors=min(topk, len(df)))
    results = []
    for dist, idx in zip(dists[0], idxs[0]):
        row = df.iloc[idx]
        results.append({'id': int(row['id']), 'name': row['name'], 'score': float(1-dist)})
    return results