<template>
  <div ref="containerRef" class="milkdown-editor">
    <div ref="editorRef" class="editor-container"></div>
  </div>
</template>

<script setup lang="ts">
// Prism 主题 CSS - 必须在组件导入前加载
import 'prismjs/themes/prism-tomorrow.css'
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { Editor, rootCtx, defaultValueCtx, editorViewCtx } from '@milkdown/core'
import { commonmark } from '@milkdown/preset-commonmark'
import { gfm } from '@milkdown/preset-gfm'
import { listener, listenerCtx } from '@milkdown/plugin-listener'
import { history } from '@milkdown/plugin-history'
import { prism, prismConfig } from '@milkdown/plugin-prism'
import { TextSelection } from '@milkdown/prose/state'
import { toggleMark, wrapIn } from '@milkdown/prose/commands'
import { useMilkdownTheme } from '@/composables/useMilkdownTheme'

// Refractor 语言注册 - 使用 refractor/all 导入所有语言
import { refractor } from 'refractor/all'

const props = defineProps<{
  modelValue: string
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: string): void
}>()

const containerRef = ref<HTMLElement | null>(null)
const editorRef = ref<HTMLElement | null>(null)
let editor: Editor | null = null

const { watchTheme } = useMilkdownTheme()

const execCommand = (commandName: string, payload?: any) => {
  if (!editor) return

  editor.action((ctx) => {
    const view = ctx.get(editorViewCtx)
    const { state, dispatch } = view

    switch (commandName) {
      case 'ToggleStrong':
        if (state.schema.marks.strong) {
          toggleMark(state.schema.marks.strong)(state, dispatch)
        }
        break
      case 'ToggleEmphasis':
        if (state.schema.marks.emphasis) {
          toggleMark(state.schema.marks.emphasis)(state, dispatch)
        }
        break
      case 'ToggleInlineCode':
        if (state.schema.marks.inlineCode) {
          toggleMark(state.schema.marks.inlineCode)(state, dispatch)
        }
        break
      case 'ToggleStrikeThrough':
      case 'ToggleStrikethrough':
        if (state.schema.marks.strike_through) {
          toggleMark(state.schema.marks.strike_through)(state, dispatch)
        }
        break
      case 'WrapInBulletList': {
        const { $from } = state.selection
        let listDepth = -1
        for (let i = $from.depth; i >= 0; i--) {
          const node = $from.node(i)
          if (node.type.name === 'bullet_list' || node.type.name === 'ordered_list') {
            listDepth = i
            break
          }
        }

        if (listDepth >= 0) {
          const node = $from.node(listDepth)
          if (node.type.name === 'bullet_list') {
            const startPos = $from.start(listDepth)
            const endPos = $from.end(listDepth)
            const textContent = node.textContent
            const paragraphNode = state.schema.nodes.paragraph
            if (paragraphNode) {
              const paragraph = paragraphNode.create(null, state.schema.text(textContent))
              const tr = state.tr.replaceWith(startPos - 1, endPos + 1, paragraph)
              dispatch(tr)
            }
          } else if (node.type.name === 'ordered_list') {
            const startPos = $from.start(listDepth)
            const endPos = $from.end(listDepth)
            const orderedList = $from.node(listDepth)

            const listItems: any[] = []
            orderedList.descendants((childNode) => {
              if (childNode.type.name === 'list_item') {
                const paragraphs: any[] = []
                childNode.content.forEach((child) => {
                  if (child.type.name === 'paragraph') {
                    paragraphs.push(child)
                  }
                })
                if (paragraphs.length > 0) {
                  const listItemNode = state.schema.nodes.list_item
                  if (listItemNode) {
                    const newItem = listItemNode.create(null, paragraphs)
                    listItems.push(newItem)
                  }
                }
              }
              return false
            })

            if (listItems.length > 0) {
              const bulletListNode = state.schema.nodes.bullet_list
              if (bulletListNode) {
                const bulletList = bulletListNode.create(null, listItems)
                const tr = state.tr.replaceWith(startPos - 1, endPos + 1, bulletList)
                dispatch(tr)
              }
            }
          }
        } else {
          const bulletListNode = state.schema.nodes.bullet_list
          if (bulletListNode) {
            wrapIn(bulletListNode)(state, dispatch)
          }
        }
        break
      }
      case 'WrapInOrderedList': {
        const { $from } = state.selection
        let listDepth = -1
        for (let i = $from.depth; i >= 0; i--) {
          const node = $from.node(i)
          if (node.type.name === 'bullet_list' || node.type.name === 'ordered_list') {
            listDepth = i
            break
          }
        }

        if (listDepth >= 0) {
          const node = $from.node(listDepth)
          if (node.type.name === 'ordered_list') {
            const startPos = $from.start(listDepth)
            const endPos = $from.end(listDepth)
            const textContent = node.textContent
            const paragraphNode = state.schema.nodes.paragraph
            if (paragraphNode) {
              const paragraph = paragraphNode.create(null, state.schema.text(textContent))
              const tr = state.tr.replaceWith(startPos - 1, endPos + 1, paragraph)
              dispatch(tr)
            }
          } else if (node.type.name === 'bullet_list') {
            const startPos = $from.start(listDepth)
            const endPos = $from.end(listDepth)
            const bulletList = $from.node(listDepth)

            const listItems: any[] = []
            bulletList.descendants((childNode) => {
              if (childNode.type.name === 'list_item') {
                const paragraphs: any[] = []
                childNode.content.forEach((child) => {
                  if (child.type.name === 'paragraph') {
                    paragraphs.push(child)
                  }
                })
                if (paragraphs.length > 0) {
                  const listItemNode = state.schema.nodes.list_item
                  if (listItemNode) {
                    const newItem = listItemNode.create(null, paragraphs)
                    listItems.push(newItem)
                  }
                }
              }
              return false
            })

            if (listItems.length > 0) {
              const orderedListNode = state.schema.nodes.ordered_list
              if (orderedListNode) {
                const orderedList = orderedListNode.create(null, listItems)
                const tr = state.tr.replaceWith(startPos - 1, endPos + 1, orderedList)
                dispatch(tr)
              }
            }
          }
        } else {
          const orderedListNode = state.schema.nodes.ordered_list
          if (orderedListNode) {
            wrapIn(orderedListNode)(state, dispatch)
          }
        }
        break
      }
      case 'WrapInHeading':
      case 'TurnIntoHeading': {
        const { $from } = state.selection
        const node = $from.node()
        if (node.type.name === 'heading') {
          const paragraphNode = state.schema.nodes.paragraph
          if (paragraphNode) {
            const tr = state.tr.setBlockType($from.start(), $from.end(), paragraphNode)
            dispatch(tr)
          }
        } else {
          const headingNode = state.schema.nodes.heading
          if (headingNode) {
            const tr = state.tr.setBlockType($from.start(), $from.end(), headingNode, { level: payload || 1 })
            dispatch(tr)
          }
        }
        break
      }
      case 'WrapInBlockquote': {
        const { $from } = state.selection
        let blockquoteDepth = -1
        for (let i = $from.depth; i >= 0; i--) {
          const node = $from.node(i)
          if (node.type.name === 'blockquote') {
            blockquoteDepth = i
            break
          }
        }

        if (blockquoteDepth >= 0) {
          const startPos = $from.start(blockquoteDepth)
          const endPos = $from.end(blockquoteDepth)
          const node = $from.node(blockquoteDepth)
          const textContent = node.textContent
          const paragraphNode = state.schema.nodes.paragraph
          if (paragraphNode) {
            const paragraph = paragraphNode.create(null, state.schema.text(textContent))
            const tr = state.tr.replaceWith(startPos - 1, endPos + 1, paragraph)
            dispatch(tr)
          }
        } else {
          const blockquoteNode = state.schema.nodes.blockquote
          if (blockquoteNode) {
            wrapIn(blockquoteNode)(state, dispatch)
          }
        }
        break
      }
      case 'WrapInCodeBlock':
      case 'TurnIntoCodeBlock': {
        const { $from, $to } = state.selection

        let codeBlockDepth = -1
        for (let i = $from.depth; i >= 0; i--) {
          const node = $from.node(i)
          if (node.type.name === 'code_block') {
            codeBlockDepth = i
            break
          }
        }

        if (codeBlockDepth >= 0) {
          const startPos = $from.start(codeBlockDepth)
          const endPos = $from.end(codeBlockDepth)
          const node = $from.node(codeBlockDepth)
          const textContent = node.textContent
          const paragraphNode = state.schema.nodes.paragraph
          if (paragraphNode) {
            const paragraph = paragraphNode.create(null, state.schema.text(textContent))
            const tr = state.tr.replaceWith(startPos - 1, endPos + 1, paragraph)
            dispatch(tr)
          }
        } else {
          const selectedText = state.doc.textBetween($from.pos, $to.pos, '\n')
          const textContent = selectedText || ' '
          const codeBlockNode = state.schema.nodes.code_block
          if (codeBlockNode) {
            const codeBlock = codeBlockNode.create(
              { language: payload || '' },
              state.schema.text(textContent)
            )
            const tr = state.tr.replaceWith($from.pos, $to.pos, codeBlock)
            dispatch(tr)
          }
        }
        break
      }
      case 'TurnIntoParagraph': {
        const { $from } = state.selection
        const paragraphNode = state.schema.nodes.paragraph
        if (paragraphNode) {
          const tr = state.tr.setBlockType($from.start(), $from.end(), paragraphNode)
          dispatch(tr)
        }
        break
      }
    }
  })
}

