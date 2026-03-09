<template>
  <div ref="containerRef" class="milkdown-editor">
    <div ref="editorRef" class="editor-container"></div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { Editor, rootCtx, defaultValueCtx, editorViewCtx, serializerCtx, parserCtx } from '@milkdown/core'
import { commonmark, codeBlockSchema } from '@milkdown/preset-commonmark'
import { gfm } from '@milkdown/preset-gfm'
import { listener, listenerCtx } from '@milkdown/plugin-listener'
import { history } from '@milkdown/plugin-history'
import { $view } from '@milkdown/utils'
import { useMilkdownTheme } from '@/composables/useMilkdownTheme'

const props = defineProps<{
  modelValue: string
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: string): void
}>()

const containerRef = ref<HTMLElement | null>(null)
const editorRef = ref<HTMLElement | null>(null)
let editor: Editor | null = null

// 主题适配
const { watchTheme } = useMilkdownTheme()

// 执行Milkdown命令 - 使用ProseMirror的commands
const execCommand = (commandName: string, payload?: any) => {
  if (!editor) {
    console.warn('Editor not initialized yet')
    return
  }
  
  editor.action((ctx) => {
    const view = ctx.get(editorViewCtx)
    const { state, dispatch } = view
    
    // 根据命令名称执行对应的ProseMirror命令
    switch (commandName) {
      case 'ToggleStrong':
        toggleMark(state.schema.marks.strong)(state, dispatch)
        break
      case 'ToggleEmphasis':
        toggleMark(state.schema.marks.emphasis)(state, dispatch)
        break
      case 'ToggleStrikethrough':
        toggleMark(state.schema.marks.strike_through)(state, dispatch)
        break
      case 'WrapInHeading':
        wrapIn(state.schema.nodes.heading, { level: payload || 2 })(state, dispatch)
        break
      case 'WrapInBlockquote':
        wrapIn(state.schema.nodes.blockquote)(state, dispatch)
        break
      case 'WrapInBulletList':
        wrapInList(state.schema.nodes.bullet_list)(state, dispatch)
        break
      case 'WrapInOrderedList':
        wrapInList(state.schema.nodes.ordered_list)(state, dispatch)
        break
      case 'WrapInCodeBlock':
        wrapInCodeBlock(state, dispatch, payload)
        break
      case 'SetCodeBlockLanguage':
        setCodeBlockLanguage(payload)
        break
    }
  })
}

// 获取当前选中的文本
const getSelectedText = () => {
  if (!editor) return ''
  let selectedText = ''
  editor.action((ctx) => {
    const view = ctx.get(editorViewCtx)
    const { state } = view
    const { from, to } = state.selection
    selectedText = state.doc.textBetween(from, to)
  })
  return selectedText
}

// 在光标位置插入文本
const insertText = (text: string) => {
  if (!editor) return
  editor.action((ctx) => {
    const view = ctx.get(editorViewCtx)
    const { state, dispatch } = view
    const { from } = state.selection
    const tr = state.tr.insertText(text, from)
    dispatch(tr)
  })
}

// 插入图片节点
const insertImage = (url: string, alt: string = '') => {
  if (!editor) return
  editor.action((ctx) => {
    const view = ctx.get(editorViewCtx)
    const { state, dispatch } = view
    const { from } = state.selection

    // 获取图片节点类型
    const imageType = state.schema.nodes.image
    if (!imageType) {
      console.error('Image node type not found in schema')
      // 回退到插入Markdown文本
      const imageMarkdown = `\n![${alt || '图片'}](${url})\n`
      const tr = state.tr.insertText(imageMarkdown, from)
      dispatch(tr)
      return
    }

    // 创建图片节点
    const imageNode = imageType.create({
      src: url,
      alt: alt || '',
      title: alt || ''
    })

    // 插入图片节点
    const tr = state.tr.insert(from, imageNode)
    dispatch(tr.scrollIntoView())
  })
}

