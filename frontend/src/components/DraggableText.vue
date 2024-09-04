<template>
    <div
      @mousedown="startDrag"
      @mousemove="onDrag"
      @mouseup="stopDrag"
      @mouseleave="stopDrag"
      @dblclick="enableEditing"
      :contenteditable="isEditing"
      @blur="disableEditing"
      :style="draggableStyle"
    >
      {{ textContent }}
    </div>
  </template>
  
  <script>
  export default {
    props: {
      initialText: {
        type: String,
        default: 'Draggable Text',
      },
    },
    data() {
      return {
        isDragging: false,
        dragOffset: { x: 0, y: 0 },
        isEditing: false,
        textContent: this.initialText,
        draggableStyle: {
          position: 'absolute',
          cursor: 'move',
          top: '0px',
          left: '0px',
          backgroundColor: 'rgba(0, 0, 0, 0.5)',
          color: 'white',
          padding: '5px',
          zIndex: 10,
        },
      };
    },
    methods: {
      startDrag(event) {
        if (this.isEditing) return;
        this.isDragging = true;
        const textRect = event.target.getBoundingClientRect();
        this.dragOffset = {
          x: event.clientX - textRect.left,
          y: event.clientY - textRect.top,
        };
      },
      stopDrag() {
        this.isDragging = false;
      },
      onDrag(event) {
        if (!this.isDragging || this.isEditing) return;
  
        const containerRect = this.$el.parentElement.getBoundingClientRect();
  
        let newX = event.clientX - containerRect.left - this.dragOffset.x;
        let newY = event.clientY - containerRect.top - this.dragOffset.y;
  
        newX = Math.min(containerRect.width - event.target.offsetWidth, Math.max(0, newX));
        newY = Math.min(containerRect.height - event.target.offsetHeight, Math.max(0, newY));
  
        this.draggableStyle.left = `${newX}px`;
        this.draggableStyle.top = `${newY}px`;
  
        console.log(`Position - X: ${newX}, Y: ${newY}`);
      },
      enableEditing(event) {
        this.isEditing = true;
        this.$nextTick(() => {
          event.target.focus();
        });
      },
      disableEditing(event) {
        this.isEditing = false;
        this.textContent = event.target.textContent;
      },
    },
  };
  </script>
  
  <style scoped>
.draggable {
  position: absolute;
  cursor: move;
  background-color: rgba(0, 0, 0, 0.5);
  color: white;
  padding: 5px;
  z-index: 10;
}
  </style>
  