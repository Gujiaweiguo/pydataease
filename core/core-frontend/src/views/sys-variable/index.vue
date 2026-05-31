<template>
  <div class="sys-variable-page">
    <div class="page-header">
      <p class="router-title">{{ t('system.variable_list') }}</p>
    </div>

    <div class="sys-variable-container">
      <section class="variable-panel panel-card">
        <div class="panel-header">
          <el-input
            v-model="searchKeyword"
            clearable
            :placeholder="t('common.search_keywords')"
            @input="handleVariableSearch"
            @clear="handleVariableSearch"
          />
          <el-button type="primary" @click="handleAddVariable">
            {{ t('system.add_variable') }}
          </el-button>
        </div>

        <div class="panel-table-wrap">
          <el-table
            :data="variables"
            border
            height="100%"
            row-key="id"
            v-loading="loading"
            highlight-current-row
            :current-row-key="selectedVariableId || undefined"
            @current-change="handleSelectVariable"
          >
            <el-table-column
              prop="name"
              :label="t('system.variable_name')"
              min-width="140"
              show-overflow-tooltip
            />
            <el-table-column :label="t('system.variable_type')" width="120">
              <template #default="{ row }">
                <span>{{ getVariableTypeLabel(row.type) }}</span>
              </template>
            </el-table-column>
            <el-table-column
              prop="remark"
              :label="t('system.variable_desc')"
              min-width="160"
              show-overflow-tooltip
            />
            <el-table-column :label="t('common.operate')" width="120" fixed="right">
              <template #default="{ row }">
                <el-button link type="primary" @click.stop="handleEditVariable(row)">
                  {{ t('common.edit') }}
                </el-button>
                <el-button link type="danger" @click.stop="handleDeleteVariable(row)">
                  {{ t('common.delete') }}
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </section>

      <section v-if="selectedVariableId" class="value-panel panel-card">
        <div class="panel-header panel-header--values">
          <div class="panel-title-group">
            <h3>{{ currentVariableTitle }}</h3>
            <p>{{ t('system.set_variable_value') }}</p>
          </div>
          <div class="panel-actions">
            <el-input
              v-model="valueSearchKeyword"
              clearable
              :placeholder="t('system.search_variable_value')"
              @input="handleValueSearch"
              @clear="handleValueSearch"
            />
            <el-button type="primary" @click="handleAddValue">
              {{ t('system.add_variable_value') }}
            </el-button>
            <el-button :disabled="selectedValueIds.length === 0" @click="handleBatchDelete">
              {{ t('user.batch_del') }}
            </el-button>
          </div>
        </div>

        <div class="panel-table-wrap">
          <el-table
            :data="values"
            border
            height="100%"
            v-loading="valueLoading"
            @selection-change="handleValueSelectionChange"
          >
            <el-table-column type="selection" width="48" />
            <el-table-column
              prop="value"
              :label="t('system.variable_value')"
              min-width="180"
              show-overflow-tooltip
            />
            <el-table-column
              prop="name"
              :label="t('common.name')"
              min-width="140"
              show-overflow-tooltip
            />
            <el-table-column
              prop="remark"
              :label="t('system.variable_desc')"
              min-width="180"
              show-overflow-tooltip
            />
            <el-table-column :label="t('common.operate')" width="120" fixed="right">
              <template #default="{ row }">
                <el-button link type="primary" @click="handleEditValue(row)">
                  {{ t('common.edit') }}
                </el-button>
                <el-button link type="danger" @click="handleDeleteValue(row)">
                  {{ t('common.delete') }}
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>

        <div v-if="valueTotal > valuePageSize" class="pagination-wrap">
          <el-pagination
            v-model:current-page="valuePage"
            v-model:page-size="valuePageSize"
            background
            layout="total, prev, pager, next"
            :total="valueTotal"
            @current-change="handleValuePageChange"
          />
        </div>
      </section>

      <section v-else class="value-panel-empty panel-card">
        <el-empty :description="t('system.on_the_left_p')" />
      </section>
    </div>

    <el-dialog
      v-model="editDialogVisible"
      :title="isEdit ? t('system.edit_variable') : t('system.add_variable')"
      width="500px"
      append-to-body
      @closed="resetVariableForm"
    >
      <el-form ref="editFormRef" :model="editForm" :rules="editFormRules" label-position="top">
        <el-form-item :label="t('system.variable_name')" prop="name">
          <el-input v-model="editForm.name" :disabled="isEdit" maxlength="100" />
        </el-form-item>
        <el-form-item :label="t('common.name')" prop="alias">
          <el-input v-model="editForm.alias" maxlength="100" />
        </el-form-item>
        <el-form-item :label="t('system.variable_type')" prop="type">
          <el-select v-model="editForm.type" style="width: 100%">
            <el-option
              v-for="item in variableTypeOptions"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item :label="t('system.variable_desc')" prop="remark">
          <el-input v-model="editForm.remark" type="textarea" :rows="3" maxlength="255" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editDialogVisible = false">{{ t('common.cancel') }}</el-button>
        <el-button type="primary" @click="handleSaveVariable">{{ t('common.sure') }}</el-button>
      </template>
    </el-dialog>

    <el-dialog
      v-model="valueEditDialogVisible"
      :title="isValueEdit ? t('system.edit_variable_value') : t('system.add_variable_value')"
      width="500px"
      append-to-body
      @closed="resetValueForm"
    >
      <el-form
        ref="valueEditFormRef"
        :model="valueEditForm"
        :rules="valueEditFormRules"
        label-position="top"
      >
        <el-form-item :label="t('system.variable_value')" prop="value">
          <el-input v-model="valueEditForm.value" maxlength="255" />
        </el-form-item>
        <el-form-item :label="t('common.name')" prop="name">
          <el-input v-model="valueEditForm.name" maxlength="100" />
        </el-form-item>
        <el-form-item :label="t('system.variable_desc')" prop="remark">
          <el-input v-model="valueEditForm.remark" type="textarea" :rows="3" maxlength="255" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="valueEditDialogVisible = false">{{ t('common.cancel') }}</el-button>
        <el-button type="primary" @click="handleSaveValue">{{ t('common.sure') }}</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script lang="ts" setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus-secondary'
