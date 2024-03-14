from openai import OpenAI

api_key = open("API_KEY", "r").read()

client = OpenAI(api_key = api_key)


class ChatAssistant():

    systemMessage = {"role": "system", "content": "You are UraniumGPT which a helpful AI assistant based on ChatGPT. It is named after it's creator Mr. Uranium."}

    models = ["gpt-3.5-turbo", "gpt-4-0125-preview"]
    selectedModel = 0

    chats = []
    selectedChat = 0

    def __init__(self):
        self.newChat()

    def deleteChat(self):
        self.chats.pop(self.selectedChat)
        self.selectedChat = max(0, self.selectedChat - 1)

        if len(self.chats) == 0:
            self.newChat()
            
    def newChat(self):
        #check if the current chat is not empty
        if len(self.chats) == 0 or len(self.chats[self.selectedChat]) > 1:
            self.chats.append([self.systemMessage])
            self.selectedChat = len(self.chats) - 1
        
    def backward(self):
        if self.selectedChat > 0:
            self.selectedChat -= 1
    
    def forward(self):
        if self.selectedChat < len(self.chats) - 1:
            self.selectedChat += 1

    def getChatText(self):
        chatText = ""
        for message in self.chats[self.selectedChat]:
            if message["role"] == "system":
                pass
            elif message["role"] == "user":
                chatText += "You: " + message["content"] + "\n"
            elif message["role"] == "assistant":
                chatText += "UraniumGPT: " + message["content"] + "\n"
            else:
                chatText += message["role"] + ": " + message["content"] + "\n"
        return chatText

    def sendMessage(self, message):

        self.chats[self.selectedChat].append({"role": "user", "content": message})

        print("Prompting using " + self.models[self.selectedModel] + " model...")

        completion = client.chat.completions.create(
            model=self.models[self.selectedModel],
            messages=self.chats[self.selectedChat],
        )

        answer = completion.choices[0].message.content

        self.chats[self.selectedChat].append({"role": "assistant", "content": answer})

        return self.getChatText()