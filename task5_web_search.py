from web_search import google_search

query = "latest news on AI email assistants"
api_key = "AIzaSyAiPFkyRbNU-r8070x_xNdbObpW2T0L0iY"
cse_id = "074c743a7b947485b"

results = google_search(query, api_key, cse_id)

print("🔎 Search Results:")
for idx, result in enumerate(results, 1):
    print(f"{idx}. {result['title']}\n   {result['link']}\n   {result['snippet']}\n")
