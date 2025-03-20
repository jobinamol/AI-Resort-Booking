import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer
from django.db.models import Count
from .models import Booking, Package, Guest

def get_recommendations(user_id):
    bookings = Booking.objects.all().values("guest_id", "package_id")

    df = pd.DataFrame(bookings)

    if df.empty:
        return Package.objects.all().order_by('?')[:5]  

    user_package_matrix = df.pivot_table(index="guest_id", columns="package_id", aggfunc=len, fill_value=0)

    user_sim = cosine_similarity(user_package_matrix)
    user_sim_df = pd.DataFrame(user_sim, index=user_package_matrix.index, columns=user_package_matrix.index)

    if user_id not in user_sim_df.index:
        return Package.objects.all().order_by('?')[:5]

    similar_users = user_sim_df[user_id].sort_values(ascending=False).index[1:4]  

    recommended_package_ids = df[df["guest_id"].isin(similar_users)]["package_id"].unique()

    return Package.objects.filter(id__in=recommended_package_ids)[:5]
