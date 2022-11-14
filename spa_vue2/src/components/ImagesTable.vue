<template>
  <v-container class="mt-0 pt-0">
    <v-simple-table class="elevation-4 mx-2">
      <template v-slot:default>
        <thead>
          <tr>
            <th class="text-left">Thumb</th>
            <th class="text-left">Filename</th>
            <th class="text-left">Type</th>
            <th class="text-left">Upload</th>
          </tr>
        </thead>
        <tbody>
          <tr 
            v-for="(thumb, idx) in data" 
            :key="idx" 
            @click="switch_selected(idx)"
            :class="{ 'blue lighten-5': is_selected(idx) }"
          >
            <td class="text-left ">
              <v-img 
                :src="'data:'+thumb.contentType+';base64,'+thumb.b64Data" 
                aspect-ratio="1" 
                width="50"
                height="50"
                class="ma-1"
              ></v-img>
            </td>
            <td class="text-left">{{ thumb.filename }}</td>
            <td class="text-left">{{ thumb.contentType }}</td>
            <td class="text-left">{{ thumb.uploadDate.substring(0,16).replace("T", " - ") }}</td>
          </tr>
        </tbody>
      </template>
    </v-simple-table>
  </v-container>
</template>

<script>
  export default {
    name: 'ImagesTable',
    props:{
      data: Array,
      switch_selected: Function,
      is_selected: Function
    },
    data: () => ({
    
    }),
  }
</script>
