from google import genai
client = genai.Client(api_key="AQ.Ab8RN6L9vEKSNjr2W0OK0MAIyZgbU5xHTRTO2KsKRXnqyYLqug")

response = client.models.generate_content(

    model="gemini-2.5-flash",


    contents="What is coding?"
)

print(response.text)