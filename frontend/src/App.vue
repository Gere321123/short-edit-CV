<template>
  <UploadVideo />
</template>

<script>
import UploadVideo from './components/UploadVideo.vue';

export default {
  name: 'App',
  components: {
    UploadVideo
  }
}
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  margin-top: 60px;
}
</style>
