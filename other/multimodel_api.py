import streamlit as st
from streamlit_webrtc import webrtc_streamer, VideoProcessorBase
import av
import asyncio
from google import genai
import cv2

# genai.configure(api_key='AIzaSyA_BY29JGyth-CmgyG499Jv1d6uME59ACY')

class VideoProcessor(VideoProcessorBase):
    def __init__(self):
        self.frames = []

    def recv(self, frame):
        img = frame.to_ndarray(format="bgr24")
        self.frames.append(img)
        return av.VideoFrame.from_ndarray(img, format="bgr24")
    
def frames_to_video(frames, output_path, fps=20):
    if not frames:
        raise ValueError("No frames to write to video.")

    height, width, _ = frames[0].shape
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    video_writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    for frame in frames:
        video_writer.write(frame)

    video_writer.release()

async def send_video_to_gemini(video_path):
    client = genai.Client(api_key="AIzaSyA_BY29JGyth-CmgyG499Jv1d6uME59ACY", http_options={'api_version': 'v1alpha'})
    model_id = "gemini-2.0-flash-exp"
    config = {"responseModalities": ["TEXT"]}

    async with client.aio.live.connect(model=model_id, config=config) as session:
        with open(video_path, 'rb') as video_file:
            video_data = video_file.read()
            await session.send(input=video_data, end_of_turn=True)

        async for response in session.receive():
            if response.text:
                st.write(response.text)

def main():
    st.title("Real-Time Video Analysis with Gemini API")

    ctx = webrtc_streamer(
        key="example",
        video_processor_factory=VideoProcessor,
        media_stream_constraints={"video": True, "audio": False},
        async_processing=True,
    )

    if ctx.video_processor:
        if st.button("Analyze Video"):
            with st.spinner("Processing..."):
                frames = ctx.video_processor.frames
                if frames:
                    video_path = "captured_video.mp4"
                    frames_to_video(frames, video_path)
                    asyncio.run(send_video_to_gemini(video_path))
                else:
                    st.error("No frames captured. Please try again.")

if __name__ == "__main__":
    main()

# import asyncio
# from google import genai

# client = genai.Client(api_key="AIzaSyA_BY29JGyth-CmgyG499Jv1d6uME59ACY", http_options={'api_version': 'v1alpha'})
# model_id = "gemini-2.0-flash-exp"
# config = {"responseModalities": ["TEXT"]}

# async def main():
#     async with client.aio.live.connect(model=model_id, config=config) as session:
#         while True:
#             message = input("User> ")
#             if message.lower() == "exit":
#                 break
#             await session.send(input=message, end_of_turn=True)

#             async for response in session.receive():
#                 if response.text is None:
#                     continue
#                 print(response.text, end="")

# if __name__ == "__main__":
#     asyncio.run(main())