const getSelectedText = (): string => {
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

const insertText = (text: string) => {
  if (!editor) return

  editor.action((ctx) => {
    const view = ctx.get(editorViewCtx)
    const { state, dispatch } = view
    const tr = state.tr.insertText(text)
    dispatch(tr)
  })
}

const insertImage = (src: string, alt: string = '') => {
  if (!editor) return

  editor.action((ctx) => {
    const view = ctx.get(editorViewCtx)
    const { state, dispatch } = view
    const { schema } = state
    const imageNode = schema.nodes.image
    if (imageNode) {
      const node = imageNode.create({ src, alt })
      const tr = state.tr.replaceSelectionWith(node)
      dispatch(tr)
    }
  })
}

const insertLink = (href: string, text: string) => {
  if (!editor) return

  editor.action((ctx) => {
    const view = ctx.get(editorViewCtx)
    const { state, dispatch } = view
    const { schema } = state
    const linkMark = schema.marks.link
    if (linkMark) {
      const node = schema.text(text, [linkMark.create({ href })])
      const tr = state.tr.replaceSelectionWith(node)
      dispatch(tr)
    }
  })
}

const insertCodeBlock = (language: string = '', code: string = '') => {
  if (!editor) return

  editor.action((ctx) => {
    const view = ctx.get(editorViewCtx)
    const { state, dispatch } = view
    const { schema } = state

    const codeBlockNode = schema.nodes.code_block
    if (codeBlockNode) {
      const node = codeBlockNode.create(
        { language },
        schema.text(code || '\n')
      )
      const tr = state.tr.replaceSelectionWith(node)
      dispatch(tr)
      view.focus()
    }
  })

  nextTick(() => {
    if (!editorRef.value) return
    const preElements = editorRef.value.querySelectorAll('pre')
    const lastPre = preElements[preElements.length - 1]
    if (lastPre && language) {
      lastPre.dataset.language = language
    }
  })
}

const focus = () => {
  if (!editor) return

  editor.action((ctx) => {
    const view = ctx.get(editorViewCtx)
    view.focus()
  })
}

const getCurrentCodeBlockLanguage = (): string | null => {
  if (!editor) return null

  let language: string | null = null
  editor.action((ctx) => {
    const view = ctx.get(editorViewCtx)
    const { state } = view
    const { $from } = state.selection

    for (let i = $from.depth; i >= 0; i--) {
      const node = $from.node(i)
      if (node.type.name === 'code_block') {
        language = node.attrs.language || null
        break
      }
    }
  })

  return language
}

const setCodeBlockLanguage = (language: string) => {
  if (!editor) return

  editor.action((ctx) => {
    const view = ctx.get(editorViewCtx)
    const { state, dispatch } = view
    const { $from } = state.selection

    let codeBlockDepth = -1
    for (let i = $from.depth; i >= 0; i--) {
      const node = $from.node(i)
      if (node.type.name === 'code_block') {
        codeBlockDepth = i
        break
      }
    }

    if (codeBlockDepth >= 0) {
      const codeBlockPos = $from.start(codeBlockDepth) - 1
      const node = $from.node(codeBlockDepth)
      
      // 创建新节点并替换，强制重新渲染
      const newNode = node.type.create(
        { ...node.attrs, language },
        node.content
      )
      
      const tr = state.tr.replaceWith(codeBlockPos, codeBlockPos + node.nodeSize, newNode)
      dispatch(tr)
      
      console.log('[setCodeBlockLanguage] replaced node with language:', language, 'at pos:', codeBlockPos)
    }
  })
}

const setCodeBlockLanguageByDOM = (element: HTMLElement, language: string) => {
  if (!editor || !element) return

  // 直接更新 DOM 的 data-language 属性，立即生效
  element.setAttribute('data-language', language)

  // 使用 editor.action 获取 view，确保上下文正确
  editor.action((ctx) => {
    try {
      const view = ctx.get(editorViewCtx)
      const { state, dispatch } = view

      // 先尝试通过 DOM 元素获取位置
      let pos = view.posAtDOM(element, 0)
      console.log('[setCodeBlockLanguageByDOM] pos from DOM:', pos, 'element:', element.tagName)
      
      // 检查通过 DOM 获取的位置是否正确
      let nodeAtPos = pos >= 0 && pos < state.doc.content.size ? state.doc.nodeAt(pos) : null
      
      // 如果 posAtDOM 失败或位置不正确，尝试通过 selection 找到代码块
      if (!nodeAtPos || nodeAtPos.type.name !== 'code_block') {
        const { $from } = state.selection
        let codeBlockDepth = -1
        for (let i = $from.depth; i >= 0; i--) {
          const node = $from.node(i)
          if (node.type.name === 'code_block') {
            codeBlockDepth = i
            break
          }
        }
        
        if (codeBlockDepth >= 0) {
          pos = $from.start(codeBlockDepth) - 1
          nodeAtPos = state.doc.nodeAt(pos)
          console.log('[setCodeBlockLanguageByDOM] using selection pos:', pos, 'node:', nodeAtPos?.type?.name)
        }
      }
      
      if (pos >= 0 && pos < state.doc.content.size && nodeAtPos) {
        console.log('[setCodeBlockLanguageByDOM] final node:', nodeAtPos.type.name, 'attrs:', nodeAtPos.attrs)
        
        if (nodeAtPos.type.name === 'code_block') {
          // 使用 setNodeMarkup 更新节点属性，这会强制视图重新渲染
          const tr = state.tr.setNodeMarkup(pos, undefined, {
            ...nodeAtPos.attrs,
            language
          })
          dispatch(tr)
          console.log('[setCodeBlockLanguageByDOM] dispatched transaction, new language:', language)

          // 强制触发一次空事务，让 Prism 插件重新计算 decorations
          setTimeout(() => {
            const refreshTr = view.state.tr.insertText(' ', 0).delete(0, 1)
            view.dispatch(refreshTr)
          }, 0)
        } else {
          console.log('[setCodeBlockLanguageByDOM] node is not code_block:', nodeAtPos.type.name)
        }
      } else {
        console.log('[setCodeBlockLanguageByDOM] pos out of range or no node:', pos, 'doc size:', state.doc.content.size)
      }
    } catch (e) {
      console.error('[setCodeBlockLanguageByDOM] error:', e)
    }
  })
}

defineExpose({
  execCommand,
  getSelectedText,
  insertText,
  insertImage,
  insertLink,
  insertCodeBlock,
  focus,
  getCurrentCodeBlockLanguage,
  setCodeBlockLanguage,
  setCodeBlockLanguageByDOM
})

let lastEnterTime = 0
const setupDoubleEnterExit = () => {
  if (!editorRef.value) return

  editorRef.value.addEventListener('keydown', (event) => {
    if (event.key !== 'Enter') {
      lastEnterTime = 0
      return
    }

    const selection = window.getSelection()
    if (!selection) return

    const node = selection.anchorNode
    if (!node) return

    let parent = node.parentElement
    while (parent && parent !== editorRef.value) {
      if (parent.tagName === 'PRE') {
        const currentTime = Date.now()
        if (currentTime - lastEnterTime < 500) {
          event.preventDefault()
          event.stopPropagation()

          editor?.action((ctx) => {
            const view = ctx.get(editorViewCtx)
            const { state } = view
            const { $from } = state.selection

            let depth = $from.depth
            while (depth >= 0) {
              const node = $from.node(depth)
              if (node.type.name === 'code_block') {
                const codeBlockPos = $from.before(depth)

                const paragraphNode = state.schema.nodes.paragraph
                if (paragraphNode) {
                  const paragraph = paragraphNode.create()
                  const tr = state.tr.insert(codeBlockPos + node.nodeSize, paragraph)

                  const newPos = codeBlockPos + node.nodeSize + 1
                  const resolvedPos = tr.doc.resolve(newPos)
                  tr.setSelection(TextSelection.near(resolvedPos))

                  view.dispatch(tr)
                  view.focus()
                }
                break
              }
              depth--
            }
          })

          lastEnterTime = 0
          return
        }
        lastEnterTime = currentTime
        break
      }
      parent = parent.parentElement
    }
  }, true)
}

onMounted(async () => {
  if (!editorRef.value) return

  try {
    watchTheme(containerRef.value)

    editor = await Editor.make()
      .config((ctx) => {
        ctx.set(rootCtx, editorRef.value!)
        ctx.set(defaultValueCtx, props.modelValue || '')

        // 配置 prism 语言
        // 使用 lib/all.js 已经注册了所有语言，无需额外配置
        ctx.set(prismConfig.key, {
          configureRefractor: () => refractor
        })

        const listener = ctx.get(listenerCtx)
        listener.markdownUpdated((ctx, markdown, prevMarkdown) => {
          if (markdown !== prevMarkdown) {
            emit('update:modelValue', markdown)
          }
        })
      })
      .use(commonmark)
      .use(gfm)
      .use(listener)
      .use(history)
      .use(prism)
      .create()

    // 强制触发一次文档更新，确保 prism 高亮生效
    // 这是因为 @milkdown/plugin-prism 在 apply 中使用了错误的 refractor 实例
    // 通过触发一次空事务，强制重新计算 decorations
    setTimeout(() => {
      if (editor) {
        const view = editor.ctx.get(editorViewCtx)
        const tr = view.state.tr.insertText(' ', 0).delete(0, 1)
        view.dispatch(tr)
      }
    }, 100)

    setupDoubleEnterExit()
  } catch (e) {
    console.error('[MilkdownEditor] mounted error:', e)
  }
})

onUnmounted(() => {
  if (editor) {
    editor.destroy()
    editor = null
  }
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
  outline: none;
}

.editor-container :deep(.ProseMirror) {
  outline: none;
  min-height: 100%;
}

.editor-container :deep(.ProseMirror p) {
  margin: 0.5em 0;
}

.editor-container :deep(.ProseMirror h1) {
  margin: 0.67em 0;
  font-size: 2em;
  font-weight: bold;
}

.editor-container :deep(.ProseMirror h2) {
  margin: 0.75em 0;
  font-size: 1.5em;
  font-weight: bold;
}

.editor-container :deep(.ProseMirror h3) {
  margin: 0.83em 0;
  font-size: 1.17em;
  font-weight: bold;
}

.editor-container :deep(.ProseMirror ul) {
  list-style-type: disc;
  padding-left: 1.5em;
  margin: 0.5em 0;
}

.editor-container :deep(.ProseMirror ol) {
  list-style-type: decimal;
  padding-left: 1.5em;
  margin: 0.5em 0;
}

.editor-container :deep(.ProseMirror blockquote) {
  border-left: 3px solid var(--border-color, #ddd);
  padding-left: 1em;
  margin: 0.5em 0;
  color: var(--text-secondary, #666);
}

.editor-container :deep(.ProseMirror pre) {
  background: var(--code-bg, #f8f9fa);
  border: 1px solid var(--border-color, #e0e0e0);
  border-radius: 6px;
  padding: 1em;
  padding-top: 2.5em;
  overflow-x: auto;
  margin: 0.5em 0;
  position: relative;
}

.editor-container :deep(.ProseMirror pre code) {
  background: none;
  padding: 40px 16px 16px 16px;
  font-family: 'Fira Code', 'Consolas', 'Monaco', monospace;
  font-size: 0.9em;
  line-height: 1.6;
  color: var(--text-primary, #24292f);
  display: block;
}

.editor-container :deep(.ProseMirror code) {
  background: var(--inline-code-bg, rgba(175, 184, 193, 0.2));
  padding: 0.2em 0.4em;
  border-radius: 3px;
  font-family: 'Fira Code', 'Consolas', monospace;
  font-size: 0.9em;
}

.editor-container :deep(.ProseMirror a) {
  color: var(--link-color, #0969da);
  text-decoration: none;
}

.editor-container :deep(.ProseMirror a:hover) {
  text-decoration: underline;
}

.editor-container :deep(.ProseMirror img) {
  max-width: 100%;
  height: auto;
}

.editor-container :deep(.ProseMirror table) {
  border-collapse: collapse;
  width: 100%;
  margin: 0.5em 0;
}

.editor-container :deep(.ProseMirror th),
.editor-container :deep(.ProseMirror td) {
  border: 1px solid var(--border-color, #ddd);
  padding: 0.5em;
  text-align: left;
}

.editor-container :deep(.ProseMirror th) {
  background: var(--header-bg, #f5f5f5);
  font-weight: bold;
}

.editor-container :deep(.ProseMirror hr) {
  border: none;
  border-top: 2px solid var(--border-color, #ddd);
  margin: 1em 0;
}

.editor-container :deep(.ProseMirror-selectednode) {
  outline: 2px solid var(--selection-color, #8cf);
}

@media (prefers-color-scheme: dark) {
  .editor-container :deep(.ProseMirror pre) {
    background: var(--code-bg-dark, #1e1e1e);
    border-color: var(--border-color-dark, #30363d);
  }

  .editor-container :deep(.ProseMirror code) {
    background: var(--inline-code-bg-dark, rgba(110, 118, 129, 0.4));
    color: var(--text-primary-dark, #c9d1d9);
  }
}

/* 启用 Milkdown 自带的代码块语言标识 - 覆盖隐藏样式 */
.editor-container :deep(.milkdown pre::before) {
  opacity: 1 !important;
  inset: auto !important;
}
</style>
