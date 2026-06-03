<template>
  <el-dialog v-model="state.visible" :title="t('visualization.save_to_panel')" width="480px">
    <el-form
      ref="formRef"
      :model="state.form"
      :rules="state.rules"
      class="de-form-item"
      label-position="top"
    >
      <el-form-item :label="t('template_manage.template_name')" prop="name">
        <el-input
          v-model="state.form.name"
          :maxlength="50"
          :placeholder="t('template_manage.enter_template_name_hint')"
          clearable
          show-word-limit
        />
      </el-form-item>
      <el-form-item :label="t('template_manage.select_catalog')" prop="categoryId">
        <el-select
          v-model="state.form.categoryId"
          :loading="state.loading"
          :no-data-text="t('template_manage.no_selectable_catalog')"
          style="width: 100%"
        >
          <el-option
            v-for="option in state.templateCategories"
            :key="option.id"
            :label="option.name"
            :value="option.id"
          />
        </el-select>
      </el-form-item>
    </el-form>
    <template #footer>
      <div class="dialog-footer">
        <el-button secondary @click="close">{{ t('commons.cancel') }}</el-button>
        <el-button :loading="state.submitLoading" type="primary" @click="submit">
          {{ t('commons.save') }}
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { findCategories } from '@/api/template'
import { useI18n } from '@/hooks/web/useI18n'
import { reactive, ref } from 'vue'

const emit = defineEmits(['submit'])
const { t } = useI18n()
const formRef = ref(null)

const state = reactive({
  visible: false,
  loading: false,
  submitLoading: false,
  templateCategories: [],
  form: {
    name: '',
    categoryId: '',
    dvType: 'dashboard'
  },
  rules: {
    name: [
      {
        required: true,
        message: t('template_manage.template_name_cannot_be_empty'),
        trigger: 'blur'
      },
      {
        max: 50,
        message: t('commons.char_can_not_more_50'),
        trigger: 'change'
      }
    ],
    categoryId: [
      {
        required: true,
        message: t('template_manage.please_select_catalog'),
        trigger: 'change'
      }
    ]
  }
})

const loadCategories = async () => {
  state.loading = true
  try {
    const response = await findCategories({
      dvType: state.form.dvType,
      templateType: 'self',
      level: '0'
    })
    state.templateCategories = response.data || []
    state.form.categoryId = state.templateCategories?.[0]?.id || ''
  } finally {
    state.loading = false
  }
}

const open = async ({ name, dvType = 'dashboard' }) => {
  state.visible = true
  state.submitLoading = false
  state.form.name = name || ''
  state.form.categoryId = ''
  state.form.dvType = dvType
  await loadCategories()
}

const close = () => {
  state.visible = false
  state.submitLoading = false
}

const submit = () => {
  formRef.value?.validate(valid => {
    if (!valid) {
      return false
    }
    state.submitLoading = true
    emit('submit', { ...state.form }, (success = true) => {
      state.submitLoading = false
      if (success) {
        close()
      }
    })
  })
}

defineExpose({
  open,
  close
})
</script>

<style scoped lang="less">
.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  width: 100%;
}
</style>
