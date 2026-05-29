<template>
  <div class="org-management-page" v-loading="loading">
    <div class="page-header">
      <p class="router-title">组织管理</p>
      <div class="toolbar">
        <el-input
          v-model="searchKeyword"
          clearable
          placeholder="搜索组织名称"
          style="width: 240px"
          @keyup.enter="handleSearch"
          @clear="handleSearch"
        />
        <el-button @click="handleSearch">查询</el-button>
        <el-button type="primary" @click="openCreateDialog()">新增组织</el-button>
      </div>
    </div>

    <div class="page-body page-layout">
      <aside class="tree-sidebar">
        <div class="sidebar-caption">组织架构</div>
        <el-tree
          ref="treeRef"
          :data="treeData"
          node-key="id"
          default-expand-all
          highlight-current
          :expand-on-click-node="false"
          :filter-node-method="filterNode"
          :props="treeProps"
          class="org-tree"
          @node-click="handleNodeClick"
        >
          <template #default="{ data }">
            <div class="tree-node" :class="{ 'is-root': data.id === ROOT_ORG_ID }">
              <span class="tree-node-label">{{ data.name }}</span>
            </div>
          </template>
        </el-tree>
      </aside>

      <section class="table-panel">
        <div class="table-panel-header">
          <div class="panel-copy">
            <h3>{{ selectedOrg?.name || '根组织' }}</h3>
            <p>{{ tableDescription }}</p>
          </div>
          <div class="selected-summary">
            直属下级 {{ filteredChildCount }} / {{ totalChildCount }}
          </div>
        </div>

        <div class="table-wrap">
          <el-table :data="tableRows" border row-key="id" height="100%">
            <el-table-column label="组织名称" min-width="220" show-overflow-tooltip>
              <template #default="scope">
                <span>{{ scope.row.name }}</span>
              </template>
            </el-table-column>
            <el-table-column label="上级组织" min-width="160" show-overflow-tooltip>
              <template #default="scope">
                <span>{{ scope.row.parentName }}</span>
              </template>
            </el-table-column>
            <el-table-column label="创建时间" width="140">
              <template #default="scope">
                <span>{{ scope.row.createTimeDisplay }}</span>
              </template>
            </el-table-column>
            <el-table-column label="操作" fixed="right" width="260">
              <template #default="scope">
                <el-button link type="primary" @click="openCreateDialog(scope.row)"
                  >新建子组织</el-button
                >
                <el-button link type="primary" @click="openEditDialog(scope.row)">编辑</el-button>
                <el-button link type="danger" @click="handleDelete(scope.row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </section>
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
        <el-button @click="closeCreateDialog">取消</el-button>
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
        <el-button @click="closeEditDialog">取消</el-button>
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

interface OrgOptionItem {
  id: string
  value: string
  label: string
}

interface OrgTableRow extends OrgTreeNode {
  parentName: string
  createTimeDisplay: string
}

interface TreeViewInstance {
  filter: (value: string) => void
  setCurrentKey: (key: string | number) => void
}

const ROOT_ORG_ID = '0'
const ROOT_ORG_NAME = '根组织'

const loading = ref(false)
const treeData = ref<OrgTreeNode[]>([])
const selectedOrgId = ref(ROOT_ORG_ID)
const searchKeyword = ref('')
const activeKeyword = ref('')
const createDialogVisible = ref(false)
const editDialogVisible = ref(false)
const createFormRef = ref<FormInstance>()
const editFormRef = ref<FormInstance>()
const treeRef = ref<TreeViewInstance>()
const nodeMap = ref<Record<string, OrgTreeNode>>({})
const parentNameMap = ref<Record<string, string>>({})
const treeProps = { label: 'name', children: 'children' }

const createForm = reactive({
  name: '',
  pid: '0'
})

const editForm = reactive({
  id: '',
  name: ''
})

const nameRules: FormRules = {
  name: [{ required: true, message: '请输入组织名称', trigger: 'blur' }]
}

const selectedOrg = computed(() => nodeMap.value[selectedOrgId.value])

const totalChildCount = computed(() => selectedOrg.value?.children?.length || 0)

const filteredChildCount = computed(() => tableRows.value.length)

