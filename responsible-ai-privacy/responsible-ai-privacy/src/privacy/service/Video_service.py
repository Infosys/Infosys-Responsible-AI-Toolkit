'''
MIT license https://opensource.org/licenses/MIT Copyright 2024 Infosys Ltd

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''

import base64
import io
from typing import Tuple, Dict, Optional, List
import cv2
from PIL import Image
from privacy.service.imagePrivacy import AttributeDict, ImagePrivacy
import numpy as np
from privacy.config.logger import request_id_var
from privacy.config.logger import CustomLogger
import os
import shutil
import threading
import time
import uuid
from concurrent.futures import ThreadPoolExecutor

log = CustomLogger()
path="../video/"
os.makedirs(path,exist_ok=True)
error_dict={}

class VideoService:
        @staticmethod
        def frameAnonymization(payload,frame,indx,results_dict_for_this_chunk, main_request_id,video_request_temp_root_path):
                try:
                    frame_op_log_id = f"frame_{indx}_{uuid.uuid4().hex[:8]}"
                    current_thread_token = None
                    frame_images_specific_dir = os.path.join(video_request_temp_root_path, "anonymization_temp_frames")
                    os.makedirs(frame_images_specific_dir, exist_ok=True)
                    current_thread_token=request_id_var.set(frame_op_log_id)
                    ipath = os.path.join(frame_images_specific_dir, f"{indx}_{frame_op_log_id}.jpg")
                         
                    imagef = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                    imagef.save(ipath)
                    payload_for_image_privacy=payload.copy()
                    payload_for_image_privacy["image"]=AttributeDict({"file": ipath})

                    redacted_image=ImagePrivacy.image_anonymize(payload_for_image_privacy)
                    decoded_bytes = base64.b64decode(redacted_image)

                    # Create a BytesIO object to simulate a file-like object
                    # Use OpenCV (assuming it's an image) or other libraries to load the image from the BytesIO object
                    processed_cv_frame = cv2.imdecode(np.frombuffer(decoded_bytes, np.uint8), cv2.IMREAD_COLOR)
                    if processed_cv_frame is None:
                        log.error(f"[{main_request_id}|{frame_op_log_id}] Frame {indx}: Failed to decode processed image from b64.")
                        results_dict_for_this_chunk[indx] = None
                    else:
                        results_dict_for_this_chunk[indx]=processed_cv_frame
                except Exception as e:
                    log.error(f"[{main_request_id}|{frame_op_log_id}] Exception in frameAnonymization for frame {indx}: {str(e)}")
                    log.error(f"  Line No: {e.__traceback__.tb_lineno}, Function: {e.__traceback__.tb_frame.f_code.co_name}")
                    results_dict_for_this_chunk[indx] = None
                finally:
                    if os.path.exists(ipath):
                        try:
                            os.remove(ipath)
                        except OSError as e_del:
                            log.warning(f"[{main_request_id}|{frame_op_log_id}] Could not delete temp frame image {ipath}: {e_del}")
                    if current_thread_token:
                        request_id_var.reset(current_thread_token)
        async def videoPrivacy(self,payload:dict) -> str:
            main_req_id=uuid.uuid4().hex
            main_req_token=request_id_var.set(main_req_id)
            log.info(f"[{main_req_id}] Starting videoPrivacy process.")
            # Root temporary directory for THIS specific videoPrivacy call
            request_specific_temp_dir = os.path.join(path, main_req_id)
            os.makedirs(request_specific_temp_dir, exist_ok=True)
            temp_input_video_path = os.path.join(request_specific_temp_dir, f"input_video_{main_req_id}.tmp")
            output_video_path = os.path.join(request_specific_temp_dir, f"anonymized_output_{main_req_id}.mp4")
            cap=None
            out_writer=None

            try:     
                payload=AttributeDict(payload)
                upload_file = payload.video
                filename=upload_file.filename
                video_data = await upload_file.read()
                s=time.time()
                with open(temp_input_video_path, "wb") as f_in:
                    f_in.write(video_data)
                del video_data
                log.info(f"[{main_req_id}] Uploaded video saved to {temp_input_video_path}")

                cap = cv2.VideoCapture(temp_input_video_path)
                if not cap.isOpened():
                    raise Exception(f"[{main_req_id}] OpenCV could not open video file: {temp_input_video_path}")
                width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                fps = cap.get(cv2.CAP_PROP_FPS)
                total_frames_approx = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                if fps <= 0: fps = 30.0 # Sensible default
                log.info(f"[{main_req_id}] Video properties: {width}x{height} @ {fps:.2f} FPS, ~{total_frames_approx} frames.")
                sampling_rate=int(fps*0.3)
                  # Define the codec and create a VideoWriter object
                fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                out_writer = cv2.VideoWriter(output_video_path, fourcc, fps, (width, height))
                if not out_writer.isOpened():
                    raise Exception(f"[{main_req_id}] OpenCV could not open VideoWriter for: {output_video_path}")
                log.info(f"[{main_req_id}] Output video writer initialized for {output_video_path}")
                sampling_interval_seconds = 0.3 
                sample_every_n_frames = max(1, int(fps * sampling_interval_seconds)) 
                log.info(f"[{main_req_id}] Sampling: Frame 0 and then 1 frame every {sample_every_n_frames} original frames.")
                  # Chunking: How many original frames to read into memory at once.
                  # E.g., 2 seconds of video frames. Adjust based on typical frame size and memory.
                FRAMES_PER_PROCESSING_CHUNK = int(fps * 2.0) 
                FRAMES_PER_PROCESSING_CHUNK = max(1, min(FRAMES_PER_PROCESSING_CHUNK, int(fps * 10))) # Min 1, Max 10s worth
                log.info(f"[{main_req_id}] Reading video in chunks of up to {FRAMES_PER_PROCESSING_CHUNK} frames.")
                MAX_CONCURRENT_ANONYMIZATION_THREADS = payload.get("max_threads", 6)
                current_original_frame_idx = 0
                last_successfully_anonymized_frame_for_propagation = np.zeros((height, width, 3), dtype=np.uint8)
            
                with ThreadPoolExecutor(max_workers=MAX_CONCURRENT_ANONYMIZATION_THREADS) as executor:
                    while True:
                    # Holds (original_index, frame_data) for the current chunk
                        current_chunk_raw_frames_info: List[Dict] = [] 
                        start_frame_idx_of_chunk = current_original_frame_idx
                    
                        for _ in range(FRAMES_PER_PROCESSING_CHUNK):
                            ret, frame = cap.read()
                            if not ret: # End of video or error
                                break
                            current_chunk_raw_frames_info.append({'idx': current_original_frame_idx, 'data': frame})
                            current_original_frame_idx += 1
                    
                        if not current_chunk_raw_frames_info: # No frames read in this attempt
                            log.info(f"[{main_req_id}] End of video detected. Total frames iterated: {current_original_frame_idx}")
                            break
                    
                        first_idx_in_chunk = current_chunk_raw_frames_info[0]['idx']
                        last_idx_in_chunk = current_chunk_raw_frames_info[-1]['idx']
                        log.info(f"[{main_req_id}] Read chunk of {len(current_chunk_raw_frames_info)} frames (Indices {first_idx_in_chunk}-{last_idx_in_chunk}).")

                        # Identify frames to be sampled and submit for anonymization
                        frames_to_submit_for_anonymization: List[Dict] = []
                        for frame_info in current_chunk_raw_frames_info:
                            original_idx = frame_info['idx']
                            # Your sampling logic: first frame (idx 0) OR every Nth frame
                            if original_idx == 0 or (original_idx % sample_every_n_frames == 0):
                                frames_to_submit_for_anonymization.append(frame_info)
                    
                        log.info(f"[{main_req_id}] Submitting {len(frames_to_submit_for_anonymization)} frames from this chunk for anonymization.")
                    
                        # This dictionary will store results from frameAnonymization for the current chunk
                        processed_frames_map_this_chunk: Dict[int, Optional[np.ndarray]] = {}
                        futures = []
                        if frames_to_submit_for_anonymization:
                            for frame_info_to_anon in frames_to_submit_for_anonymization:
                                future = executor.submit(VideoService.frameAnonymization,
                                                     payload, # The main AttributeDict payload
                                                     frame_info_to_anon['data'], 
                                                     frame_info_to_anon['idx'],
                                                     processed_frames_map_this_chunk, # Results dict for this chunk
                                                     main_req_id, # Main request ID for logging/context
                                                     request_specific_temp_dir) # Root path for frame images
                                futures.append(future)
                        
                            # Wait for all submitted tasks for this chunk to complete
                            for i, f_item in enumerate(futures):
                                try:
                                    f_item.result() # Wait for thread to finish. Result is stored in dict by the thread.
                                                # This will also re-raise exceptions from the thread if not handled there.
                                except Exception as e_future:
                                # This catches exceptions from frameAnonymization if it re-raised them,
                                # or if ThreadPoolExecutor itself had an issue with the task.
                                    failed_frame_original_idx = frames_to_submit_for_anonymization[i]['idx']
                                    log.error(f"[{main_req_id}] Anonymization thread for frame {failed_frame_original_idx} ultimately failed: {e_future}")
                                    # Ensure it's marked as None in the results map if not already.
                                    processed_frames_map_this_chunk[failed_frame_original_idx] = None

                        log.info(f"[{main_req_id}] Anonymization for chunk (frames {first_idx_in_chunk}-{last_idx_in_chunk}) completed.")

                        # Write all frames of the current chunk to output video
                        for frame_info_write in current_chunk_raw_frames_info:
                            idx_write = frame_info_write['idx']
                        
                            frame_for_output_video: Optional[np.ndarray] = None
                        
                            if idx_write in processed_frames_map_this_chunk:
                            # This frame was sampled and an anonymization attempt was made
                                anonymized_version = processed_frames_map_this_chunk[idx_write]
                                if anonymized_version is not None:
                                    frame_for_output_video = anonymized_version
                                # Update last good frame for propagation, ensure it's a copy
                                    last_successfully_anonymized_frame_for_propagation = anonymized_version.copy() 
                        
                            if frame_for_output_video is None:
                            # Frame was not sampled, OR it was sampled but anonymization failed.
                            # Use the last successfully anonymized frame. Ensure it's a copy.
                                frame_for_output_video = last_successfully_anonymized_frame_for_propagation.copy() 
                        
                            out_writer.write(frame_for_output_video)
                    
                        log.info(f"[{main_req_id}] Finished writing chunk (frames {first_idx_in_chunk}-{last_idx_in_chunk}) to output video.")
                    # Memory for this chunk's frames will be released when these go out of scope.
                        del current_chunk_raw_frames_info, processed_frames_map_this_chunk, futures
                        frames_to_submit_for_anonymization.clear()

            # --- End of main processing loop ---
                log.info(f"[{main_req_id}] All video chunks processed. Finalizing.")
                  # Release OpenCV resources BEFORE trying to read the output file
                if cap: cap.release()
                if out_writer: out_writer.release()
                cap, out_writer = None, None # Clear references
                  # Read processed video and encode to base64 for returning
                with open(output_video_path, "rb") as f_out_processed:
                    processed_video_data_bytes = f_out_processed.read()
                video_result_b64 = base64.b64encode(processed_video_data_bytes).decode('utf-8')
                log.info(f"[{main_req_id}] Processed video encoded to base64 string.")

                return video_result_b64
            except Exception as e_main:
                log.error(f"[{main_req_id}] CRITICAL ERROR in videoPrivacy: {str(e_main)}")
                log.error(f"  Line No: {e_main.__traceback__.tb_lineno}, In function: {e_main.__traceback__.tb_frame.f_code.co_name}")
                # Populate your error_dict
                if main_req_id not in error_dict: error_dict[main_req_id] = []
                error_dict[main_req_id].append({
                "UUID": main_req_id, "function": "videoPrivacy_main_handler",
                "msg": str(e_main.__class__.__name__),
                "description": f"{str(e_main)} at Line No:{e_main.__traceback__.tb_lineno}"
                })
                raise # Re-throw to be handled by FastAPI or calling context
            finally:
            # Ensure OpenCV resources are released even on error
                if cap and cap.isOpened(): cap.release()
                if out_writer and out_writer.isOpened(): out_writer.release()
            
            # Cleanup the entire temporary directory for this request
                if os.path.exists(request_specific_temp_dir):
                    try:
                        shutil.rmtree(request_specific_temp_dir)
                        log.info(f"[{main_req_id}] Cleaned up temp directory: {request_specific_temp_dir}")
                    except OSError as e_clean:
                        log.error(f"[{main_req_id}] Error during cleanup of {request_specific_temp_dir}: {e_clean}")
            
            # Reset the main request_id_var context
                if main_req_token:                                                                                                                                                                                  
                    request_id_var.reset(main_req_token)