// 设置代码块语言
const setCodeBlockLanguage = (language: string) => {
  if (!editor) return
  
  editor.action((ctx) => {
    const view = ctx.get(editorViewCtx)
    const { state, dispatch } = view
    const { $from } = state.selection
    
    // 查找当前所在的代码块
    let codeBlockPos = $from.pos
    let codeBlockNode = null
    
    // 向上查找代码块节点
    state.doc.nodesBetween($from.start(), $from.end(), (node, pos) => {
      if (node.type.name === 'code_block') {
        codeBlockNode = node
        codeBlockPos = pos
        return false
      }
      return true
    })
    
    if (codeBlockNode && dispatch) {
      // 更新代码块的语言属性
      const tr = state.tr.setNodeMarkup(codeBlockPos, undefined, {
        ...codeBlockNode.attrs,
        language: language || undefined
      })
      dispatch(tr)
    }
  })
}

// 获取当前代码块的语言
const getCurrentCodeBlockLanguage = (): string | null => {
  if (!editor) return null
  
  let language: string | null = null
  editor.action((ctx) => {
    const view = ctx.get(editorViewCtx)
    const { state } = view
    const { $from } = state.selection
    
    // 向上查找代码块节点
    state.doc.nodesBetween($from.start(), $from.end(), (node) => {
      if (node.type.name === 'code_block') {
        language = node.attrs.language || null
        return false
      }
      return true
    })
  })
  
  return language
}

// 支持的编程语言列表
const supportedLanguages = [
  { value: '', label: '纯文本' },
  { value: 'javascript', label: 'JavaScript' },
  { value: 'typescript', label: 'TypeScript' },
  { value: 'python', label: 'Python' },
  { value: 'java', label: 'Java' },
  { value: 'go', label: 'Go' },
  { value: 'rust', label: 'Rust' },
  { value: 'cpp', label: 'C++' },
  { value: 'c', label: 'C' },
  { value: 'csharp', label: 'C#' },
  { value: 'php', label: 'PHP' },
  { value: 'ruby', label: 'Ruby' },
  { value: 'swift', label: 'Swift' },
  { value: 'kotlin', label: 'Kotlin' },
  { value: 'sql', label: 'SQL' },
  { value: 'html', label: 'HTML' },
  { value: 'css', label: 'CSS' },
  { value: 'scss', label: 'SCSS' },
  { value: 'json', label: 'JSON' },
  { value: 'yaml', label: 'YAML' },
  { value: 'xml', label: 'XML' },
  { value: 'markdown', label: 'Markdown' },
  { value: 'bash', label: 'Bash' },
  { value: 'powershell', label: 'PowerShell' },
  { value: 'dockerfile', label: 'Dockerfile' },
  { value: 'vim', label: 'Vim' },
  { value: 'lua', label: 'Lua' },
  { value: 'perl', label: 'Perl' },
  { value: 'r', label: 'R' },
  { value: 'matlab', label: 'MATLAB' },
  { value: 'scala', label: 'Scala' },
  { value: 'groovy', label: 'Groovy' },
  { value: 'dart', label: 'Dart' },
  { value: 'elixir', label: 'Elixir' },
  { value: 'erlang', label: 'Erlang' },
  { value: 'haskell', label: 'Haskell' },
  { value: 'clojure', label: 'Clojure' },
  { value: 'fsharp', label: 'F#' },
  { value: 'ocaml', label: 'OCaml' },
  { value: 'reason', label: 'Reason' },
  { value: 'purescript', label: 'PureScript' },
  { value: 'elm', label: 'Elm' },
  { value: 'coffeescript', label: 'CoffeeScript' },
  { value: 'livescript', label: 'LiveScript' },
  { value: 'julia', label: 'Julia' },
  { value: 'crystal', label: 'Crystal' },
  { value: 'nim', label: 'Nim' },
  { value: 'zig', label: 'Zig' },
  { value: 'v', label: 'V' },
  { value: 'odin', label: 'Odin' },
  { value: 'hare', label: 'Hare' },
  { value: 'gleam', label: 'Gleam' }
]

// 暴露编辑器实例和方法给父组件
defineExpose({
  editor: () => editor,
  execCommand,
  getEditor: () => editor,
  getSelectedText,
  insertText,
  insertImage,
  setCodeBlockLanguage,
  getCurrentCodeBlockLanguage,
  supportedLanguages
})

// ProseMirror commands (简化版)
const toggleMark = (markType: any) => {
  return (state: any, dispatch: any) => {
    const { from, to } = state.selection
    const hasMark = state.doc.rangeHasMark(from, to, markType)
    
    if (dispatch) {
      const tr = state.tr
      if (hasMark) {
        tr.removeMark(from, to, markType)
      } else {
        tr.addMark(from, to, markType.create())
      }
      dispatch(tr)
    }
    return true
  }
}