const tableDescription = computed(() => {
  if (selectedOrgId.value === ROOT_ORG_ID) {
    return '展示全部一级组织，点击左侧组织可查看其直属下级。'
  }
  return `展示“${selectedOrg.value?.name || ''}”的直属下级组织。`
})

const tableRows = computed<OrgTableRow[]>(() => {
  const keyword = activeKeyword.value
  const children = selectedOrg.value?.children || []
  return children
    .filter(item => !keyword || item.name.includes(keyword))
    .map(item => ({
      ...item,
      parentName: parentNameMap.value[item.id] || ROOT_ORG_NAME,
      createTimeDisplay: '-'
    }))
})

const orgOptions = computed<OrgOptionItem[]>(() => {
  const options: OrgOptionItem[] = []
  const walk = (nodes: OrgTreeNode[], prefix = '') => {
    nodes.forEach(node => {
      if (node.id !== ROOT_ORG_ID) {
        options.push({
          id: node.id,
          value: String(node.id),
          label: `${prefix}${node.name}`
        })
      }
      if (node.children?.length) {
        walk(node.children, `${prefix}${node.name} / `)
      }
    })
  }
  walk(treeData.value)
  return options
})

const cloneOrgNode = (node: OrgTreeNode): OrgTreeNode => ({
  id: String(node.id),
  pid: node.pid,
  name: node.name,
  leaf: Boolean(node.leaf),
  children: (node.children || []).map(child => cloneOrgNode(child))
})

const normalizeTree = (nodes: OrgTreeNode[]): OrgTreeNode[] => {
  const sourceNodes = (nodes || []).map(item => cloneOrgNode(item))
  const rootNode = sourceNodes.find(item => item.id === ROOT_ORG_ID)
  const rootChildren = rootNode?.children?.length
    ? rootNode.children
    : sourceNodes.filter(item => item.id !== ROOT_ORG_ID)

  return [
    {
      id: ROOT_ORG_ID,
      pid: ROOT_ORG_ID,
      name: ROOT_ORG_NAME,
      leaf: rootChildren.length === 0,
      children: rootChildren
    }
  ]
}

const rebuildTreeMeta = (nodes: OrgTreeNode[]) => {
  const nextNodeMap: Record<string, OrgTreeNode> = {}
  const nextParentNameMap: Record<string, string> = {}

  const walk = (items: OrgTreeNode[], parentName = '') => {
    items.forEach(node => {
      nextNodeMap[node.id] = node
      nextParentNameMap[node.id] = parentName || ROOT_ORG_NAME
      if (node.children?.length) {
        walk(node.children, node.name)
      }
    })
  }

  walk(nodes)
  nodeMap.value = nextNodeMap
  parentNameMap.value = nextParentNameMap
}

const syncCurrentTreeNode = async () => {
  await nextTick()
  treeRef.value?.setCurrentKey(selectedOrgId.value)
}

const filterNode = (value: string, data: OrgTreeNode) => {
  if (!value) {
    return true
  }
  if (data.id === ROOT_ORG_ID) {
    return true
  }
  return data.name.includes(value)
}

const handleSearch = () => {
  activeKeyword.value = searchKeyword.value.trim()
  treeRef.value?.filter(activeKeyword.value)
}

const handleNodeClick = (data: OrgTreeNode) => {
  selectedOrgId.value = data.id
}

const loadTree = async () => {
  loading.value = true
  try {
    const res = await searchApi({})
    const normalizedTree = normalizeTree(res.data || [])
    treeData.value = normalizedTree
    rebuildTreeMeta(normalizedTree)
    if (!nodeMap.value[selectedOrgId.value]) {
      selectedOrgId.value = ROOT_ORG_ID
    }
    await syncCurrentTreeNode()
    handleSearch()
  } finally {
    loading.value = false
  }
}

const resetCreateForm = () => {
  createForm.name = ''
  createForm.pid = '0'
}

const closeCreateDialog = () => {
  createFormRef.value?.clearValidate()
  createDialogVisible.value = false
  resetCreateForm()
}

const closeEditDialog = () => {
  editFormRef.value?.clearValidate()
  editDialogVisible.value = false
  editForm.id = ''
  editForm.name = ''
}