import type { FormInstance, FormRules } from 'element-plus-secondary'
import { useI18n } from '@/hooks/web/useI18n'
import {
  batchDelApi,
  searchVariableApi,
  valueSelectedForVariableApi,
  variableCreateApi,
  variableDeletelApi,
  variableDetailApi,
  variableEditApi,
  variableValueCreateApi,
  variableValueDeletelApi,
  variableValueEditApi
} from '@/api/variable'

interface VariableItem {
  id: number
  name: string
  alias?: string
  type: string
  remark?: string
}

interface VariableValueItem {
  id: number
  variableId: number
  value: string
  name?: string
  remark?: string
}

const { t } = useI18n()

const variables = ref<VariableItem[]>([])
const selectedVariable = ref<VariableItem | null>(null)
const selectedVariableId = ref<number | null>(null)
const searchKeyword = ref('')
const loading = ref(false)
const editDialogVisible = ref(false)
const editFormRef = ref<FormInstance>()
const isEdit = ref(false)
const variableEditingId = ref<number | null>(null)
const variableOriginalType = ref('text')

const values = ref<VariableValueItem[]>([])
const valueTotal = ref(0)
const valuePage = ref(1)
const valuePageSize = ref(10)
const valueSearchKeyword = ref('')
const selectedValueIds = ref<number[]>([])
const valueEditDialogVisible = ref(false)
const valueEditFormRef = ref<FormInstance>()
const isValueEdit = ref(false)
const valueEditingId = ref<number | null>(null)
const valueLoading = ref(false)

const editForm = reactive({
  name: '',
  alias: '',
  type: 'text',
  remark: ''
})

const valueEditForm = reactive({
  value: '',
  name: '',
  remark: ''
})

const variableTypeOptions = computed(() => [
  { label: t('data_set.text'), value: 'text' },
  { label: t('data_fill.database.number'), value: 'number' },
  { label: t('data_fill.database.datetime'), value: 'date' },
  { label: t('data_fill.form.list'), value: 'list' }
])

const currentVariableTitle = computed(() => {
  const variable = selectedVariable.value
  if (!variable) {
    return ''
  }
  return variable.alias || variable.name
})

const editFormRules: FormRules = {
  name: [
    { required: true, message: t('common.required'), trigger: 'blur' },
    {
      pattern: /^[a-zA-Z][a-zA-Z0-9_]{0,99}$/,
      message: t('common.letter_start'),
      trigger: 'blur'
    }
  ],
  type: [{ required: true, message: t('common.please_select'), trigger: 'change' }]
}

const valueEditFormRules: FormRules = {
  value: [{ required: true, message: t('user.cannot_be_empty'), trigger: 'blur' }]
}