const wrapIn = (nodeType: any, attrs?: any) => {
  return (state: any, dispatch: any) => {
    const { from, to } = state.selection
    const tr = state.tr.wrap(state.selection.$from.blockRange(), [{ type: nodeType, attrs }])
    if (tr && dispatch) {
      dispatch(tr)
      return true
    }
    return false
  }
}

// 包装为列表 - 支持光标所在行创建/移除列表，支持列表类型互换，支持多行选中
const wrapInList = (listType: any) => {
  return (state: any, dispatch: any) => {
    const { $from, $to } = state.selection
    const paragraphType = state.schema.nodes.paragraph
    const listItemType = state.schema.nodes.list_item
    const bulletListType = state.schema.nodes.bullet_list
    const orderedListType = state.schema.nodes.ordered_list

    if (!listItemType || !paragraphType) {
      console.error('Required node types not found in schema')
      return false
    }

    // 检查是否有选区（多行选中）
    const hasSelection = $from.pos !== $to.pos

    // 如果有选区，处理多行
    if (hasSelection) {
      return wrapMultipleLinesInList(state, dispatch, listType, $from, $to, paragraphType, listItemType, bulletListType, orderedListType)
    }

    // 单行处理（光标模式）
    return wrapSingleLineInList(state, dispatch, listType, $from, paragraphType, listItemType, bulletListType, orderedListType)
  }
}

// 单行列表处理
const wrapSingleLineInList = (state: any, dispatch: any, listType: any, $from: any, paragraphType: any, listItemType: any, bulletListType: any, orderedListType: any) => {
  const currentNode = $from.parent
  const currentDepth = $from.depth
  const currentPos = $from.before(currentDepth)

  // 检查当前是否在列表中
  const parentList = currentDepth > 1 ? $from.node(currentDepth - 1) : null
  const grandParentList = currentDepth > 2 ? $from.node(currentDepth - 2) : null

  // 如果在同类型列表中，解除列表
  if (parentList && parentList.type === listType) {
    return removeListItem(state, dispatch, currentPos, currentDepth, currentNode)
  }

  // 如果在另一种列表中，转换为当前类型
  if (parentList && (parentList.type === bulletListType || parentList.type === orderedListType)) {
    return convertListType(state, dispatch, parentList, listType, currentDepth - 1)
  }

  // 如果grandParent是列表（处理嵌套情况）
  if (grandParentList && (grandParentList.type === bulletListType || grandParentList.type === orderedListType)) {
    if (grandParentList.type === listType) {
      return removeListItem(state, dispatch, $from.before(currentDepth - 1), currentDepth - 1, parentList)
    } else {
      return convertListType(state, dispatch, grandParentList, listType, currentDepth - 2)
    }
  }

  if (!dispatch) return true

  // 不在列表中，创建新的列表项
  const lineText = currentNode.textContent || ''
  const paragraph = paragraphType.create(null, lineText ? state.schema.text(lineText) : null)
  const listItem = listItemType.create(null, paragraph)
  const listNode = listType.create(null, listItem)

  const tr = state.tr.replaceWith(currentPos, $from.after(currentDepth), listNode)
  dispatch(tr.scrollIntoView())
  return true
}

// 多行列表处理
const wrapMultipleLinesInList = (state: any, dispatch: any, listType: any, $from: any, $to: any, paragraphType: any, listItemType: any, bulletListType: any, orderedListType: any) => {
  // 获取选区范围内的所有段落
  const range = $from.blockRange($to)
  if (!range) return false

  // 检查选区是否已经在同类型列表中
  const parent = $from.node(-1)
  if (parent && parent.type === listType) {
    // 解除整个列表
    return liftListItems(state, dispatch, $from, $to, listItemType, paragraphType)
  }

  // 检查选区是否在另一种列表中
  if (parent && (parent.type === bulletListType || parent.type === orderedListType)) {
    // 转换整个列表类型
    return convertListTypeForRange(state, dispatch, parent, listType, $from, $to)
  }

  if (!dispatch) return true

  // 将选中的段落转换为列表项
  const listItems: any[] = []
  const startPos = range.start
  const endPos = range.end

  // 遍历选区内的所有段落
  state.doc.nodesBetween(startPos, endPos, (node: any, pos: number) => {
    if (node.type === paragraphType) {
      const item = listItemType.create(null, node.copy(node.content))
      listItems.push(item)
    }
  })

  if (listItems.length === 0) return false

  // 创建列表节点
  const listNode = listType.create(null, listItems)

  // 替换选区内容为列表
  const tr = state.tr.replaceWith(startPos, endPos, listNode)
  dispatch(tr.scrollIntoView())
  return true
}

