<script setup lang="ts">
import Modal from '@/components/data-visualization/Modal.vue'
import { eventList } from '@/utils/events'
import { ref } from 'vue'
import { dvMainStoreWithOut } from '@/store/modules/data-visualization/dvMain'
import { eventStoreWithOut } from '@/store/modules/data-visualization/event'
import { useI18n } from '@/hooks/web/useI18n'
import { storeToRefs } from 'pinia'
const dvMainStore = dvMainStoreWithOut()
const eventStore = eventStoreWithOut()
const { curComponent } = storeToRefs(dvMainStore)
const { t } = useI18n()

const isShowEvent = ref(false)
const eventActiveName = ref('redirect')

const addEvent = (event, param) => {
  isShowEvent.value = false
  eventStore.addEvent({ event, param })
}

const removeEvent = event => {
  eventStore.removeEvent(event)
}
</script>

<template>
  <div class="event-list">
    <div class="div-events">
      <el-button @click="isShowEvent = true">{{ t('visualization.add_event') }}</el-button>
      <div>
        <el-tag
          v-for="event in Object.keys(curComponent.events)"
          :key="event"
          closable
          @close="removeEvent(event)"
        >
          {{ event }}
        </el-tag>
      </div>
    </div>

    <!-- 选择事件 -->
    <Modal v-model="isShowEvent">
      <el-tabs v-model="eventActiveName">
        <el-tab-pane
          v-for="item in eventList"
          :key="item.key"
          :label="item.label"
          :name="item.key"
          style="padding: 0 20px"
        >
          <el-input
            v-if="item.key == 'redirect'"
            v-model="item.param"
            type="textarea"
            :placeholder="t('visualization.input_full_url')"
          />
          <el-input
            v-if="item.key == 'alert'"
            v-model="item.param"
            type="textarea"
            :placeholder="t('visualization.input_alert_content')"
          />
          <el-button style="margin-top: 20px" @click="addEvent(item.key, item.param)">
            {{ t('visualization.confirm') }}
          </el-button>
        </el-tab-pane>
      </el-tabs>
    </Modal>
  </div>
</template>

<style lang="less" scoped>
.event-list {
  .div-events {
    text-align: center;
    padding: 0 20px;

    .ed-button {
      display: inline-block;
      margin-bottom: 10px;
    }

    .ed-tag {
      display: block;
      width: 50%;
      margin: auto;
      margin-bottom: 10px;
    }
  }
}
</style>
