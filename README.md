# Video Insight AI

**Video Insight AI** is an advanced Streamlit application that uses state-of-the-art generative AI models to extract insights from videos. It offers a comprehensive suite of features including transcription, video analysis, content summarization, roadmap generation, similar content recommendations, and interactive chat assistance—all tailored to the video’s content and intended audience.

## Features

- **Video Upload & Processing:**

  - Upload a video file (mp4, mov, avi) or provide a Google Drive URL.
  - Save uploaded videos locally for processing.

- **Transcription & Translation:**

  - Automatically transcribe the video and, if necessary, translate the transcript to English.
  - Returns both original and translated text along with the detected language.

- **Video Analysis:**

  - Analyze video content using a vision model to extract key metadata such as genre, mood, similar content suggestions, key elements, and recommended audience options.
  - Classify the video as either "Knowledge Analytics" (educational) or "Entertainment Analytics" based on the transcript.

- **Content Generation:**

  - Generate detailed summaries, learning roadmaps, or entertainment analyses based on the video content.
  - Custom prompts allow for tailored responses for different audiences.

- **Chat Assistant:**

  - Engage in a conversational Q&A about the video content.
  - The chat assistant uses the video transcript and analysis context to provide expert responses.

- **Audience Selection:**
  - Choose the target audience for which the content should be tailored, influencing the generated outputs.

## Installation

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/Jnan-py/video-insight-ai.git
   cd video-insight-ai
   ```

2. **Create a Virtual Environment (Recommended):**

   ```bash
   python -m venv venv
   source venv/bin/activate   # On Windows use: venv\Scripts\activate
   ```

3. **Install Dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Set Up Environment Variables:**
   - Create a `.env` file in the project root with your API keys:
     ```
     GEMINI_API=your_google_gemini_api_key_here
     ```

## Usage

1. **Run the Application:**

   ```bash
   streamlit run main.py
   ```

2. **Upload or Link a Video:**

   - Use the sidebar to either upload a video file or enter a Google Drive URL.
   - The app will download (or read) the video, process it, and extract the transcript.

3. **Process the Video:**

   - Click **"Process Video"** to upload the file to the generative AI service.
   - The app will generate the transcript, analyze the video using the vision model, and classify the content (e.g., Knowledge Analytics vs. Entertainment Analytics).

4. **Interact with Video Insights:**
   - **Summary:** Generate a detailed summary of the video content.
   - **Roadmap:** (For educational content) Generate a learning roadmap based on the video.
   - **Similar Content:** (For entertainment content) Get recommendations for similar content.
   - **Transcript:** View the original and translated transcript.
   - **Chat:** Engage in a chat with the AI assistant about the video content.

## Project Structure

```
video-insight-ai/
│
├── main.py                         # Main Streamlit application
├── downloads/                     # Directory for downloaded video files
├── .env                           # Environment variables file (create and add your API keys)
├── README.md                      # Project documentation
└── requirements.txt               # Python dependencies
```

## Technologies Used

- **Streamlit:** Interactive web interface.
- **Google Generative AI (Gemini):** For content generation, transcription, and video analysis.
- **Pinecone:** For vectorizing and indexing video text content.
- **LangChain:** For text splitting and integration with AI models.
- **Python-Dotenv:** For environment variable management.
- **Streamlit Option Menu:** For sidebar navigation.
- **Requests, PIL, Plotly, Matplotlib, NumPy:** For file handling, image processing, and data visualization.

---

Save these files in your project directory. To launch the application, simply run:

```bash
streamlit run main.py
```

Feel free to modify the documentation as needed. Enjoy exploring video insights with Video Insight AI!
