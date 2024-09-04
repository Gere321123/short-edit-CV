<template>
  <div>
    <div id="upload">
  <h2>Upload Video</h2>
  <label for="file-upload" class="custom-file-upload">
    Choose File
  </label>
  <input id="file-upload" type="file" @change="onFileChange"/>
</div>

      
<div id="video" v-if="videoId" style="margin-top: 20px;">
    <h3>Upload Successful!</h3>
    <p>Video: {{ videoId }}</p>
    <div style="position: relative; display: inline-block;">
      <div 
        ref="videoContainer"
        style="position: relative; width: 100%;"
      >
        <video
          :src="`http://localhost:5000/uploads/${videoId}`"
          controls
          style="width: 100%; height: auto;"
          ref="videoElement"
        >
          Your browser does not support the video tag.
        </video>

        <DraggableText initialText="Text 1" />

      </div>
    </div>
  </div>
</div>
</template>

<script>
import axios from 'axios';
import DraggableText from './DraggableText.vue';
export default {
  components: {
    DraggableText,
  },
  data() {
    return {
      selectedFile: null,
      videoId: null,
      text: 'Hello',
    };
  },
      

  methods: {
    onFileChange(event) {
      this.selectedFile = event.target.files[0];
      this.uploadVideo();
    },
    async uploadVideo() {
  if (!this.selectedFile || !this.text) return alert('Please select a video file and enter some text.');

  const formData = new FormData();
  formData.append('video', this.selectedFile);
  formData.append('text', this.text);

  try {
    const response = await axios.post('http://localhost:5000/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      },
      responseType: 'blob'
    });

    if (response.status === 200) {
      const responseData = await response.data.text();
      const jsonData = JSON.parse(responseData);
      this.videoId = jsonData.video_id;
    } else {
      alert('Failed to process video.');
    }
  } catch (error) {
    console.error('Error processing video:', error);
    alert('Failed to process video.');
  }
},

  }
};
</script>

<style>



body {
  margin: 0;
  padding: 0;
  font-family: Arial, sans-serif;
  background-color: #2c2c2c;
  color: #ffffff;
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
}


#upload {
  position: absolute;
  text-align: left;
  color: #f1c40f;
  left: 0px;
  top: 0px;
  padding: 150px;
}

#video {
  position: absolute;
  text-align: left;
  color: #f1c40f;
  right: 150px;
  top: 0px;
  padding: 30px;
}

h2, h3, p {
  margin-top: 0;
  color: #f1c40f;
}

input[type="file"] {
  display: block;
  margin-bottom: 20px;
}

button {
  background-color: #e74c3c;
  color: #ffffff;
  padding: 10px 20px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

#file-upload {
  display: none;
}
/* Style the label as a button */
.custom-file-upload {
  background-color: #e74c3c;
  width: 90px;
  color: #ffffff;
  padding: 10px 20px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  transition: background-color 0.3s ease;
  display: inline-block;
}

.custom-file-upload:hover {
  background-color: #c0392b;
}

button:hover {
  background-color: #c0392b;
}

video {
  max-width: 100%;
  height: auto;
  border-radius: 10px;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.5);
}

#upload, #video {
  flex: 1;
  max-width: 50%;
}

#upload {
  margin-right: 20px;
}

#video {
  margin-left: 20px;
}

@media screen and (max-width: 768px) {
  body {
    flex-direction: column;
    padding: 20px;
    height: auto;
  }

  #upload, #video {
    width: 100%;
    max-width: 100%;
    margin: 10px 0;
    padding: 20px 0;
  }

  video {
    width: 100%;
    height: auto;
  }
}
</style>
