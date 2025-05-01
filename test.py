
import speech_recognition as sr
import pyttsx3
import google.generativeai as genai

# Configurações do modelo Gemin
genai.configure(api_key="AIzaSyCkNDj7Yzndmj0QVC4SLcq60lKMCaZDvsg")
model = genai.GenerativeModel("models/gemini-1.5-pro")

# Função para capturar a voz do usuário 
def capturar_voz():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Aguardando sua pergunta...")
        r.adjust_for_ambient_noise(source)  # Ajusta para o ruído ambiente
        audio = r.listen(source)  # Escuta a entrada de áudio
    try:
        pergunta = r.recognize_google(audio, language="pt-BR")  # Converte áudio em texto
        print(f"Você perguntou: {pergunta}")
        return pergunta
    except sr.UnknownValueError:
        print("Não consegui entender. Pode repetir?")
        return None
    except sr.RequestError as e:
        print(f"Erro ao tentar se conectar ao serviço de reconhecimento de voz; {e}")
        return None

# Função para responder com voz
def falar_resposta(resposta):
    engine = pyttsx3.init()
    engine.setProperty('rate', 150)  # Velocidade da fala
    engine.setProperty('volume', 1)  # Volume (0.0 a 1.0)
    engine.say(resposta)
    engine.runAndWait()

# Função principal
def main():
    pergunta = capturar_voz()  # Captura a pergunta do usuário
    if pergunta:
        # Gera a resposta usando o modelo Gemini
        response = model.generate_content(pergunta)
        resposta_texto = response.text
       # print(f"Resposta do Gemini: {resposta_texto}")

        # Responde ao usuário com voz
        falar_resposta(resposta_texto)

if __name__ == "__main__":
    main()
