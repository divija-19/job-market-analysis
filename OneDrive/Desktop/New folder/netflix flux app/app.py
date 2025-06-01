from flask import Flask, render_template, request
import pandas as pd

app = Flask(__name__)
df = pd.read_csv("data/netflix_titles.csv")

@app.route("/", methods=["GET", "POST"])
def home():
    search_title = ""
    search_genre = ""
    filtered_df = df.copy()
    rating_table_html = df["rating"].value_counts().to_frame().to_html(classes="table table-striped")

    page = 1
    has_next = False

    if request.method == "POST":
        search_title = request.form.get("title", "")
        search_genre = request.form.get("genre", "")
        page = int(request.form.get("page", 1))

        if request.form.get("clear") == "true":
            search_title = ""
            search_genre = ""

        if search_title:
            filtered_df = filtered_df[filtered_df["title"].str.contains(search_title, case=False, na=False)]
        if search_genre:
            filtered_df = filtered_df[filtered_df["type"].str.contains(search_genre, case=False, na=False)]

        # Pagination
        per_page = 20
        start = (page - 1) * per_page
        end = start + per_page
        has_next = end < len(filtered_df)
        filtered_df = filtered_df.iloc[start:end]

        table_html = filtered_df.to_html(classes="table table-striped", index=False)
    else:
        table_html = None

    return render_template(
        "index.html",
        tables=table_html,
        rating_table=rating_table_html,
        search_title=search_title,
        search_genre=search_genre,
        page=page,
        has_next=has_next
    )

if __name__ == "__main__":
    app.run(debug=True)
