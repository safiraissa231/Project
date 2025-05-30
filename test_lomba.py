import streamlit as st
import pandas as pd
import google.generativeai as genai
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# --- Configuration ---
GOOGLE_API_KEY = "AIzaSyDET9U4B4uM9keiAruaxyVsm1YNaccEZwE"  # Ganti dengan API key kamu
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemma-3-1b-it')

# --- Load Pasal-Isi Dataset ---
@st.cache_data
def load_pasal_isi_from_excel(file_path):
    df = pd.read_excel(file_path)
    pasal_isi_list = list(zip(df['Pasal'], df['Isi']))
    return pasal_isi_list

# --- Retrieve Context ---
def retrieve_relevant_context(user_input, pasal_isi_list, threshold=0.3):
    isi_texts = [isi for pasal, isi in pasal_isi_list]
    corpus = [user_input] + isi_texts

    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(corpus)

    user_vector = tfidf_matrix[0]
    isi_vectors = tfidf_matrix[1:]

    similarities = cosine_similarity(user_vector, isi_vectors)[0]

    matched_context = []
    for (pasal, isi), similarity in zip(pasal_isi_list, similarities):
        if similarity > threshold:
            matched_context.append(f"{pasal}: {isi}")
    return matched_context

# --- Detect Greetings/Thanks ---
def detect_special_response(text):
    greetings = ['halo', 'hai', 'hello', 'hi', 'selamat pagi', 'selamat siang',
                 'selamat sore', 'selamat malam', 'assalamualaikum', 'salam sejahtera']
    thanks = ['terima kasih', 'makasih', 'thanks', 'thank you', 'trims']

    text_lower = text.lower()

    if any(greet in text_lower for greet in greetings):
        return "greeting"
    elif any(thank in text_lower for thank in thanks):
        return "thankyou"
    else:
        return None

# --- Build Prompt ---
def build_rag_prompt(user_input, matched_context, chat_history=None):
    if not matched_context:
        return None

    history_prompt = ""
    if chat_history:
        for chat in chat_history[-5:]:
            history_prompt += f"User: {chat['user']}\nBot: {chat['bot']}\n"

    system_prompt = (
        "Jawablah pertanyaan pengguna hanya berdasarkan informasi berikut:\n\n"
        + "\n\n".join(matched_context) +
        "\n\nJika tidak ada informasi yang sesuai, jawab: 'Maaf, saya tidak menemukan jawaban yang relevan berdasarkan dokumen yang ada.'\n\n"
        + (f"Riwayat percakapan:\n{history_prompt}" if history_prompt else "") +
        f"\nPertanyaan baru: {user_input}"
    )
    return system_prompt

# --- Core RAG Function ---
def RAG_query(user_input, pasal_isi_list, chat_history=None, threshold=0.3):
    special_response = detect_special_response(user_input)
    if special_response == "greeting":
        response = "Halo! Ada yang bisa saya bantu terkait dokumen ini?"
    elif special_response == "thankyou":
        response = "Sama-sama! Senang bisa membantu."
    else:
        matched_context = retrieve_relevant_context(user_input, pasal_isi_list, threshold)

        if not matched_context:
            response = "Maaf, saya tidak menemukan jawaban yang relevan berdasarkan dokumen yang ada."
        else:
            system_prompt = build_rag_prompt(user_input, matched_context, chat_history)
            response_llm = model.generate_content(system_prompt)
            response = response_llm.text.strip()

    if chat_history is not None:
        chat_history.append({'user': user_input, 'bot': response})
    return response

# --- Streamlit App ---
def main():
    st.set_page_config(page_title="Chatbot RAG Dokumen", layout="centered")
    st.title("📄 Chatbot RAG - Tanya Jawab Berdasarkan Dokumen")

    uploaded_file = st.file_uploader("Unggah file Excel berisi kolom 'Pasal' dan 'Isi'", type=["xlsx"])

    if uploaded_file:
        pasal_isi_list = load_pasal_isi_from_excel(uploaded_file)

        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []

        # Chatbot Interface
        user_input = st.text_input("Tanyakan sesuatu:", key="user_input")

        if user_input:
            response = RAG_query(user_input, pasal_isi_list, st.session_state.chat_history)
            st.session_state.chat_history.append({'user': user_input, 'bot': response})

        # Display chat history
        if st.session_state.chat_history:
            for chat in reversed(st.session_state.chat_history):
                st.markdown(f"**🧑 Kamu:** {chat['user']}")
                st.markdown(f"**🤖 Bot:** {chat['bot']}")

if __name__ == "__main__":
    main()
