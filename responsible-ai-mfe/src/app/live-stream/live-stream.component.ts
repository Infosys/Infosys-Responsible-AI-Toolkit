import { Component, OnInit,OnDestroy } from '@angular/core';
import { urlList } from '../urlList';
import { NonceService } from '../nonce.service';

@Component({
  selector: 'app-live-stream',
  templateUrl: './live-stream.component.html',
  styleUrls: ['./live-stream.component.css']
})
export class LiveStreamComponent implements OnInit {
  videoUrl: string = '';
  isPlaying: boolean = false;
  websocket: WebSocket | undefined;
  frameDataQueue: string[] = [];
  canvas: HTMLCanvasElement | undefined;
  ctx: CanvasRenderingContext2D | undefined;
  showPlayButton: boolean = false;
  errorMessage: string | undefined;
  playbackInterval: any;

  constructor(public nonceService:NonceService){}
    // Initializes the component and sets up the canvas
  ngOnInit(): void {
    this.canvas = document.getElementById('videoCanvas') as HTMLCanvasElement;
    this.ctx = this.canvas.getContext('2d') as CanvasRenderingContext2D;
  }

    // Cleans up resources when the component is destroyed
  ngOnDestroy(): void {
  if (this.websocket) {
    this.websocket.close();
  }
  if (this.playbackInterval) {
    clearInterval(this.playbackInterval);
  }
}

  // Handles the submission of the video URL
  onSubmit(): void {
    if (!this.videoUrl) {
      alert("Please enter a video URL.");
      return;
    }
    this.clearCanvas();
    this.frameDataQueue = [];
    this.errorMessage = undefined;

    if (this.websocket) {
      this.websocket.close();
      this.websocket = undefined;
    }

    this.websocket = new WebSocket(urlList.websocketUrl);

    this.websocket.onopen = () => {
      console.log('Connected to WebSocket server');
      const urlMessage = JSON.stringify({ url: this.videoUrl });
      this.websocket?.send(urlMessage);
      this.isPlaying = true; // Start playing automatically after connection
      this.showPlayButton = true;

      // Buffer frames for 10 milliseconds
      this.bufferFrames(10);
    };

    this.websocket.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data);
        if (message.frame) {
          this.frameDataQueue.push(message.frame); // Store the frame data in the queue
        }
      } catch (error) {
        this.errorMessage = 'Error processing message';
      }
    };

    this.websocket.onclose = () => {
      console.log('Disconnected from WebSocket server');
      this.errorMessage = 'Disconnected from WebSocket server';
      this.isPlaying = false; // Reset play state
    };

    this.websocket.onerror = (error) => {
      console.error('WebSocket error:', error);
      this.isPlaying = false; // Reset play state
    };
  }

  // Buffers frames for a specified duration before starting playback
  private bufferFrames(milliseconds: number): void {
    const bufferStartTime = Date.now();

    // Continue buffering for the specified time (10 milliseconds)
    const bufferInterval = setInterval(() => {
      if (Date.now() - bufferStartTime >= milliseconds) {
        clearInterval(bufferInterval); // Stop buffering after 10 milliseconds
        this.startPlayback(); // Start playback after buffering
      }
    }, 20); // Check every 20 milliseconds

    // Optionally, you can use `setTimeout` to wait before starting playback if needed.
  }
  
  // Toggles between play and pause states
  togglePlayPause(): void {
    this.isPlaying = !this.isPlaying; // Toggle play/pause state

    if (this.isPlaying) {
      this.startPlayback();
    } else {
      if (this.playbackInterval) {
        clearInterval(this.playbackInterval);
      }
    }
  }

  // Resets the component state
  reset(): void {
    this.videoUrl = '';
    this.isPlaying = false;
    this.showPlayButton = false;
    this.errorMessage = undefined;
    this.frameDataQueue = []; // Clear frame data queue
    this.clearCanvas(); 
    if (this.websocket) {
      this.websocket.close();
      this.websocket = undefined;
    }
    if (this.playbackInterval) {
      clearInterval(this.playbackInterval);
    }
  }

  // Clears the canvas
  private clearCanvas(): void {
    if (this.ctx) {
      this.ctx.clearRect(0, 0, this.canvas!.width, this.canvas!.height);
    }
  }

  // Starts playback of the video frames
  private startPlayback(): void {
    if (this.playbackInterval) {
      clearInterval(this.playbackInterval);
    }

    this.playbackInterval = setInterval(() => {
      if (this.frameDataQueue.length > 0) {
        const frameData = this.frameDataQueue.shift();
        if (frameData && this.ctx) {
          const img = new Image();
          img.onload = () => {
            this.ctx?.drawImage(img, 0, 0, this.canvas!.width, this.canvas!.height);
          };
          img.src = 'data:image/jpeg;base64,' + frameData;
        }
      }
    }, 100); // Adjust the interval as needed for smooth playback
  }
}