<template>
  <div class="system-page" v-loading="loading">
    <div class="page-header">
      <p class="router-title">组织管理</p>
      <div class="actions">
        <el-input
          v-model="searchKeyword"
          clearable
          placeholder="搜索组织名称"
          style="width: 220px"
          @keyup.enter="handleSearch"
          @clear="handleSearch"
        />
        <el-button @click="handleSearch">查询</el-button>
        <el-button type="primary" @click="openCreateDialog(undefined)">新增组织</el-button>
      </div>
    </div>

    <div class="page-body">
      <el-tree
        ref="treeRef"
        :data="treeNodes"
        :filter-node-method="filterNode"
        node-key="id"
        default-expand-all
        highlight-current
        :expand-on-click-node="false"
        :props="treeProps"
        @node-click="handleNodeClick"
      >
        <template #default="{ data }">
          <div class="tree-node" :class="{ 'is-root': data.id === '0' }">
            <span class="tree-node-label">{{ data.name }}</span>
            <span v-if="data.id !== '0'" class="tree-node-actions">
              <el-button link type="primary" size="small" @click.stop="openCreateDialog(data)"
                >新建子组织</el-button
              >
              <el-button link type="primary" size="small" @click.stop="openEditDialog(data)"
                >编辑</el-button
              >
              <el-button link type="danger" size="small" @click.stop="handleDelete(data)"
                >删除</el-button
              >
            </span>
          </div>
        </template>
      </el-tree>
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
import { computed, nextTick, onMounted, reactive, ref } from 'vue'
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
const treeRef = ref<any>()
const searchKeyword = ref('')
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

const filterNode = (value: string, data: OrgTreeNode) => {
  if (!value) return true
  return data.name.includes(value)
}

const handleSearch = () => {
  treeRef.value?.filter(searchKeyword.value.trim())
}

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

const openCreateDialog = (parent?: OrgTreeNode | undefined) => {
  createForm.name = ''
  createForm.pid = parent && parent.id !== '0' ? Number(parent.id) : 0
  createDialogVisible.value = true
}

const openEditDialog = (data: OrgTreeNode) => {
  if (data.id === '0') {
    return
  }
  editForm.id = data.id
  editForm.name = data.name
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
  await nextTick()
  handleSearch()
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

const handleDelete = async (data: OrgTreeNode) => {
  if (data.id === '0') {
    return
  }
  const oid = Number(data.id)
  const hasChildren = await resourceExistApi(oid)
  if (hasChildren.data) {
    ElMessage.warning('当前组织存在下级组织，无法删除')
    return
  }
  await ElMessageBox.confirm(
    `确认删除组织"${data.name}"吗？删除后该组织下所有资源将一并删除。`,
    '删除组织',
    {
      type: 'warning',
      confirmButtonType: 'danger',
      autofocus: false,
      showClose: false
    }
  )
  await deleteApi(oid)
  ElMessage.success('删除成功')
  if (selectedOrg.value?.id === data.id) {
    selectedOrg.value = null
  }
  await loadTree()
  await nextTick()
  handleSearch()
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

  .tree-node {
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex: 1;
    padding-right: 8px;

    &.is-root .tree-node-label {
      font-weight: 500;
    }

    .tree-node-label {
      font-size: 14px;
      color: #1f2329;
    }

    .tree-node-actions {
      display: none;
      gap: 4px;
      margin-left: 8px;
    }

    &:hover .tree-node-actions {
      display: flex;
    }
  }
}
</style>
