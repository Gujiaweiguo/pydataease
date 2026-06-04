import mitt from 'mitt'
import { getCurrentInstance, onBeforeUnmount } from 'vue'

interface Option {
  name: string // 事件名称
  callback: Fn // 回调
}

const emitter = mitt()

export const useEmitt = (option?: Option) => {
  if (option) {
    emitter.on(option.name, option.callback)

    if (getCurrentInstance()) {
      onBeforeUnmount(() => {
        emitter.off(option.name, option.callback)
      })
    }
  }

  return {
    emitter
  }
}
