from mistralai import Mistral

class Mistral_Ai:
    def __init__(self, api):
        self.__api = api
        self.__client: Mistral = None

    def generate_text(self, prompt) -> str:
        if not self.__client:
            self.__client = Mistral(api_key=self.__api)
        response = self.__client.chat.complete(
            model= "mistral-large-2407",
            messages = [
                {
                    "role": "user",
                    "content": str(prompt),
                },
            ]
        )
        return response