<template>
  <v-container class="mt-0 pt-0" v-if="$store.state.images.viewSelected=='thumbs'">
    <v-hover 
      v-for="(thumb, idx) in data" :key="idx"
      v-slot="{ hover }" 
    >
      <v-sheet
        :elevation="hover ? 6 : 2"
        :class="{ 'on-hover': hover, 'blue lighten-4': is_selected(idx) }"
        class="pa-2 ma-3 d-inline-flex"
        style="cursor:pointer;"
        :width="thumWidth"
        
        @click="switch_selected(idx)"
      >
        <v-img
          :src="'data:'+thumb.contentType+';base64,'+thumb.b64Data"
          aspect-ratio="1"
        ></v-img>
      </v-sheet>
    </v-hover>
  </v-container>
</template>

<script>
  export default {
    name: 'ImagesThumbs',
    props:{
      data: Array,
      switch_selected: Function,
      is_selected: Function,
      thumb_width: Number
    },
    data: () => ({
      thumWidth: 140
    }),
    methods:{
      set_thumb_width(){
        if(this.thumb_width){
          this.thumWidth = this.thumb_width
        }
      }
    },
    mounted: function(){
      this.set_thumb_width()
    }
  }
</script>
