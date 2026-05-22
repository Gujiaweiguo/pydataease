<script setup lang="ts">
import { PropType, ref, toRefs } from 'vue'
import ComponentWrapper from '@/components/data-visualization/canvas/ComponentWrapper.vue'
import { toPercent } from '@/utils/translate'
import { dvMainStoreWithOut } from '@/store/modules/data-visualization/dvMain'
import UserViewEnlarge from '@/components/visualization/UserViewEnlarge.vue'
const dvMainStore = dvMainStoreWithOut()
const userViewEnlargeRef = ref<any>(null)

type GroupItem = Record<string, any> & {
  id: string
  groupStyle: {
    width: number
    height: number
    top: number
    left: number
  }
}

const props = defineProps({
  propValue: {
    type: Array as PropType<GroupItem[]>,
    default: () => []
  },
  element: {
    type: Object,
    default() {
      return {
        propValue: null
      }
    }
  },
  showPosition: {
    type: String,
    required: false,
    default: 'canvas'
  },
  dvInfo: {
    type: Object as PropType<Record<string, any>>,
    required: true
  },
  // 仪表板刷新计时器
  searchCount: {
    type: Number,
    required: false,
    default: 0
  },
  scale: {
    type: Number,
    required: false,
    default: 1
  },
  canvasViewInfo: {
    type: Object as PropType<Record<string, any>>,
    required: true
  },
  // 字体
  fontFamily: {
    type: String,
    required: false,
    default: 'inherit'
  }
})

const { propValue, dvInfo, searchCount, scale, canvasViewInfo } = toRefs(props)
const customGroupStyle = (item: GroupItem) => {
  return {
    width: toPercent(item.groupStyle.width),
    height: toPercent(item.groupStyle.height),
    top: toPercent(item.groupStyle.top),
    left: toPercent(item.groupStyle.left)
  }
}

const userViewEnlargeOpen = (opt: any, item: GroupItem) => {
  userViewEnlargeRef.value.dialogInit(
    dvMainStore.canvasStyleData,
    canvasViewInfo.value[item.id],
    item,
    opt,
    { scale: scale.value }
  )
}
</script>

<template>
  <div class="group">
    <div>
      <component-wrapper
        v-for="(item, index) in propValue"
        :id="'component' + item.id"
        :canvas-style-data="dvMainStore.canvasStyleData"
        :view-info="canvasViewInfo[item.id]"
        :key="index"
        :config="item"
        :index="index"
        :dv-info="dvInfo"
        :canvas-view-info="canvasViewInfo"
        :style="customGroupStyle(item)"
        :show-position="showPosition"
        :search-count="searchCount"
        :scale="scale"
        :font-family="fontFamily"
        @userViewEnlargeOpen="userViewEnlargeOpen($event, item)"
      />
    </div>
    <user-view-enlarge ref="userViewEnlargeRef"></user-view-enlarge>
  </div>
</template>

<style lang="less" scoped>
.group {
  & > div {
    position: relative;
    width: 100%;
    height: 100%;

    .component {
      position: absolute;
    }
  }
}
</style>
