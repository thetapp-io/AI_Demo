## pip install --upgrade google-genai==0.2.2 ##
import asyncio
import json
import os
import websockets
from google import genai
import base64
from prompts import analyses_prompt
# Load API key from environment
os.environ['GOOGLE_API_KEY'] = 'AIzaSyDrXbT__ltXGPRCbpOd8FMZZcq98-CO0Rw'
MODEL = "gemini-2.0-flash-exp"  # use your model ID

client = genai.Client(
  http_options={
    'api_version': 'v1alpha',
  }
)

async def gemini_session_handler(client_websocket: websockets.WebSocketServerProtocol):
    """Handles the interaction with Gemini API within a websocket session.

    Args:
        client_websocket: The websocket connection to the client.
    """
    try:   
        config_message = await client_websocket.recv()
        config_data = json.loads(config_message)
        CONFIG = {
            "generation_config": {"response_modalities": ["AUDIO"]},
            "system_instruction": analyses_prompt#"Your system instruction here"
        }
        # config = config_data.get("setup", {})
        # config["system_instruction"] = analyses_prompt
        # config["generation_config"]["response_modalities"] = ["TEXT"]

        async with client.aio.live.connect(model=MODEL, config=CONFIG) as session:
            print("Connected to Gemini API")

            async def send_to_gemini():
                # import pdb
                # pdb.set_trace()
        
                """Sends messages from the client websocket to the Gemini API."""
                try:
                  async for message in client_websocket:
                    try:
                        data = json.loads(message)

                        if "realtime_input" in data:
                            # if "text_input" in data["realtime_input"]:
                            #     text = data["realtime_input"]["text_input"]
                            #     await session.send(input=text)
                            # else:
                            for chunk in data["realtime_input"]["media_chunks"]:
                                if chunk["mime_type"] == "audio/pcm":
                                    await session.send({"mime_type": "audio/pcm", "data": chunk["data"]})
                                    
                                elif chunk["mime_type"] == "image/jpeg":
                                    await session.send({"mime_type": "image/jpeg", "data": chunk["data"]})
                    except Exception as e:
                            print(f"Error sending to Gemini sdfhgdhfjtj: {e}")
                  print("Client connection closed (send)")
                except Exception as e:
                     print(f"Error sending to Gemini: {e}")
                finally:
                   print("send_to_gemini closed")



            async def receive_from_gemini():
                """Receives responses from the Gemini API and forwards them to the client, looping until turn is complete."""
                full_response = ""
                try:
                    while True:
                        try:
    
                            print("receiving from gemini")
                            async for response in session.receive():
                                # import pdb
                                # pdb.set_trace()

                                #first_response = True
                                print(f"response: {response}")
                                if response.server_content is None:
                                    print(f'Unhandled server message! - {response}')
                                    continue

                                model_turn = response.server_content.model_turn
                                if model_turn:
                                    for part in model_turn.parts:
                                        print(f"part: {part}")
                                        if hasattr(part, 'text') and part.text is not None:
                                            full_response += " " + part.text.strip()
                                        elif hasattr(part, 'inline_data') and part.inline_data is not None:
                                            # if first_response:
                                            print("audio mime_type:", part.inline_data.mime_type)
                                                #first_response = False
                                            base64_audio = base64.b64encode(part.inline_data.data).decode('utf-8')
                                            await client_websocket.send(json.dumps({
                                                "audio": base64_audio,
                                            }))
                                            print("audio received")

                                if response.server_content.turn_complete:
                                    print('\n<Turn complete>')
                                
                            if full_response:
                                print('*************************',full_response,'********************************')
                                formatted_response = " ".join(full_response.split())  # Remove excessive spaces and newlines
                                await client_websocket.send(json.dumps({"text": formatted_response}))
                                full_response = ''
                        except websockets.exceptions.ConnectionClosedOK:
                            print("Client connection closed normally (receive)")
                            break  # Exit the loop if the connection is closed
                        except Exception as e:
                            print(f"Error receiving from Gemini sdgey6uj: {e}")
                            break # exit the lo
                except Exception as e:
                      print(f"Error receiving from Gemini: {e}")
                finally:
                      print("Gemini connection closed (receive)")


            # Start send loop
            send_task = asyncio.create_task(send_to_gemini())
            # Launch receive loop as a background task
            receive_task = asyncio.create_task(receive_from_gemini())
            await asyncio.gather(send_task, receive_task)


    except Exception as e:
        print(f"Error in Gemini session: {e}")
    finally:
        print("Gemini session closed.")


async def main() -> None:
    async with websockets.serve(gemini_session_handler, "0.0.0.0", 443):
        print("Running websocket server 0.0.0.0:443...")
        await asyncio.Future()  # Keep the server running indefinitely


if __name__ == "__main__":
    asyncio.run(main())