// 移除列表项，转换为普通段落
const removeListItem = (state: any, dispatch: any, pos: number, depth: number, node: any) => {
  if (!dispatch) return true

  const paragraphType = state.schema.nodes.paragraph
  if (!paragraphType) return false

  // 获取list_item的内容（通常是paragraph）
  let paragraphContent = null
  node.forEach((child: any) => {
    if (child.type.name === 'paragraph') {
      paragraphContent = child.content
    }
  })

  // 创建新的paragraph
  const newParagraph = paragraphType.create(null, paragraphContent)

  // 替换list_item为paragraph
  const tr = state.tr.replaceWith(pos, pos + node.nodeSize, newParagraph)
  dispatch(tr.scrollIntoView())
  return true
}

// 转换列表类型（无序<->有序）- 用于单行
const convertListType = (state: any, dispatch: any, oldList: any, newListType: any, listDepth: number) => {
  if (!dispatch) return true

  const { $from } = state.selection
  const listItemType = state.schema.nodes.list_item
  if (!listItemType) return false

  // 找到列表的起始位置 - 使用更可靠的方法
  let listStart = $from.start(listDepth) - 1
  let listEnd = $from.end(listDepth)

  // 获取旧列表的所有list_item
  const listItems: any[] = []
  oldList.forEach((child: any) => {
    if (child.type === listItemType) {
      listItems.push(child)
    }
  })

  if (listItems.length === 0) return false

  // 创建新类型的列表节点
  const newList = newListType.create(null, listItems)

  // 替换旧列表
  const tr = state.tr.replaceWith(listStart, listEnd, newList)
  dispatch(tr.scrollIntoView())
  return true
}

// 转换列表类型 - 用于多行选区
const convertListTypeForRange = (state: any, dispatch: any, oldList: any, newListType: any, $from: any, $to: any) => {
  if (!dispatch) return true

  const listItemType = state.schema.nodes.list_item
  if (!listItemType) return false

  // 获取选区范围
  const range = $from.blockRange($to)
  if (!range) return false

  // 获取旧列表的所有list_item
  const listItems: any[] = []
  oldList.forEach((child: any) => {
    if (child.type === listItemType) {
      listItems.push(child)
    }
  })

  if (listItems.length === 0) return false

  // 创建新类型的列表节点
  const newList = newListType.create(null, listItems)

  // 替换旧列表 - 使用range的范围
  const tr = state.tr.replaceWith(range.start, range.end, newList)
  dispatch(tr.scrollIntoView())
  return true
}

// 解除多行列表项
const liftListItems = (state: any, dispatch: any, $from: any, $to: any, listItemType: any, paragraphType: any) => {
  if (!dispatch) return true

  const range = $from.blockRange($to)
  if (!range) return false

  // 获取列表节点
  const listNode = $from.node(-1)
  const paragraphs: any[] = []

  // 遍历列表中的所有list_item，提取内容
  listNode.forEach((child: any) => {
    if (child.type === listItemType) {
      child.forEach((content: any) => {
        if (content.type === paragraphType) {
          paragraphs.push(paragraphType.create(null, content.content))
        } else {
          paragraphs.push(content.copy(content.content))
        }
      })
    }
  })

  if (paragraphs.length === 0) return false

  // 替换整个列表为段落
  const tr = state.tr.replaceWith(range.start, range.end, paragraphs)
  dispatch(tr.scrollIntoView())
  return true
}

