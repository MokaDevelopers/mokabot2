<template>
  <div class="qq-chat">
    <v-app>
      <v-main>
        <br>
        <v-card class="elevation-6">
          <v-toolbar color="primary" dark dense flat>
            <v-row no-gutters justify="space-between">
              <v-col cols="auto">
                <div class="center">
                  <v-icon small>fa-chevron-left</v-icon>
                  &nbsp;&nbsp;&nbsp;&nbsp;
                </div>
              </v-col>
              <v-col cols="auto">
                <div class="center">
                  <v-col>
                    <v-row no-gutters>
                      <v-col>
                        <h4 class="white--text" align="center">🔥 mokabot</h4>
                      </v-col>
                    </v-row>
                    <v-row no-gutters>
                      <v-col>
                        <h6 class="white--text" align="center">🟢 手机在线 - 2G ></h6>
                      </v-col>
                    </v-row>
                  </v-col>
                </div>
              </v-col>
              <v-col class="text-right" cols="auto">
                <div class="center">
                  <v-icon small>fa-phone-alt</v-icon>
                  &nbsp;&nbsp;
                  <v-icon small>fa-bars</v-icon>
                </div>
              </v-col>
            </v-row>
          </v-toolbar>
          <v-container fluid ref="chat" class="chat chat-bg">
            <template v-for="(item, index) in messages">
              <v-row
                  v-if="item.position === 'right'"
                  justify="end"
                  :key="index"
                  class="message wow animate__fadeInRight"
                  data-wow-duration="0.7s"
              >
                <div
                    class="message-box"
                    v-html="
                    item.msg.replace(/\n/g, '<br/>').replace(/ /g, '&nbsp;')
                  "
                ></div>
                <v-avatar color="blue lighten-2" size="36">
                  <h4>😅</h4>
                </v-avatar>
              </v-row>
              <v-row
                  v-else-if="item.position === 'left'"
                  justify="start"
                  :key="index"
                  class="message wow animate__fadeInLeft"
                  data-wow-duration="0.7s"
              >
                <v-avatar color="transparent" size="36">
                  <v-img src="/images/profile.jpg"></v-img>
                </v-avatar>
                <div
                    class="message-box"
                    v-html="
                    item.msg.replace(/\n/g, '<br/>').replace(/ /g, '&nbsp;')
                  "
                ></div>
              </v-row>
              <v-row
                  v-else
                  justify="center"
                  :key="index"
                  class="notify mt-1 wow animate__fadeIn"
                  data-wow-duration="0.7s"
              >
                <div class="notify-box">
                  <span
                      v-html="
                      item.msg.replace(/\n/g, '<br/>').replace(/ /g, '&nbsp;')
                    "
                  ></span>
                </div>
              </v-row>
            </template>
          </v-container>
          <v-container fluid class="chat-bg py-0">
            <v-row dense class="mx-0">
              <v-col>
                <v-text-field
                    dense
                    solo
                    hide-details
                    height="28px"
                ></v-text-field>
              </v-col>
              <v-col cols="auto">
                <v-btn
                    style="font-size: 0.8rem"
                    color="primary"
                    small
                    rounded
                    depressed
                >发送
                </v-btn
                >
              </v-col>
            </v-row>
            <v-row class="text-center" no-gutters>
              <v-col class="pa-1" cols="2">
                <v-icon small>fa-microphone</v-icon>
              </v-col>
              <v-col class="pa-1" cols="2">
                <v-icon small>fa-image</v-icon>
              </v-col>
              <v-col class="pa-1" cols="2">
                <v-icon small>fa-camera</v-icon>
              </v-col>
              <v-col class="pa-1" cols="2">
                <v-icon small>fa-wallet</v-icon>
              </v-col>
              <v-col class="pa-1" cols="2">
                <v-icon small>fa-smile-wink</v-icon>
              </v-col>
              <v-col class="pa-1" cols="2">
                <v-icon small>fa-plus-circle</v-icon>
              </v-col>
            </v-row>
          </v-container>
        </v-card>
        <br>
      </v-main>
    </v-app>
  </div>
</template>

<script>
import {WOW} from "wowjs";
import "animate.css/animate.min.css";

export default {
  name: "Messenger",
  props: {
    messages: {
      type: Array,
      default: () => [],
    },
  },
  methods: {
    initWOW: function () {
      new WOW({
        noxClass: "wow",
        animateClass: "animate__animated",
        offset: 0,
        mobile: true,
        live: true,
      }).init();
    },
  },
  mounted() {
    this.initWOW();
  },
};
</script>

<style scoped>
.wow {
  visibility: hidden;
}

.chat {
  min-height: 150px;
  overflow-x: hidden;
}

.chat-bg {
  background-color: #f3f6f9;
}

.message {
  position: relative;
  margin: 0;
}

.message .message-box {
  position: relative;
  width: fit-content;
  max-width: 55%;
  border-radius: 0.5rem;
  padding: 0.6rem 0.8rem;
  margin: 0.4rem 0.8rem;
  background-color: #fff;
}

.message .message-box::after {
  content: "";
  position: absolute;
  right: 100%;
  top: 0;
  width: 8px;
  height: 12px;
  color: #fff;
  border: 0 solid transparent;
  border-bottom: 7px solid;
  border-radius: 0 0 0 8px;
}

.message.justify-end .message-box::after {
  left: 100%;
  right: auto;
  border-radius: 0 0 8px 0;
}

.notify {
  position: relative;
}

.notify .notify-box {
  max-width: 70%;
  background: #e0e0e0;
  border-radius: 10px;
  padding: 5px 12px;
  font-size: 12px;
  margin-bottom: 16px;
}
</style>

<style>
.v-application--wrap {
  min-height: 0 !important;
}

.center {
  display: flex;
  text-align: center;
  height: 100%;
}
</style>