function normalizeResponseData<T>(response: unknown, fallback: T): T {
  if (response && typeof response === 'object' && 'data' in response) {
    return ((response as { data?: T }).data ?? fallback) as T
  }
  return (response as T) ?? fallback
}

const getVariableTypeLabel = (type: string) => {
  const match = variableTypeOptions.value.find(item => item.value === type)
  return match?.label || type
}

const resetVariableForm = () => {
  variableEditingId.value = null
  variableOriginalType.value = 'text'
  editForm.name = ''
  editForm.alias = ''
  editForm.type = 'text'
  editForm.remark = ''
  editFormRef.value?.clearValidate()
}

const resetValueForm = () => {
  valueEditingId.value = null
  valueEditForm.value = ''
  valueEditForm.name = ''
  valueEditForm.remark = ''
  valueEditFormRef.value?.clearValidate()
}

const loadVariables = async () => {
  loading.value = true
  try {
    const response = await searchVariableApi({ keyword: searchKeyword.value.trim() })
    const list = normalizeResponseData<VariableItem[]>(response, [])
    variables.value = Array.isArray(list) ? list : []
    if (selectedVariableId.value) {
      const matched = variables.value.find(item => item.id === selectedVariableId.value) || null
      selectedVariable.value = matched
      if (!matched) {
        selectedVariableId.value = null
        values.value = []
        valueTotal.value = 0
        selectedValueIds.value = []
      }
    }
  } finally {
    loading.value = false
  }
}

const loadValues = async () => {
  if (!selectedVariableId.value) {
    values.value = []
    valueTotal.value = 0
    return
  }
  valueLoading.value = true
  try {
    const response = await valueSelectedForVariableApi(valuePage.value, valuePageSize.value, {
      variableId: selectedVariableId.value,
      keyword: valueSearchKeyword.value.trim()
    })
    const pageData = normalizeResponseData<{
      records?: VariableValueItem[]
      total?: number
      page?: number
      pageSize?: number
    }>(response, {})
    values.value = pageData.records || []
    valueTotal.value = pageData.total || 0
    selectedValueIds.value = []
  } finally {
    valueLoading.value = false
  }
}

const handleVariableSearch = () => {
  loadVariables()
}

const handleValueSearch = () => {
  valuePage.value = 1
  loadValues()
}

const handleSelectVariable = async (variable: VariableItem | null) => {
  if (!variable?.id) {
    return
  }
  selectedVariableId.value = variable.id
  valuePage.value = 1
  selectedValueIds.value = []
  const response = await variableDetailApi(variable.id)
  selectedVariable.value = normalizeResponseData<VariableItem | null>(response, variable)
  await loadValues()
}

const handleAddVariable = () => {
  isEdit.value = false
  resetVariableForm()
  editDialogVisible.value = true
}

const handleEditVariable = async (variable: VariableItem) => {
  isEdit.value = true
  resetVariableForm()
  const response = await variableDetailApi(variable.id)
  const detail = normalizeResponseData<VariableItem | null>(response, variable)
  variableEditingId.value = variable.id
  variableOriginalType.value = detail?.type || variable.type || 'text'
  editForm.name = detail?.name || ''
  editForm.alias = detail?.alias || ''
  editForm.type = detail?.type || 'text'
  editForm.remark = detail?.remark || ''
  editDialogVisible.value = true
}

const handleSaveVariable = async () => {
  if (!editFormRef.value) {
    return
  }
  const valid = await editFormRef.value.validate().catch(() => false)
  if (!valid) {
    return
  }

  if (isEdit.value && editForm.type !== variableOriginalType.value) {
    await ElMessageBox.confirm(t('system.to_change_it'), {
      type: 'warning',
      confirmButtonText: t('common.sure'),
      cancelButtonText: t('common.cancel')
    })
  }

  const payload = {
    ...(isEdit.value && variableEditingId.value ? { id: variableEditingId.value } : {}),
    name: editForm.name.trim(),
    alias: editForm.alias.trim(),
    type: editForm.type,
    remark: editForm.remark.trim()
  }

  const currentEditingId = variableEditingId.value

  if (isEdit.value) {
    await variableEditApi(payload)
  } else {
    await variableCreateApi(payload)
  }

  ElMessage.success(t('common.save_success'))
  editDialogVisible.value = false
  await loadVariables()

  if (isEdit.value && currentEditingId === selectedVariableId.value) {
    const current = variables.value.find(item => item.id === selectedVariableId.value) || null
    selectedVariable.value = current
    valuePage.value = 1
    await loadValues()
  }
}