// 从列表中提升（解除列表）- 用于选区操作
const liftListItem = (itemType: any) => {
  return (state: any, dispatch: any) => {
    const { $from, $to } = state.selection
    const range = $from.blockRange($to, (node: any) => node.childCount && node.firstChild?.type === itemType)
    if (!range) return false
    if (!dispatch) return true

    // 获取列表项内容并替换
    const listNode = $from.node(-1)
    const listItemNodes: any[] = []

    listNode.forEach((child: any) => {
      if (child.type === itemType) {
        child.forEach((content: any) => {
          listItemNodes.push(content)
        })
      }
    })

    const paragraphType = state.schema.nodes.paragraph
    if (listItemNodes.length > 0 && paragraphType) {
      const newNodes = listItemNodes.map(content => paragraphType.create(null, content.content))
      const start = $from.start(range.depth - 1)
      const end = $to.end(range.depth - 1)
      const tr = state.tr.replaceWith(start, end, newNodes)
      dispatch(tr.scrollIntoView())
      return true
    }

    return false
  }
}

// 查找包裹方式 - 使用ProseMirror的findWrapping逻辑
const findWrapping = (range: any, nodeType: any, attrs: any = null, innerType: any = null) => {
  const parent = range.parent
  const around = parent.contentMatchAt(range.startIndex).findWrapping(nodeType, attrs)
  if (!around) return null

  // 如果提供了innerType（如list_item），需要将其添加到wrapping中
  if (innerType) {
    // around是一个NodeType数组，我们需要构造包含innerType的wrapping
    // 格式应该是 [{type: nodeType, attrs}, {type: innerType}]
    return [
      { type: nodeType, attrs },
      { type: innerType }
    ]
  }

  return around
}

// 代码块包装函数
const wrapInCodeBlock = (state: any, dispatch: any, language?: string) => {
  const { $from, $to } = state.selection
  const range = $from.blockRange($to)
  if (!range) return false
  
  // 获取选中的文本内容
  const selectedText = state.doc.textBetween($from.pos, $to.pos)
  
  // 创建代码块节点
  const codeBlockType = state.schema.nodes.code_block
  if (!codeBlockType) return false
  
  // 创建代码块节点，带语言属性
  const attrs = language ? { language } : {}
  const codeBlock = codeBlockType.create(attrs, state.schema.text(selectedText || ' '))
  
  if (dispatch) {
    // 替换选中内容为代码块
    const tr = state.tr.replaceRangeWith(range.start, range.end, codeBlock)
    dispatch(tr)
    return true
  }
  return false
}

// 自定义代码块视图 - 添加 data-language 属性，处理键盘事件
const codeBlockView = $view(codeBlockSchema.node, () => {
  return (node, view, getPos) => {
    const dom = document.createElement('pre')
    const language = node.attrs.language as string | undefined

    if (language) {
      dom.setAttribute('data-language', language)
    }

    const code = document.createElement('code')
    dom.appendChild(code)

    return {
      dom,
      contentDOM: code,
      update: (updatedNode) => {
        if (updatedNode.type.name !== 'code_block') return false

        const newLanguage = updatedNode.attrs.language as string | undefined
        if (newLanguage) {
          dom.setAttribute('data-language', newLanguage)
        } else {
          dom.removeAttribute('data-language')
        }

        return true
      }
    }
  }
})

onMounted(async () => {
  if (!editorRef.value) return

  // 应用主题
  watchTheme(containerRef.value)

  editor = await Editor.make()
    .config((ctx) => {
      ctx.set(rootCtx, editorRef.value!)
      ctx.set(defaultValueCtx, props.modelValue || '')

      const listener = ctx.get(listenerCtx)
      listener.markdownUpdated((ctx, markdown, prevMarkdown) => {
        if (markdown !== prevMarkdown) {
          emit('update:modelValue', markdown)
        }
      })
    })
    // 不使用nord主题，使用自定义CSS
    .use(commonmark)
    .use(gfm)
    .use(listener)
    .use(history)
    .use(codeBlockView)
    .create()
})

onUnmounted(() => {
  editor?.destroy()
})

// 监听外部值变化
watch(() => props.modelValue, (newValue) => {
  // 这里可以处理外部值同步到编辑器
  // Milkdown有内部状态管理，需要谨慎处理
})
</script>

<style scoped>
.milkdown-editor {
  width: 100%;
  height: 100%;
}

.editor-container {
  width: 100%;
  height: 100%;
  min-height: 400px;
}

/* Milkdown 编辑器基础样式 */
:deep(.milkdown) {
  height: 100%;
  padding: 16px;
  background: var(--bg-primary);
  color: var(--text-primary);
}

:deep(.editor) {
  min-height: 100%;
}
</style>
