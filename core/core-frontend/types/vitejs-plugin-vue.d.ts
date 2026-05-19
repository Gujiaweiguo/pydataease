declare module '@vitejs/plugin-vue' {
  import type { Plugin } from 'vite'

  export interface Options {
    include?: string | RegExp | (string | RegExp)[]
    exclude?: string | RegExp | (string | RegExp)[]
    reactivityTransform?: boolean
  }

  export default function vue(options?: Options): Plugin
}
