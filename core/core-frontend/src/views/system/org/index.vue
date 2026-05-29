<template>
  <div class="system-page" v-loading="loading">
    <div class="page-header">
      <p class="router-title">组织管理</p>
      <div class="actions">
        <el-button type="primary" @click="openCreateDialog">新增组织</el-button>
        <el-button :disabled="!selectedOrg || selectedOrg.id === '0'" @click="openEditDialog"
          >编辑</el-button
        >
        <el-button
          :disabled="!selectedOrg || selectedOrg.id === '0'"
          type="danger"
          @click="handleDelete"
        >
          删除
        </el-button>
      </div>
    </div>

    <div class="page-body">
      <el-tree
        :data="treeNodes"
        node-key="id"
        default-expand-all
        highlight-current
        :expand-on-click-node="false"
        :props="treeProps"
        @node-click="handleNodeClick"
      />
    </div>

    <el-dialog v-model="createDialogVisible" title="新增组织" width="480px" append-to-body>
      <el-form ref="createFormRef" :model="createForm" :rules="nameRules" label-position="top">
        <el-form-item label="组织名称" prop="name">
          <el-input v-model="createForm.name" maxlength="255" show-word-limit />
        </el-form-item>
        <el-form-item label="上级组织">
          <el-select v-model="createForm.pid" clearable placeholder="根组织" style="width: 100%">
            <el-option :value="0" label="根组织" />
            <el-option
              v-for="item in orgOptions"
              :key="item.id"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="createDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitCreate">确定</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="editDialogVisible" title="编辑组织" width="480px" append-to-body>
      <el-form ref="editFormRef" :model="editForm" :rules="nameRules" label-position="top">
        <el-form-item label="组织名称" prop="name">
          <el-input v-model="editForm.name" maxlength="255" show-word-limit />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitEdit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script lang="ts" setup>
import { computed, onMounted, reactive, ref } from 'vue'
import type { FormInstance, FormRules } from 'element-plus-secondary'
import { ElMessage, ElMessageBox } from 'element-plus-secondary'
import { deleteApi, resourceExistApi, saveApi, searchApi, updateApi } from '@/api/org'

interface OrgTreeNode {
  id: string
  pid: string | number
  name: string
  leaf: boolean
  children?: OrgTreeNode[]
}

const loading = ref(false)
const treeData = ref<OrgTreeNode[]>([])
const selectedOrg = ref<OrgTreeNode | null>(null)
const createDialogVisible = ref(false)
const editDialogVisible = ref(false)
const createFormRef = ref<FormInstance>()
const editFormRef = ref<FormInstance>()
const treeProps = { label: 'name', children: 'children' }

const createForm = reactive({
  name: '',
  pid: 0 as number
})

const editForm = reactive({
  id: '',
  name: ''
})

const nameRules: FormRules = {
  name: [{ required: true, message: '请输入组织名称', trigger: 'blur' }]
}

const treeNodes = computed(() => treeData.value[0]?.children || [])

const orgOptions = computed(() => {
  const options: Array<{ id: string; value: number; label: string }> = []
  const walk = (nodes: OrgTreeNode[], prefix = '') => {
    nodes.forEach(node => {
      if (node.id !== '0') {
        options.push({
          id: node.id,
          value: Number(node.id),
          label: `${prefix}${node.name}`
        })
      }
      if (node.children?.length) {
        walk(node.children, `${prefix}${node.name} / `)
      }
    })
  }
  walk(treeNodes.value)
  return options
})

const loadTree = async () => {
  loading.value = true
  try {
    const res = await searchApi({})
    treeData.value = res.data || []
    const currentId = selectedOrg.value?.id
    selectedOrg.value = currentId
      ? findNode(treeData.value, currentId) || null
      : treeData.value[0]?.children?.[0] || null
  } finally {
    loading.value = false
  }
}

const findNode = (nodes: OrgTreeNode[], id: string): OrgTreeNode | undefined => {
  for (const node of nodes) {
    if (node.id === id) {
      return node
    }
    if (node.children?.length) {
      const found = findNode(node.children, id)
      if (found) {
        return found
      }
    }
  }
}

const handleNodeClick = (data: OrgTreeNode) => {
  selectedOrg.value = data
}

const openCreateDialog = () => {
  createForm.name = ''
  createForm.pid =
    selectedOrg.value && selectedOrg.value.id !== '0' ? Number(selectedOrg.value.id) : 0
  createDialogVisible.value = true
}

const openEditDialog = () => {
  if (!selectedOrg.value || selectedOrg.value.id === '0') {
    return
  }
  editForm.id = selectedOrg.value.id
  editForm.name = selectedOrg.value.name
  editDialogVisible.value = true
}

const submitCreate = async () => {
  await createFormRef.value?.validate()
  await saveApi({
    name: createForm.name.trim(),
    pid: createForm.pid || 0
  })
  ElMessage.success('新增成功')
  createDialogVisible.value = false
  await loadTree()
}

const submitEdit = async () => {
  await editFormRef.value?.validate()
  await updateApi({
    id: Number(editForm.id),
    name: editForm.name.trim()
  })
  ElMessage.success('编辑成功')
  editDialogVisible.value = false
  await loadTree()
}

const handleDelete = async () => {
  if (!selectedOrg.value || selectedOrg.value.id === '0') {
    return
  }
  const oid = Number(selectedOrg.value.id)
  const hasChildren = await resourceExistApi(oid)
  if (hasChildren.data) {
    ElMessage.warning('当前组织存在下级组织，无法删除')
    return
  }
  await ElMessageBox.confirm(`确认删除组织“${selectedOrg.value.name}”吗？`, '删除组织', {
    type: 'warning',
    confirmButtonType: 'danger',
    autofocus: false,
    showClose: false
  })
  await deleteApi(oid)
  ElMessage.success('删除成功')
  selectedOrg.value = null
  await loadTree()
}

onMounted(() => {
  loadTree()
})
</script>

<style scoped lang="less">
.system-page {
  .page-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 16px;
  }

  .router-title {
    margin: 0;
    color: #1f2329;
    font-size: 20px;
    font-weight: 500;
    line-height: 28px;
  }

  .actions {
    display: flex;
    gap: 12px;
  }

  .page-body {
    min-height: calc(100vh - 176px);
    padding: 16px;
    background: var(--ContentBG, #ffffff);
    border-radius: 12px;
    overflow: auto;
  }
}
</style>
