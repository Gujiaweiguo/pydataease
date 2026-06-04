<template>
  <div class="testcase-template">
    <div class="template-img-container">
      <div class="template-img" :style="classBackground" @click.stop="templateInnerPreview" />
    </div>
    <el-row class="bottom-area"> </el-row>
    <el-row
      class="bottom-area-show"
      :class="{
        'create-area': !canCreateCurrentTemplate
      }"
    >
      <el-row class="demonstration">
        <span class="template-title-text">{{ template.title }}</span>
        <span class="template-action-icons">
          <el-tooltip :content="t('template_manage.export_template')" placement="top">
            <el-icon class="action-icon" @click.stop="handleDownload"><Download /></el-icon>
          </el-tooltip>
          <el-tooltip :content="t('commons.delete')" placement="top">
            <el-icon class="action-icon action-icon-danger" @click.stop="handleDelete"
              ><Delete
            /></el-icon>
          </el-tooltip>
        </span>
      </el-row>
      <el-row class="template-button" v-show="canCreateCurrentTemplate">
        <el-button secondary style="width: calc(50% - 18px)" @click="templateInnerPreview">{{
          t('visualization.preview')
        }}</el-button>
        <el-button style="width: calc(50% - 18px)" type="primary" @click="apply">{{
          t('visualization.apply')
        }}</el-button>
      </el-row>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { useI18n } from '@/hooks/web/useI18n'
import { computed } from 'vue'
import { imgUrlTrans } from '@/utils/imgUtils'
import { hasTemplateCreatePermission } from '@/utils/visualizationResource'
import { Download, Delete } from '@element-plus/icons-vue'
const { t } = useI18n()

const emits = defineEmits([
  'templateApply',
  'templatePreview',
  'templateDownload',
  'templateDelete'
])

const props = defineProps({
  template: {
    type: Object,
    default() {
      return {}
    }
  },
  curPosition: {
    type: String
  },
  baseUrl: {
    type: String
  },
  width: {
    type: Number
  },
  createAuth: {
    type: Object,
    default() {
      return {
        PANEL: false,
        SCREEN: false
      }
    }
  }
})

const classBackground = computed(() => {
  return {
    width: props.width + 'px',
    height: props.width * 0.58 + 'px',
    background: `url(${imgUrlTrans(thumbnailUrl.value)
      .replace(/\(/g, '%28')
      .replace(/\)/g, '%29')}) no-repeat`,
    'background-size': `100% 100%`
  }
})

const thumbnailUrl = computed(() => {
  if (
    props.template.thumbnail.indexOf('http') > -1 ||
    props.template.thumbnail.indexOf('static-resource') > -1
  ) {
    return props.template.thumbnail
  } else {
    return props.baseUrl + props.template.thumbnail
  }
})

const canCreateCurrentTemplate = computed(() =>
  hasTemplateCreatePermission(props.createAuth, props.template?.templateType)
)

const apply = () => {
  emits('templateApply', props.template)
}

const templateInnerPreview = () => {
  emits('templatePreview', props.template.id)
}

const handleDownload = () => {
  emits('templateDownload', props.template)
}

const handleDelete = () => {
  emits('templateDelete', props.template)
}
</script>

<style scoped lang="less">
.testcase-template {
  position: relative;
  display: inline-block;
  margin: 0;
  border: 1px solid rgba(222, 224, 227, 1);
  box-sizing: border-box;
  border-radius: 12px;
  width: 100%;
  background: #fff;
  overflow: hidden;
  &:hover {
    box-shadow: 0px 6px 24px 0px #1f232914;
  }
}

.demonstration {
  height: 34px;
  font-weight: 500;
  display: block;
  font-size: 14px;
  text-align: left;
  padding: 8px 12px 4px 12px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  color: var(--TextPrimary, #1f2329);
}
.template-img-container {
  padding: 4px 4px 0;
  display: flex;
  flex-direction: row;
  justify-content: center;
}
.template-img {
  background-size: 100% 100%;
  border-radius: 6px 4px 0 0;
}

.template-button {
  justify-content: center;
  width: 100%;
  padding-bottom: 8px;
  display: none;
}

.template-title-text {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.template-action-icons {
  display: none;
  align-items: center;
  gap: 6px;
  margin-left: 8px;
  flex-shrink: 0;

  .action-icon {
    font-size: 16px;
    cursor: pointer;
    color: var(--TextSecondary, #646a73);
    padding: 4px;
    border-radius: 4px;

    &:hover {
      background: rgba(31, 35, 41, 0.1);
      color: var(--TextPrimary, #1f2329);
    }

    &.action-icon-danger:hover {
      color: var(--ed-color-danger, #f54a45);
    }
  }
}

.bottom-area {
  height: 38px;
}

.bottom-area-show {
  width: 100%;
  border-top: 1px solid rgba(222, 224, 227, 1);
  position: absolute;
  height: 75px;
  bottom: -38px;
  background: #ffffff;
}

.testcase-template:hover ::v-deep(.bottom-area-show) {
  transition: 0.3s;
  bottom: 0px;
}

.testcase-template:hover ::v-deep(.template-img) {
  outline: solid 1px #4b8fdf;
  color: deepskyblue;
  cursor: pointer;
}
.testcase-template:hover {
  .template-button {
    display: block;
  }
  .template-action-icons {
    display: flex;
  }
}
.create-area {
  bottom: -38px !important;
}

.fix-bottom {
  bottom: -38px !important;
}
</style>
