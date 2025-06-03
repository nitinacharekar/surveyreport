import google.generativeai as genai


GOOGLE_API_KEY = 'AIzaSyBaatgD5IVZuffNcLNwG_GHqLs9Luqzk5g'

if __name__ == "__main__":
    genai.configure(api_key=GOOGLE_API_KEY)
    #print([m.name for m in genai.list_models()])
    response = genai.GenerativeModel('models/gemini-1.5-flash').generate_content("Hello, how are you?")
    print(response.text)