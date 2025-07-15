from mistralai import Mistral

class Mistral_Ai:
    def __init__(self, api):
        self.__api = api
        self.__client: Mistral = None

    def generate_text(self, messages: list[dict[str, str]]) -> str:
        if not self.__client:
            self.__client = Mistral(api_key=self.__api)
        response = self.__client.chat.complete(
            model= "mistral-large-2407",
            messages = [
                {
                    "role": mes_obj.get('role'),
                    "content": mes_obj.get('content')
                } for mes_obj in messages
            ]
        )
        return response.model_dump_json()