const openCreateDialog = (parent?: OrgTreeNode) => {
  resetCreateForm()
  createForm.pid = parent && parent.id !== ROOT_ORG_ID ? String(parent.id) : '0'
  createDialogVisible.value = true
}

const openEditDialog = (data: OrgTreeNode) => {
  if (data.id === ROOT_ORG_ID) {
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
    pid: createForm.pid || '0'
  })
  ElMessage.success('新增成功')
  selectedOrgId.value = createForm.pid ? createForm.pid : ROOT_ORG_ID
  closeCreateDialog()
  await loadTree()
}

const submitEdit = async () => {
  await editFormRef.value?.validate()
  await updateApi({
    id: editForm.id,
    name: editForm.name.trim()
  })
  ElMessage.success('编辑成功')
  closeEditDialog()
  await loadTree()
}

const handleDelete = async (data: OrgTreeNode) => {
  if (data.id === ROOT_ORG_ID) {
    return
  }

  const oid = data.id
  const hasChildren = await resourceExistApi(oid)
  if (hasChildren.data) {
    ElMessage.warning('当前组织存在下级组织，无法删除')
    return
  }

  await ElMessageBox.confirm(
    `确认删除组织“${data.name}”吗？删除后该组织下所有资源将一并删除。`,
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
  if (selectedOrgId.value === data.id) {
    selectedOrgId.value = String(data.pid || ROOT_ORG_ID)
  }
  await loadTree()
}

onMounted(async () => {
  await loadTree()
})
</script>

<style scoped lang="less">
.org-management-page {
  .page-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 16px;
    gap: 16px;
  }

  .router-title {
    margin: 0;
    color: #1f2329;
    font-family: var(--de-custom_font, 'PingFang');
    font-size: 20px;
    font-weight: 500;
    line-height: 28px;
  }

  .toolbar {
    display: flex;
    align-items: center;
    justify-content: flex-end;
    gap: 12px;
    flex-wrap: wrap;
  }

  .page-body {
    background: var(--ContentBG, #ffffff);
    border-radius: 12px;
  }

  .page-layout {
    display: grid;
    grid-template-columns: 280px minmax(0, 1fr);
    min-height: calc(100vh - 176px);
    padding: 0;
    overflow: hidden;
  }

  .tree-sidebar {
    padding: 16px 12px 16px 16px;
    background: var(--ContentBG, #ffffff);
    border-right: 1px solid #ebedf0;
    overflow-y: auto;
  }

  .sidebar-caption {
    margin-bottom: 12px;
    color: #646a73;
    font-size: 13px;
    line-height: 20px;
  }

  .org-tree {
    min-width: 0;
  }

  .tree-node {
    display: flex;
    align-items: center;
    min-width: 0;
    gap: 8px;

    &.is-root {
      font-weight: 500;
    }
  }

  .tree-node-label {
    overflow: hidden;
    color: inherit;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .table-panel {
    display: flex;
    flex-direction: column;
    min-width: 0;
    padding: 16px;
    overflow: hidden;
  }

  .table-panel-header {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    gap: 16px;
    margin-bottom: 16px;
  }

  .panel-copy {
    h3 {
      margin: 0;
      color: #1f2329;
      font-size: 18px;
      font-weight: 500;
      line-height: 26px;
    }

    p {
      margin: 6px 0 0;
      color: #646a73;
      font-size: 13px;
      line-height: 20px;
    }
  }

  .selected-summary {
    display: inline-flex;
    align-items: center;
    min-height: 32px;
    padding: 0 12px;
    color: #3f4854;
    font-size: 13px;
    background: #f5f7fa;
    border-radius: 999px;
    white-space: nowrap;
  }

  .table-wrap {
    flex: 1;
    min-height: 0;
  }

  :deep(.org-tree .el-tree-node__content) {
    height: 40px;
    margin-bottom: 4px;
    border-radius: 8px;
  }

  :deep(.org-tree .el-tree-node.is-current > .el-tree-node__content) {
    color: #3370ff;
    background: rgba(51, 112, 255, 0.08);
  }

  :deep(.org-tree .el-tree-node__label) {
    width: 100%;
    font-size: 14px;
  }
}
</style>
