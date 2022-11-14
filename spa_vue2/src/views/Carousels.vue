<template>
  <div class="Carousels">
    <!-- -------------------------------------------------- -->
    <v-card class="ma-6 mt-10 pa-4 elevation-6">
      <v-card-title class="py-2 px-3 text-h7 ">
        <v-row>
          <v-col>Your Carousels</v-col>
          <v-col class="text-right">
            <v-btn 
              small
              fab
              class="purple darken-4 white--text"
              @click="dialogAdd = !dialogAdd"
            >
              <v-icon dark>mdi-plus</v-icon>
            </v-btn>
          </v-col>
          
        </v-row>
      </v-card-title>
      <v-data-table
        :headers="tableHeaders"
        :items="$store.state.dataStore.carousels"
        :search="search"
      >
        <template v-slot:[`item.imgLen`]="{item}">
          <div v-if="item.images">{{item.images.length}}</div>
          <div v-else>0</div>
        </template>
        <template v-slot:[`item.act`]="{item}">
          <v-btn light icon @click="open_dialog_carousel($store.state.dataStore.carousels.indexOf(item))">
            <v-icon>mdi-pencil</v-icon>
          </v-btn>
        </template>
      
      </v-data-table>
    </v-card>

    <!-- -------------------------------------------------- -->
    <v-dialog v-model="dialogAdd" max-width="600px" >
      <form @submit.prevent="submit_add">
        <v-card class="" >
          <v-card-title class="purple darken-3 white--text mb-2">
            Add new Carousel
          </v-card-title>
          <v-card-text class="pt-6" >
            <v-text-field
              v-model="carouselAdd.name"
              label="Carousel Name"
              class="pa-3" 
              required 
            ></v-text-field>
            <v-text-field
              v-model="carouselAdd.description"
              label="Short Description"
              class="pa-3"  
            ></v-text-field>
            <v-select 
              class="pa-3" 
              required 
              label="Switch Mode" 
              v-model="carouselAdd.mode" 
              :items="ddMode"
              >
            </v-select>
            <v-select 
              class="pa-3" 
              required 
              label="State" 
              v-model="carouselAdd.state" 
              :items="ddState"
              >
            </v-select>
            <v-slider
              v-model="carouselAdd.timeout"
              class="pa-3 mt-3" 
              step="1"
              min="1"
              max="30"
              thumb-label
              label="Switch Time" 
              ticks
            ></v-slider>
          </v-card-text>

          <v-card-actions>
            <v-container class="text-center">
              <v-btn
                dark 
                class="purple darken-3 mx-4" 
                min-width="120"
                type="submit"
              >Submit</v-btn>
              <v-btn
                dark 
                class="grey darken-2 mx-4"
                min-width="120"
                type="button"
                @click="close_dialog_add"
              >Close</v-btn>
            </v-container>
          </v-card-actions>
        </v-card>
      </form>
    </v-dialog>

    <!-- -------------------------------------------------- -->
    <v-dialog
      v-model="dialogConfig"
      fullscreen
      hide-overlay
      transition="dialog-bottom-transition"
      scrollable
      >
      <v-card title>
        <v-toolbar flat dark color="purple darken-3" >
          <v-btn icon dark @click="dialogConfig = !dialogConfig" type="button">
            <v-icon>mdi-close</v-icon>
          </v-btn>
          <v-toolbar-title>Carousel Configuration: {{this.carouselConfig.name}}</v-toolbar-title>
          <v-spacer></v-spacer>
          <v-toolbar-items >
            <v-btn icon dark type="submit">Save</v-btn>
          </v-toolbar-items>
        </v-toolbar>

        <v-card-text class="text-left px-1" >
          <div style="height:210px; overflow:auto;">
          <v-sheet
            class="pa-2 ma-3 d-inline-flex elevation-4"
            style="cursor:pointer;"
            :width="80"
            v-for="(thumb,idx) in $store.state.dataStore.thumbs" :key="idx"
          >
            <v-img
              :src="'data:'+thumb.contentType+';base64,'+thumb.b64Data"
              aspect-ratio="1"
              @click="print_something(idx)"
            ></v-img>
          </v-sheet>
          </div>
        </v-card-text>


        <v-card-text class="text-center">
          <v-btn 
            small
            dark
            color="blue-grey darken-4" 
            min-width="140"
            @click="dialogDelete = !dialogDelete"
            class="mx-4">Delete Carousel</v-btn>
        </v-card-text>

      </v-card>
    </v-dialog>

    <!-- -------------------------------------------------- -->
    <!-- -------------------------------------------------- -->
    <v-dialog
      v-model="dialogDelete"
      max-width="500px"
    >
      <v-card class="pb-6">
        <v-card-title class="purple darken-3 white--text mb-6">
          Delete carousel "{{carouselConfig.name}}"?
        </v-card-title>
        <v-card-actions>
          <v-container class="text-center">
            <v-btn
              dark 
              class="purple darken-3 mx-4" 
              min-width="120"
              type="submit"
              @click="submit_carousel_delete"
            >Submit</v-btn>
            <v-btn
              dark 
              class="grey darken-1 mx-4"
              min-width="120"
              type="button"
              @click="dialogDelete = !dialogDelete"
            >Close</v-btn>
          </v-container>
        </v-card-actions>
      </v-card>
    </v-dialog>
    
    
    <!-- -------------------------------------------------- -->
   
  </div>