const handleDeleteVariable = async (variable: VariableItem) => {
  await ElMessageBox.confirm(t('system.delete_this_variable'), {
    type: 'warning',
    confirmButtonText: t('common.sure'),
    cancelButtonText: t('common.cancel')
  })
  await variableDeletelApi(variable.id)
  ElMessage.success(t('common.delete_success'))

  const isCurrent = selectedVariableId.value === variable.id
  if (isCurrent) {
    selectedVariable.value = null
    selectedVariableId.value = null
    values.value = []
    valueTotal.value = 0
    selectedValueIds.value = []
    valueSearchKeyword.value = ''
  }

  await loadVariables()
}

const handleAddValue = () => {
  if (!selectedVariableId.value) {
    return
  }
  isValueEdit.value = false
  resetValueForm()
  valueEditDialogVisible.value = true
}

const handleEditValue = (value: VariableValueItem) => {
  isValueEdit.value = true
  resetValueForm()
  valueEditingId.value = value.id
  valueEditForm.value = value.value || ''
  valueEditForm.name = value.name || ''
  valueEditForm.remark = value.remark || ''
  valueEditDialogVisible.value = true
}

const handleSaveValue = async () => {
  if (!valueEditFormRef.value || !selectedVariableId.value) {
    return
  }
  const valid = await valueEditFormRef.value.validate().catch(() => false)
  if (!valid) {
    return
  }

  const payload = {
    ...(isValueEdit.value && valueEditingId.value ? { id: valueEditingId.value } : {}),
    variableId: selectedVariableId.value,
    value: valueEditForm.value.trim(),
    name: valueEditForm.name.trim(),
    remark: valueEditForm.remark.trim()
  }

  if (isValueEdit.value) {
    await variableValueEditApi(payload)
  } else {
    await variableValueCreateApi(payload)
  }

  ElMessage.success(t('common.save_success'))
  valueEditDialogVisible.value = false
  valuePage.value = 1
  await loadValues()
}

const handleDeleteValue = async (value: VariableValueItem) => {
  await ElMessageBox.confirm(t('system.this_variable_value'), {
    type: 'warning',
    confirmButtonText: t('common.sure'),
    cancelButtonText: t('common.cancel')
  })
  await variableValueDeletelApi(value.id)
  ElMessage.success(t('common.delete_success'))
  if (values.value.length === 1 && valuePage.value > 1) {
    valuePage.value -= 1
  }
  await loadValues()
}

const handleBatchDelete = async () => {
  if (!selectedValueIds.value.length) {
    return
  }
  await ElMessageBox.confirm(t('system.this_variable_value'), {
    type: 'warning',
    confirmButtonText: t('common.sure'),
    cancelButtonText: t('common.cancel')
  })
  await batchDelApi({ ids: selectedValueIds.value })
  ElMessage.success(t('common.delete_success'))
  if (selectedValueIds.value.length >= values.value.length && valuePage.value > 1) {
    valuePage.value -= 1
  }
  await loadValues()
}

const handleValueSelectionChange = (rows: VariableValueItem[]) => {
  selectedValueIds.value = rows.map(row => row.id)
}

const handleValuePageChange = (page: number) => {
  valuePage.value = page
  loadValues()
}

onMounted(async () => {
  await loadVariables()
  if (variables.value.length) {
    await handleSelectVariable(variables.value[0])
  }
})
</script>

<style lang="less" scoped>
.sys-variable-page {
  padding: 16px 24px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.sys-variable-container {
  display: flex;
  gap: 16px;
  height: calc(100vh - 180px);
  min-height: 560px;
}

.panel-card {
  background: var(--ContentBG, #ffffff);
  border-radius: 4px;
  padding: 16px;
}

.variable-panel {
  width: 45%;
  min-width: 400px;
  display: flex;
  flex-direction: column;
}

.value-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.value-panel-empty {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;

  .el-input {
    max-width: 240px;
  }
}

.panel-header--values {
  align-items: flex-start;
}

.panel-title-group {
  min-width: 0;

  h3 {
    margin: 0;
    font-size: 16px;
    line-height: 24px;
    color: var(--MainTextColor, #1f2329);
  }

  p {
    margin: 4px 0 0;
    font-size: 14px;
    line-height: 22px;
    color: var(--deTextSecondary, #646a73);
  }
}

.panel-actions {
  display: flex;
  align-items: center;
  gap: 8px;

  .el-input {
    width: 220px;
  }
}

.panel-table-wrap {
  flex: 1;
  min-height: 0;
}

.pagination-wrap {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}
</style>