</template>


<script>
  // import HelloWorld from '../components/HelloWorld'
  import axios from 'axios'
  import { mapMutations } from 'vuex'
  import ImagesThumbs from '../components/ImagesThumbs'

  export default {
    name: 'Carousels',
    components: {
      ImagesThumbs,
    },
    data: () => ({
      title: "Carousels",
      tableHeaders: [
        { text: 'Name', value: 'name' },
        { text: 'Description', value: 'description' },
        { text: 'Switch Mode', value: 'mode' },
        { text: 'Switch Time', value: 'timeout' },
        { text: 'Images', value: 'imgLen' },
        { text: 'Action', value: 'act' }
      ],
      search: null,

      dialogAdd: false,
      dialogConfig: false,
      dialogDelete: false,

      carouselConfig: {},
      carouselAdd: {},
      carouselAddTmp: { 
        state:"private",
        mode:"fade",
        timeout: 5,
        // images:[]
      },
      ddMode:[
        {
          text: "Fade",
          value: "fade"
        },
        {
          text: "Slide",
          value: "slide"
        }
      ],
      ddState:[
        {
          text: "Private",
          value: "private"
        },
        {
          text: "Public",
          value: "public"
        },
        {
          text: "Disabled ",
          value: "disabled "
        }
      ],

    }),
  

    methods:{
      ...mapMutations([ "set_err", "reset_err", 'add_carousel', "remove_carousel_by_item" ]),

      //-------------------------------------------
      submit_add(){
        // console.log(this.carouselAdd);
        axios.post(
          "/api/carousels", 
          this.carouselAdd,
          this.$store.getters.create_bearer_auth_header
        )
        .then((res)=>{
          // console.log(res.data._id)
          let newItem = {...this.carouselAdd}
          newItem._id = res.data._id
          this.add_carousel(newItem)
        })
        .catch((err)=>{
          this.set_err(err.message)
        })
        .finally(()=>{
          this.close_dialog_add()
        })
      },

      //-------------------------------------------
      close_dialog_add(){
        this.dialogAdd = false;
        this.carouselAdd = {...this.carouselAddTmp}
      },

      //-------------------------------------------
      submit_carousel_delete(){
        axios.delete(
          "/api/carousels/"+this.carouselConfig._id, 
          this.$store.getters.create_bearer_auth_header
        )
        .then((res)=>{
          this.dialogDelete = false
          this.dialogConfig = false
          this.remove_carousel_by_item(this.carouselConfig)
        })
        .catch((err)=>{
          this.set_err(err.message)
        })
      },


      //-------------------------------------------
      open_dialog_carousel(idx){
        this.carouselConfig = {...this.$store.state.dataStore.carousels[idx]}
        this.dialogConfig = true

      },

      //-------------------------------------------
      is_selected(idx){
        return false
      },

      //-------------------------------------------
      print_something(msg){
        console.log(msg)
      },
      //-------------------------------------------


    },
    mounted: function(){
      this.carouselAdd = {...this.carouselAddTmp}
    }
  }
</script>