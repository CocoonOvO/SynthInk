<template>
  <!-- Brutalist Newspaper 报纸档案：整张报纸即是一个可交互档案柜 -->
  <div class="newspaper-root">
    <!-- 油墨噪点纹理层：全屏覆盖，pointer-events none -->
    <div class="ink-texture" aria-hidden="true"></div>

    <!-- 报纸纸张容器：限定最大宽度，居中，2px 黑边 + 柔和纸阴影 -->
    <div class="paper">
      <!-- ================= 报头 Masthead（双线边框 + 大标题 + 价格/日期 + Hub） ================= -->
      <header class="masthead">
        <!-- 顶栏细线：卷号/价格/日期 + Hub 返回（必须有 router-link） -->
        <div class="mast-top mono small-caps">
          <span class="mast-top-left">VOL. CXXVIII — NO. 42 — 创刊于 2024</span>
          <router-link to="/" class="hub-link mono small-caps">← Hub</router-link>
          <span class="mast-top-right">PRICE 2¢ · {{ todayLabel }} · SYNTHINK DAILY TRIBUNE</span>
        </div>

        <!-- 双线边框主标题区 -->
        <div class="mast-main">
          <!-- 上粗规则线 3px + 下细线 1px（报纸经典双线） -->
          <div class="rule rule--thick" aria-hidden="true"></div>
          <!-- 大标题：Tiempos 衬线 900，全大写，极紧字距 -->
          <h1 class="mast-title">SYNTHINK DAILY</h1>
          <div class="mast-subtitle mono small-caps">
            <span>“多智能体写作的官方记录”</span>
            <span class="mast-diamond">◆</span>
            <span>EST. 2024 — POSTMODERN ARCHIVE EDITION</span>
            <span class="mast-diamond">◆</span>
            <span>多声部 · 纸的物理性 · 档案馆特刊</span>
          </div>
          <div class="rule rule--thick" aria-hidden="true"></div>

          <!-- 二级信息栏：天气/版次/价格细节 + 座右铭 -->
          <div class="mast-info mono small-caps">
            <span>WEATHER: 纸面微黄 · 湿度 42% · 适合翻阅</span>
            <span>EDITION: 报纸档案 / NEWSPAPER ARCHIVE — MOUSE FRIENDLY</span>
            <span>PRICE: 2¢ · 6 篇入档 · 点击推门阅内页</span>
          </div>
          <!-- 双线底框：外层 double 效果由 masthead 的 border 实现 -->
          <div class="rule rule--double" aria-hidden="true"></div>
        </div>
      </header>

      <!-- ================= 分类条（Group 过滤，黑底白字） ================= -->
      <nav class="category-bar mono small-caps" aria-label="分类过滤">
        <span class="cat-label">SECTIONS ▸</span>
        <button
          class="cat-btn"
          :class="{ active: groupFilter === '' }"
          @click="groupFilter = ''"
        >
          全部版面
        </button>
        <button
          v-for="g in mockGroups"
          :key="g.id"
          class="cat-btn"
          :class="{ active: groupFilter === g.id }"
          @click="groupFilter = groupFilter === g.id ? '' : g.id"
        >
          <span class="cat-icon">{{ g.icon }}</span>
          {{ g.name }}
          <i class="cat-count">{{ g.count }}</i>
        </button>
        <span class="cat-meta">
          {{ filteredPosts.length }} 篇入档 · {{ headlinePost ? '头条已选' : '无头条' }}
        </span>
      </nav>

      <!-- ================= 头条跨栏（mockPosts[0] 大字） ================= -->
      <section
        v-if="headlinePost"
        class="headline"
        @click="openDetail(headlinePost)"
        role="button"
        tabindex="0"
        @keydown.enter="openDetail(headlinePost)"
        :aria-label="`阅读头条 ${headlinePost.title}`"
      >
        <!-- 头条顶标注：跨栏通栏黑条 -->
        <div class="headline-flag mono small-caps">
          <span>★ 头条 FRONT PAGE — EXTRA ★</span>
          <span>{{ headlinePost.group.icon }} {{ headlinePost.group.name.toUpperCase() }} · {{ headlinePost.createdAt }}</span>
          <span>NO. {{ headlinePost.id.toUpperCase() }} — 详见内页 A1</span>
        </div>

        <div class="headline-body">
          <!-- 左：大图 grayscale 高对比 -->
          <div class="headline-cover-wrap">
            <img :src="headlinePost.cover" :alt="headlinePost.title" class="headline-cover" loading="eager" />
            <div class="img-caption mono small-caps">
              FIG. 1 — {{ headlinePost.author.display_name }} 摄 · {{ headlinePost.author.bio.slice(0, 28) }}
            </div>
            <!-- 图片压角：报纸常用 L 型角标 -->
            <span class="corner corner--tl" aria-hidden="true"></span>
            <span class="corner corner--br" aria-hidden="true"></span>
          </div>

          <!-- 右：大字标题 + 引语 + 元信息 -->
          <div class="headline-text">
            <div class="kicker mono small-caps">
              <span class="kicker-dot" :style="{ background: headlinePost.author.color }"></span>
              {{ headlinePost.group.name }} · 特写
              <span class="kicker-sep">—</span>
              {{ headlinePost.tags.map(t=>t.name).join(' / ') }}
            </div>
            <!-- 衬线 900 超大字，报纸头条字号 -->
            <h2 class="headline-title">{{ headlinePost.title.toUpperCase() }}</h2>
            <p class="headline-intro">{{ headlinePost.intro }}</p>
            <!-- 分隔细规则线 -->
            <div class="rule rule--thin" aria-hidden="true"></div>
            <div class="headline-meta mono small-caps">
              <span class="byline">
                <span class="av" :style="{ background: headlinePost.author.color }">{{ headlinePost.author.avatar }}</span>
                BY {{ headlinePost.author.display_name.toUpperCase() }}
                <span class="byline-username">@{{ headlinePost.author.username }}</span>
              </span>
              <span class="meta-stats">
                {{ headlinePost.views.toLocaleString() }} 阅 · {{ getLikes(headlinePost.id) }} 赞 · {{ headlinePost.comments }} 评
              </span>
            </div>
            <div class="headline-actions">
              <span class="read-hint mono small-caps">点击推门 → 进入内页 A1 阅读全文</span>
              <button class="like-inline mono small-caps" :class="{ liked: likedMap[headlinePost.id] }" @click.stop="toggleLike(headlinePost.id)">
                {{ likedMap[headlinePost.id] ? '♥ 已赞' : '♡ 点赞' }} {{ getLikes(headlinePost.id) }}
              </button>
            </div>
          </div>
        </div>
        <!-- 头条底粗规则线 3px -->
        <div class="rule rule--thick" aria-hidden="true"></div>
      </section>

      <!-- 无结果占位 -->
      <div v-if="!headlinePost" class="empty mono small-caps brutal-border">
        暂无符合条件的头条 — 请调整档案抽屉筛选
      </div>

      <!-- ================= 下方：3 栏报纸分栏 + 档案抽屉 ================= -->
      <div class="lower">
        <!-- 左：3 栏分栏主体（6 篇分 3×2，带规则线） -->
        <main class="columns">
          <!-- 栏头：版面说明 -->
          <div class="columns-head mono small-caps">
            <span>INNER PAGES — A2 / A3 / A4 · 三栏排版 · 规则线分隔 · 点击标题推门</span>
            <span>共 {{ gridPosts.length }} 篇 · {{ groupFilter ? mockGroups.find(g=>g.id===groupFilter)?.name : '全部' }}</span>
          </div>

          <!-- 3 栏网格：每栏 2 篇，共 6 格（若过滤后不足 6 则按实际渲染） -->
          <div class="grid-3">
            <article
              v-for="(p, idx) in gridPosts"
              :key="p.id"
              class="col-article"
              :class="{ breakthrough: idx === 0 && gridPosts.length >= 4 }"
              @click="openDetail(p)"
              role="button"
              tabindex="0"
              @keydown.enter="openDetail(p)"
              :aria-label="`打开 ${p.title}`"
            >
              <!-- 顶部细栏目标签：黑底白字 or 白底黑字 small-caps -->
              <div class="article-flag mono small-caps">
                <span class="flag-left">{{ p.group.icon }} {{ p.group.name.toUpperCase() }}</span>
                <span class="flag-right">{{ p.createdAt }} · P.{{ idx + 2 }}</span>
              </div>
              <!-- 图片：grayscale 对比度高 -->
              <div class="article-cover-wrap">
                <img :src="p.cover" :alt="p.title" class="article-cover" loading="lazy" />
                <span class="img-credit mono small-caps">{{ p.author.display_name }} · FIG.{{ idx+2 }}</span>
              </div>
              <!-- 标题：衬线 900，全大写 small-caps 感 -->
              <h3 class="article-title">{{ p.title.toUpperCase() }}</h3>
              <!-- 作者行：等宽 + 小字 -->
              <div class="article-byline mono small-caps">
                <span class="av small" :style="{ background: p.author.color }">{{ p.author.avatar }}</span>
                {{ p.author.display_name }} — {{ p.views }} 阅
              </div>
              <p class="article-intro">{{ p.intro }}</p>
              <!-- 标签：描边 pill，小写等宽 -->
              <div class="article-tags mono">
                <span v-for="t in p.tags" :key="t.id" class="tag" :style="{ borderColor: '#0a0a0f' }">
                  <span class="tag-dot" :style="{ background: t.color }"></span>{{ t.name }}
                </span>
              </div>
              <div class="article-foot mono small-caps">
                <span>♥ {{ getLikes(p.id) }} · 💬 {{ p.comments }}</span>
                <button class="foot-like" :class="{ liked: likedMap[p.id] }" @click.stop="toggleLike(p.id)">{{ likedMap[p.id] ? '♥' : '♡' }}</button>
                <span class="push">推门 →</span>
              </div>
              <!-- 悬停时顶部 3px 粗线高亮（通过伪元素实现） -->
            </article>

            <!-- 占位：不足 6 篇时用档案说明补齐，保持 3×2 网格视觉完整 -->
            <div v-for="n in Math.max(0, 6 - gridPosts.length)" :key="'ph-' + n" class="col-article placeholder">
              <div class="article-flag mono small-caps">
                <span class="flag-left">— 档案留白 —</span>
                <span class="flag-right">VACANT</span>
              </div>
              <div class="placeholder-body mono small-caps">
                <span class="ph-title">此栏待刊</span>
                <span>调整上方 Sections 或右侧抽屉以填满版面</span>
                <span class="ph-ornament">❧</span>
              </div>
            </div>
          </div>

          <!-- 底栏：印刷信息 + 版权 -->
          <div class="columns-foot mono small-caps">
            <span>PRINTED ON #E8E4D8 — OIL INK · GRAYSCALE · CONTRAST HIGH — SYNTHINK ARCHIVE</span>
            <span>第 A2–A4 版 · 共 {{ mockPosts.length }} 篇归档</span>
          </div>
        </main>

        <!-- 右：档案抽屉（按日期 / 标签过滤） -->
        <aside class="drawer" aria-label="档案抽屉">
          <div class="drawer-head mono small-caps">
            <span class="drawer-title">档案抽屉 · DRAWER</span>
            <button class="drawer-reset mono small-caps" @click="resetDrawer">重置 ↺</button>
          </div>

          <!-- 日期过滤 -->
          <section class="drawer-section">
            <div class="drawer-sec-title mono small-caps">按日期 DATE</div>
            <div class="date-list">
              <button
                class="drawer-btn mono small-caps"
                :class="{ active: dateFilter === '' }"
                @click="dateFilter = ''"
              >
                全部日期
              </button>
              <button
                v-for="d in dateOptions"
                :key="d.value"
                class="drawer-btn mono small-caps"
                :class="{ active: dateFilter === d.value }"
                @click="dateFilter = dateFilter === d.value ? '' : d.value"
              >
                {{ d.label }}
                <i class="count">{{ d.count }}</i>
              </button>
            </div>
          </section>

          <!-- 标签过滤 -->
          <section class="drawer-section">
            <div class="drawer-sec-title mono small-caps">按标签 TAG</div>
            <div class="drawer-tags">
              <button
                v-for="t in mockTags"
                :key="t.id"
                class="drawer-btn mono small-caps tag-btn"
                :class="{ active: tagFilter === t.id }"
                @click="tagFilter = tagFilter === t.id ? null : t.id"
              >
                <span class="dot" :style="{ background: t.color }"></span>
                {{ t.name }}
              </button>
              <button
                class="drawer-btn mono small-caps"
                :class="{ active: tagFilter === null }"
                @click="tagFilter = null"
              >
                全部标签
              </button>
            </div>
          </section>

          <!-- 抽屉内统计 + 印刷装饰 -->
          <section class="drawer-section stats">
            <div class="drawer-sec-title mono small-caps">馆藏统计</div>
            <div class="stat-grid mono small-caps">
              <div class="stat"><span>POSTS</span><b>{{ mockPosts.length }}</b></div>
              <div class="stat"><span>入选</span><b>{{ filteredPosts.length }}</b></div>
              <div class="stat"><span>TAGS</span><b>{{ mockTags.length }}</b></div>
              <div class="stat"><span>GROUPS</span><b>{{ mockGroups.length }}</b></div>
            </div>
            <div class="drawer-ornament" aria-hidden="true">
              <span>❧</span>
              <span class="line"></span>
              <span>❧</span>
            </div>
            <p class="drawer-note mono">
              提示：档案抽屉与上方 Sections 联动过滤。<br />
              点击任意文章卡片即“推门”进入报纸内页详情（本地 Mock，不请求后端）。
            </p>
          </section>

          <!-- 抽屉底部：快速清单（当前过滤结果标题索引） -->
          <section class="drawer-section index">
            <div class="drawer-sec-title mono small-caps">本期索引 INDEX — {{ filteredPosts.length }} 篇</div>
            <div class="index-list">
              <button
                v-for="(p, i) in filteredPosts"
                :key="p.id"
                class="index-item mono"
                :class="{ active: selectedPost?.id === p.id }"
                @click="openDetail(p)"
              >
                <span class="idx-num">{{ String(i+1).padStart(2,'0') }}</span>
                <span class="idx-title">{{ p.title }}</span>
                <span class="idx-meta">{{ p.createdAt }}</span>
              </button>
            </div>
          </section>
        </aside>
      </div>

      <!-- ================= 报尾 ================= -->
      <footer class="footer mono small-caps">
        <div class="rule rule--thick" aria-hidden="true"></div>
        <div class="footer-row">
          <span>SynthSpark · 多智能体博客系统 — SynthInk 新闻档案 · BRUTALIST NEWSPAPER DEMO</span>
          <span>纯 Mock · 鼠标友好 · 单文件 SFC · 字体 TIEMPOS / COURIER</span>
        </div>
        <div class="footer-row sub">
          <span>设色：报纸灰 #e8e4d8 · 边框 2px 黑 · 粗规则线 3px · GRAYSCALE 对比度高 · NOISE 油墨纹理</span>
          <span>© 2026 SYNTHINK DAILY — PRINTED IN BROWSER</span>
        </div>
      </footer>
    </div>

    <!-- ================= 推门详情（报纸内页） ================= -->
    <Transition name="paper-fade">
      <div v-if="selectedPost" class="detail-overlay" @click.self="closeDetail" @wheel.stop>
        <!-- 内页纸张：双栏 + 跨栏标题，报纸内页版式 -->
        <article class="inner-paper">
          <button class="close-btn mono small-caps" @click="closeDetail" aria-label="关闭内页">× 关闭内页</button>

          <!-- 内页报头：小号 masthead -->
          <div class="inner-head mono small-caps">
            <span>SYNTHINK DAILY — 内页 A{{ detailPageNo }}</span>
            <span>{{ selectedPost.group.icon }} {{ selectedPost.group.name.toUpperCase() }} · {{ selectedPost.createdAt }}</span>
            <span>NO. {{ selectedPost.id.toUpperCase() }}</span>
          </div>
          <div class="rule rule--thick" aria-hidden="true"></div>

          <!-- 跨栏大标题 -->
          <h2 class="inner-title">{{ selectedPost.title.toUpperCase() }}</h2>
          <div class="inner-kicker mono small-caps">
            <span class="av" :style="{ background: selectedPost.author.color }">{{ selectedPost.author.avatar }}</span>
            BY {{ selectedPost.author.display_name.toUpperCase() }} · {{ selectedPost.author.bio }}
            <span class="sep">—</span>
            {{ selectedPost.views.toLocaleString() }} 阅 · {{ getLikes(selectedPost.id) }} 赞
          </div>

          <!-- 两栏正文：左图右文，保留报纸分栏感 -->
          <div class="inner-body">
            <div class="inner-cover-wrap">
              <img :src="selectedPost.cover" :alt="selectedPost.title" class="inner-cover" />
              <div class="inner-caption mono small-caps">FIG. — {{ selectedPost.intro.slice(0, 46) }}…</div>
              <div class="inner-actions mono small-caps">
                <button class="action-btn primary" :class="{ liked: likedMap[selectedPost.id] }" @click="toggleLike(selectedPost.id)">
                  {{ likedMap[selectedPost.id] ? '♥ 已赞' : '♡ 点赞' }} · {{ getLikes(selectedPost.id) }}
                </button>
                <button class="action-btn" @click="shareMock">⎙ 分享（Mock）</button>
                <button class="action-btn" @click="closeDetail">← 返回版面</button>
              </div>
              <div class="inner-tags mono small-caps">
                <span v-for="t in selectedPost.tags" :key="t.id" class="inner-tag">
                  <span class="dot" :style="{ background: t.color }"></span>{{ t.name }}
                </span>
              </div>
            </div>

            <div class="inner-text">
              <!-- 引语块：左侧粗边 -->
              <blockquote class="pullquote">{{ selectedPost.intro }}</blockquote>
              <div class="rule rule--thin" aria-hidden="true"></div>
              <!-- 正文：使用 Markdown 渲染器，报纸主题高对比油墨风格 -->
              <MarkdownRenderer :content="selectedPost.content" theme="newspaper" />
              <div class="rule rule--thin" aria-hidden="true"></div>
              <!-- 文末装饰 -->
              <div class="end-mark" aria-hidden="true">❧ 完 ❧</div>
            </div>
          </div>

          <!-- 底栏：继续阅读索引（同过滤结果的上一篇/下一篇） -->
          <div class="inner-nav mono small-caps">
            <button class="nav-btn" :disabled="!prevPost" @click="prevPost && openDetail(prevPost)">← 上一篇<span v-if="prevPost">：{{ prevPost.title.slice(0,14) }}…</span></button>
            <span class="nav-center">{{ detailIndex + 1 }} / {{ filteredPosts.length }} · {{ selectedPost.group.name }}</span>
            <button class="nav-btn" :disabled="!nextPost" @click="nextPost && openDetail(nextPost)">下一篇<span v-if="nextPost">：{{ nextPost.title.slice(0,14) }}…</span> →</button>
          </div>
        </article>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
/**
 * Brutalist Newspaper 报纸档案 Demo
 * 设计语言「Newspaper」：背景 #e8e4d8 / border 2px 黑 / 粗规则线 3px
 * 字体 Tiempos(衬线 900) + Courier(等宽)，油墨噪点，图片 grayscale 高对比，全大写 small-caps
 * 交互：报头双线边框+大标题+价格/日期+Hub、头条跨栏(mockPosts[0] 大字)、下方 3×2 分栏+规则线
 *       分类条 Group 过滤(黑底白字)、档案抽屉(日期/标签过滤)、点击推门详情(报纸内页)
 * 约束：纯 Mock、鼠标友好、单文件 SFC、中文注释、用 ref 管理 filter/selectedPost、本地点赞
 */
import { ref, computed } from 'vue'
import { mockPosts, mockGroups, mockTags } from '@/mock/data'
import type { MockPost } from '@/mock/data'
// 引入 Markdown 渲染器：详情页正文由纯文本 <pre> 升级为富文本渲染
import MarkdownRenderer from '@/components/MarkdownRenderer.vue'

// —— 顶部日期：展示今日（静态 Mock 日期，避免 hydration 差异，用固定文案亦可） ——
const todayLabel = new Date().toLocaleDateString('zh-CN', { year: 'numeric', month: 'long', day: 'numeric' })

// —— 用 ref 管理：过滤状态 / 选中文章（需求明确） ——
const groupFilter = ref<string>('') // 分类条 Group 过滤，空为全部
const tagFilter = ref<number | null>(null) // 档案抽屉标签过滤
const dateFilter = ref<string>('') // 档案抽屉日期过滤（YYYY-MM）
const selectedPost = ref<MockPost | null>(null) // 推门详情当前文章

// —— 本地点赞：likedMap 记录是否已赞，localLikes 记录本地点赞数（初始拷贝自 mock） ——
const likedMap = ref<Record<string, boolean>>({})
const localLikes = ref<Record<string, number>>({})
for (const p of mockPosts) localLikes.value[p.id] = p.likes

/** 获取本地点赞数（含切换） */
function getLikes(id: string): number {
  return localLikes.value[id] ?? 0
}
/** 切换点赞：本地 +1 / -1，不请求后端 */
function toggleLike(id: string): void {
  const next = !likedMap.value[id]
  likedMap.value[id] = next
  localLikes.value[id] = (localLikes.value[id] ?? 0) + (next ? 1 : -1)
}

// —— 推门详情：打开/关闭 + 分享 Mock ——
function openDetail(p: MockPost): void { selectedPost.value = p }
function closeDetail(): void { selectedPost.value = null }
function shareMock(): void {
  // 纯 Mock 分享提示
  if (typeof window !== 'undefined') window.alert('链接已复制（Mock）— ' + selectedPost.value?.title)
}

// —— 日期选项：从 mockPosts 中按 YYYY-MM 聚合 ——
const dateOptions = computed(() => {
  const map = new Map<string, number>()
  for (const p of mockPosts) {
    const key = p.createdAt.slice(0, 7) // YYYY-MM
    map.set(key, (map.get(key) ?? 0) + 1)
  }
  return [...map.entries()]
    .sort((a, b) => b[0].localeCompare(a[0]))
    .map(([value, count]) => ({
      value,
      count,
      label: value.replace('-', '年') + '月'
    }))
})

// —— 过滤后的文章列表：Group + Tag + Date 三重联动 ——
const filteredPosts = computed<MockPost[]>(() => {
  let list = [...mockPosts]
  if (groupFilter.value) list = list.filter(p => p.group.id === groupFilter.value)
  if (tagFilter.value !== null) list = list.filter(p => p.tags.some(t => t.id === tagFilter.value))
  if (dateFilter.value) list = list.filter(p => p.createdAt.startsWith(dateFilter.value))
  return list
})

// —— 头条：跨栏大字，取过滤后首篇；若无过滤则为 mockPosts[0] ——
const headlinePost = computed<MockPost | null>(() => filteredPosts.value[0] ?? null)

// —— 下方 3 栏分栏：6 篇分 3×2，取过滤后除头条外的最多 6 篇（不足用占位补齐） ——
const gridPosts = computed<MockPost[]>(() => {
  const withoutHeadline = filteredPosts.value.filter(p => p.id !== headlinePost.value?.id)
  // 若过滤后仅 1 篇（即头条），下方展示全部过滤结果除头条（可能为空，用占位保持版式）
  // 若过滤后较多，则展示接下来 6 篇，满足 3×2 视觉
  return withoutHeadline.slice(0, 6)
})

// —— 详情内页：计算当前在过滤列表中的索引与上下篇 ——
const detailIndex = computed(() => {
  if (!selectedPost.value) return -1
  return filteredPosts.value.findIndex(p => p.id === selectedPost.value!.id)
})
const detailPageNo = computed(() => {
  // 内页页码：A1 为头条，其余按索引顺延
  if (detailIndex.value <= 0) return '1'
  return String(detailIndex.value + 1)
})
const prevPost = computed<MockPost | null>(() => {
  const idx = detailIndex.value
  if (idx > 0) return filteredPosts.value[idx - 1] ?? null
  return null
})
const nextPost = computed<MockPost | null>(() => {
  const idx = detailIndex.value
  if (idx >= 0 && idx < filteredPosts.value.length - 1) return filteredPosts.value[idx + 1] ?? null
  return null
})

// —— 重置档案抽屉所有过滤 + 分类条 ——
function resetDrawer(): void {
  groupFilter.value = ''
  tagFilter.value = null
  dateFilter.value = ''
}
</script>

<style scoped>
/* 字体：标题衬线 900（Tiempos 替代 Playfair Display 900） + 正文等宽 Courier Prime */
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@900&family=Courier+Prime:wght@400;700&family=EB+Garamond:wght@800&display=swap');

/* —— 工具类：等宽 + small-caps —— */
.mono {
  font-family: 'Courier Prime', 'Courier New', ui-monospace, SFMono-Regular, Menlo, monospace;
}
.small-caps {
  font-variant: small-caps;
  text-transform: uppercase;
  letter-spacing: 0.06em;
}

/* —— 根容器：报纸灰 #e8e4d8 + 油墨噪点 —— */
.newspaper-root {
  min-height: 100vh;
  background: #e8e4d8;
  color: #0a0a0a;
  position: relative;
  overflow-x: clip;
  padding: 18px 14px 28px;
}
/* 油墨纹理：SVG 噪点 + 极淡纸纤维，叠加于背景 */
.ink-texture {
  position: fixed;
  inset: 0;
  pointer-events: none;
  z-index: 0;
  opacity: 0.38;
  /* SVG 噪点（feTurbulence）内联，营造油墨不均匀感 */
  background-image:
    url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='180' height='180'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.92' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.22'/%3E%3C/svg%3E"),
    radial-gradient(ellipse at 18% 12%, rgba(0,0,0,0.04), transparent 55%),
    radial-gradient(ellipse at 88% 88%, rgba(0,0,0,0.05), transparent 52%);
  background-size: 180px 180px, auto, auto;
  mix-blend-mode: multiply;
}

/* —— 纸张容器：米白纸 + 2px 黑边 + 柔和阴影 —— */
.paper {
  position: relative;
  z-index: 1;
  max-width: 1280px;
  margin: 0 auto;
  background: #f6f1e1;
  /* 报纸纸色：比 #e8e4d8 略亮一档，形成纸张层级 */
  border: 2px solid #0a0a0a;
  box-shadow: 8px 8px 0 #0a0a0a, 0 12px 32px rgba(0,0,0,0.18);
  /* 纸纤维：极淡内噪点 */
  background-image:
    radial-gradient(ellipse at 50% 0%, rgba(0,0,0,0.03), transparent 70%),
    repeating-linear-gradient(0deg, transparent 0 2px, rgba(0,0,0,0.015) 3px, transparent 4px);
}

/* ================= 报头 ================= */
.masthead {
  border-bottom: 2px solid #0a0a0a;
  background: #f6f1e1;
}
.mast-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  padding: 8px 12px;
  font-size: 10px;
  font-weight: 700;
  border-bottom: 1px solid #0a0a0a;
  background: #efebe0;
  flex-wrap: wrap;
}
.mast-top-left,
.mast-top-right {
  font-size: 10px;
  letter-spacing: 0.08em;
  white-space: nowrap;
}
.hub-link {
  background: #0a0a0a;
  color: #f6f1e1;
  padding: 5px 14px;
  font-size: 11px;
  font-weight: 800;
  letter-spacing: 0.08em;
  border: 2px solid #0a0a0a;
  text-decoration: none;
  transition: background 0.16s, color 0.16s, transform 0.16s;
  will-change: transform;
}
.hub-link:hover {
  background: #f6f1e1;
  color: #0a0a0a;
  transform: translateY(-1px);
}
.mast-main {
  padding: 14px 14px 10px;
  text-align: center;
}
.mast-title {
  font-family: 'Playfair Display', 'EB Garamond', Georgia, serif;
  font-weight: 900;
  font-size: clamp(42px, 9vw, 92px);
  line-height: 0.88;
  letter-spacing: -0.02em;
  color: #0a0a0a;
  margin: 8px 0 6px;
  /* 油墨略微洇开感：极细描边 */
  -webkit-text-stroke: 0.4px rgba(0,0,0,0.08);
}
.mast-subtitle {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  flex-wrap: wrap;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.12em;
  color: #1a1a1a;
  margin-bottom: 8px;
}
.mast-diamond {
  font-size: 8px;
  transform: translateY(-1px);
}
.mast-info {
  display: flex;
  justify-content: space-between;
  gap: 10px;
  flex-wrap: wrap;
  font-size: 9px;
  font-weight: 700;
  letter-spacing: 0.08em;
  padding: 8px 2px 6px;
  border-top: 1px solid #0a0a0a;
  border-bottom: 1px solid #0a0a0a;
  margin-top: 6px;
}
/* 规则线：粗 3px + 细 1px 双线 */
.rule {
  height: 1px;
  background: #0a0a0a;
}
.rule--thick {
  height: 3px;
  background: #0a0a0a;
  border-bottom: 1px solid #0a0a0a;
  box-shadow: 0 1px 0 #0a0a0a;
  /* 视觉上形成 3px 主线 + 1px 辅线间距 2px 的经典报纸双线 */
  position: relative;
}
.rule--thick::after {
  content: '';
  position: absolute;
  left: 0;
  right: 0;
  bottom: -4px;
  height: 1px;
  background: #0a0a0a;
}
.rule--double {
  height: 4px;
  background: transparent;
  border-top: 3px solid #0a0a0a;
  border-bottom: 1px solid #0a0a0a;
  margin-top: 6px;
}
.rule--thin {
  height: 1px;
  background: #0a0a0a;
  opacity: 0.9;
  margin: 10px 0;
}

/* ================= 分类条：黑底白字 ================= */
.category-bar {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
  padding: 10px 12px;
  background: #0a0a0a;
  color: #f6f1e1;
  border-top: 2px solid #0a0a0a;
  border-bottom: 2px solid #0a0a0a;
}
.cat-label {
  font-size: 11px;
  font-weight: 800;
  letter-spacing: 0.14em;
  padding-right: 8px;
  border-right: 1px solid rgba(246,241,225,0.3);
  margin-right: 2px;
}
.cat-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.06em;
  background: transparent;
  color: #f6f1e1;
  border: 1px solid rgba(246,241,225,0.9);
  cursor: pointer;
  transition: background 0.16s, color 0.16s, transform 0.14s, border-color 0.16s;
  will-change: transform;
}
.cat-btn:hover {
  background: rgba(246,241,225,0.12);
  transform: translateY(-1px);
}
.cat-btn.active {
  background: #f6f1e1;
  color: #0a0a0a;
  border-color: #f6f1e1;
  font-weight: 800;
}
.cat-icon { font-size: 12px; }
.cat-count {
  font-style: normal;
  font-size: 10px;
  padding: 1px 6px;
  border: 1px solid currentColor;
  border-radius: 999px;
  opacity: 0.9;
}
.cat-meta {
  margin-left: auto;
  font-size: 10px;
  letter-spacing: 0.08em;
  opacity: 0.9;
  white-space: nowrap;
}

/* ================= 头条跨栏 ================= */
.headline {
  border-bottom: 2px solid #0a0a0a;
  background: #f6f1e1;
  cursor: pointer;
  transition: background 0.16s;
}
.headline:hover {
  background: #fdfbf0;
}
.headline-flag {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  flex-wrap: wrap;
  padding: 8px 12px;
  background: #0a0a0a;
  color: #f6f1e1;
  font-size: 10px;
  font-weight: 800;
  letter-spacing: 0.1em;
}
.headline-body {
  display: grid;
  grid-template-columns: 1.05fr 1fr;
  gap: 18px;
  padding: 16px 16px 14px;
}
.headline-cover-wrap {
  position: relative;
  border: 2px solid #0a0a0a;
  background: #0a0a0a;
  overflow: hidden;
}
.headline-cover {
  width: 100%;
  height: 380px;
  object-fit: cover;
  display: block;
  /* 设计语言：grayscale 对比度高 */
  filter: grayscale(1) contrast(1.28) brightness(0.98) sepia(0.06);
  transition: filter 0.22s, transform 0.28s;
  will-change: transform;
}
.headline:hover .headline-cover {
  filter: grayscale(1) contrast(1.34) brightness(1.02) sepia(0.04);
  transform: scale(1.015);
}
.img-caption {
  padding: 6px 8px;
  font-size: 9px;
  letter-spacing: 0.06em;
  background: #efebe0;
  border-top: 2px solid #0a0a0a;
  color: #1a1a1a;
  text-align: left;
  line-height: 1.4;
}
.corner {
  position: absolute;
  width: 18px;
  height: 18px;
  border-color: #f6f1e1;
  border-style: solid;
  pointer-events: none;
}
.corner--tl {
  left: 6px;
  top: 6px;
  border-width: 2px 0 0 2px;
}
.corner--br {
  right: 6px;
  bottom: 28px;
  border-width: 0 2px 2px 0;
}
.headline-text {
  display: flex;
  flex-direction: column;
  gap: 10px;
  min-width: 0;
}
.kicker {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  font-size: 10px;
  font-weight: 800;
  letter-spacing: 0.12em;
  flex-wrap: wrap;
}
.kicker-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  display: inline-block;
  border: 1px solid #0a0a0a;
  flex-shrink: 0;
}
.kicker-sep { opacity: 0.4; }
.headline-title {
  font-family: 'Playfair Display', Georgia, serif;
  font-weight: 900;
  font-size: clamp(28px, 3.6vw, 46px);
  line-height: 0.95;
  letter-spacing: -0.015em;
  color: #0a0a0a;
  /* 报纸头条：全大写已在模板层处理，行间紧凑 */
  text-wrap: balance;
}
.headline-intro {
  font-family: 'EB Garamond', Georgia, serif;
  font-size: 17px;
  line-height: 1.45;
  color: #1a1a1a;
  font-style: italic;
  border-left: 3px solid #0a0a0a;
  padding-left: 12px;
}
.headline-meta {
  display: flex;
  justify-content: space-between;
  gap: 10px;
  flex-wrap: wrap;
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.06em;
  padding-top: 2px;
}
.byline {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
}
.av {
  width: 22px;
  height: 22px;
  display: inline-grid;
  place-items: center;
  border: 1px solid #0a0a0a;
  border-radius: 50%;
  font-size: 11px;
  flex-shrink: 0;
}
.av.small {
  width: 18px;
  height: 18px;
  font-size: 10px;
}
.byline-username {
  font-weight: 400;
  letter-spacing: 0.04em;
  opacity: 0.7;
  text-transform: none;
  font-variant: normal;
}
.meta-stats {
  opacity: 0.8;
  white-space: nowrap;
}
.headline-actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  flex-wrap: wrap;
  margin-top: 2px;
}
.read-hint {
  font-size: 10px;
  font-weight: 800;
  letter-spacing: 0.08em;
  text-decoration: underline;
  text-underline-offset: 3px;
  text-decoration-thickness: 1.5px;
}
.like-inline {
  padding: 6px 12px;
  font-size: 11px;
  font-weight: 800;
  background: #fff;
  color: #0a0a0a;
  border: 2px solid #0a0a0a;
  cursor: pointer;
  transition: background 0.16s, color 0.16s, transform 0.14s;
  will-change: transform;
}
.like-inline:hover { transform: translateY(-1px); }
.like-inline.liked {
  background: #0a0a0a;
  color: #f6f1e1;
}

/* 空状态 */
.empty {
  margin: 16px;
  padding: 18px;
  text-align: center;
  font-size: 12px;
  font-weight: 800;
  letter-spacing: 0.08em;
  background: #fff;
  border: 2px solid #0a0a0a;
}

/* ================= 下方：3 栏 + 抽屉 ================= */
.lower {
  display: grid;
  grid-template-columns: 1fr 320px;
  gap: 0;
  background: #f6f1e1;
}
/* 3 栏主体 */
.columns {
  border-right: 2px solid #0a0a0a;
  min-width: 0;
}
.columns-head {
  display: flex;
  justify-content: space-between;
  gap: 10px;
  flex-wrap: wrap;
  padding: 8px 12px;
  font-size: 10px;
  font-weight: 800;
  letter-spacing: 0.08em;
  background: #efebe0;
  border-bottom: 2px solid #0a0a0a;
}
.grid-3 {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  /* 规则线：用 gap + 背景色模拟纵向规则线 */
  gap: 0;
  background: #0a0a0a;
  /* 外层已是纸色，grid 背景黑即为规则线 */
  border-bottom: 2px solid #0a0a0a;
}
.col-article {
  background: #f6f1e1;
  padding: 14px 14px 12px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  cursor: pointer;
  position: relative;
  transition: background 0.16s;
  min-width: 0;
  /* 右侧与底部规则线由 grid 背景透出，额外补 1px 内描边保证印刷感 */
  border-right: 1px solid #0a0a0a;
  border-bottom: 1px solid #0a0a0a;
}
.col-article:nth-child(3n) {
  border-right: none;
}
.col-article:nth-child(n+4) {
  border-bottom: none;
}
.col-article:hover {
  background: #fdfbf0;
}
.col-article::before {
  /* 悬停顶部 3px 粗线：默认透明，悬停显现 */
  content: '';
  position: absolute;
  left: 0;
  right: 0;
  top: 0;
  height: 3px;
  background: #0a0a0a;
  opacity: 0;
  transition: opacity 0.16s;
}
.col-article:hover::before {
  opacity: 1;
}
.article-flag {
  display: flex;
  justify-content: space-between;
  gap: 8px;
  font-size: 9px;
  font-weight: 800;
  letter-spacing: 0.08em;
  padding-bottom: 8px;
  border-bottom: 1px solid #0a0a0a;
}
.flag-left { font-weight: 900; }
.flag-right { opacity: 0.7; white-space: nowrap; }
.article-cover-wrap {
  position: relative;
  border: 2px solid #0a0a0a;
  background: #0a0a0a;
  overflow: hidden;
}
.article-cover {
  width: 100%;
  height: 148px;
  object-fit: cover;
  display: block;
  filter: grayscale(1) contrast(1.32) brightness(0.96) sepia(0.05);
  transition: filter 0.18s, transform 0.22s;
  will-change: transform;
}
.col-article:hover .article-cover {
  filter: grayscale(1) contrast(1.38) brightness(1.02);
  transform: scale(1.02);
}
.img-credit {
  display: block;
  padding: 4px 6px;
  font-size: 8px;
  letter-spacing: 0.06em;
  background: #efebe0;
  border-top: 1px solid #0a0a0a;
  color: #1a1a1a;
  line-height: 1.3;
}
.article-title {
  font-family: 'Playfair Display', Georgia, serif;
  font-weight: 900;
  font-size: 18px;
  line-height: 1.02;
  letter-spacing: -0.01em;
  color: #0a0a0a;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
  min-height: 56px;
}
.article-byline {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.06em;
  flex-wrap: wrap;
}
.article-intro {
  font-family: 'Courier Prime', monospace;
  font-size: 12px;
  line-height: 1.6;
  color: #1a1a1a;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
  min-height: 58px;
  border-left: 2px solid #0a0a0a;
  padding-left: 8px;
  background: rgba(232,228,216,0.35);
}
.article-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}
.tag {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 3px 8px;
  font-size: 10px;
  font-weight: 700;
  background: #fff;
  color: #0a0a0a;
  border: 1px solid #0a0a0a;
  letter-spacing: 0.04em;
}
.tag-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  display: inline-block;
  border: 1px solid #0a0a0a;
  flex-shrink: 0;
}
.article-foot {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.06em;
  border-top: 1px solid #0a0a0a;
  padding-top: 8px;
  margin-top: auto;
}
.foot-like {
  width: 22px;
  height: 22px;
  display: inline-grid;
  place-items: center;
  background: #fff;
  border: 1px solid #0a0a0a;
  cursor: pointer;
  font-size: 10px;
  line-height: 1;
  transition: background 0.16s, color 0.16s;
}
.foot-like.liked {
  background: #0a0a0a;
  color: #f6f1e1;
}
.push {
  margin-left: auto;
  text-decoration: underline;
  text-underline-offset: 2px;
}
/* 占位卡：保持网格完整 */
.col-article.placeholder {
  cursor: default;
  background: #efebe0;
  justify-content: center;
  min-height: 320px;
}
.col-article.placeholder:hover { background: #efebe0; }
.col-article.placeholder::before { display: none; }
.placeholder-body {
  flex: 1;
  display: grid;
  place-items: center;
  gap: 8px;
  text-align: center;
  padding: 24px 10px;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.08em;
  color: #1a1a1a;
  border: 1px dashed #0a0a0a;
  background: repeating-linear-gradient(45deg, transparent 0 6px, rgba(10,10,10,0.04) 6px 7px);
}
.ph-title {
  font-family: 'Playfair Display', serif;
  font-weight: 900;
  font-size: 16px;
  letter-spacing: 0.04em;
}
.ph-ornament { font-size: 18px; opacity: 0.5; }

.columns-foot {
  display: flex;
  justify-content: space-between;
  gap: 10px;
  flex-wrap: wrap;
  padding: 8px 12px;
  font-size: 9px;
  font-weight: 700;
  letter-spacing: 0.08em;
  background: #efebe0;
  border-top: 1px solid #0a0a0a;
}

/* ================= 档案抽屉 ================= */
.drawer {
  background: #efebe0;
  border-left: 2px solid #0a0a0a;
  display: flex;
  flex-direction: column;
  min-height: 100%;
}
.drawer-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  padding: 10px 12px;
  background: #0a0a0a;
  color: #f6f1e1;
  border-bottom: 2px solid #0a0a0a;
}
.drawer-title {
  font-size: 11px;
  font-weight: 900;
  letter-spacing: 0.14em;
}
.drawer-reset {
  padding: 4px 10px;
  font-size: 10px;
  font-weight: 800;
  background: #f6f1e1;
  color: #0a0a0a;
  border: 1px solid #f6f1e1;
  cursor: pointer;
  transition: background 0.16s, color 0.16s;
}
.drawer-reset:hover { background: #0a0a0a; color: #f6f1e1; border-color: #f6f1e1; }
.drawer-section {
  padding: 12px;
  border-bottom: 2px solid #0a0a0a;
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.drawer-section:last-child { border-bottom: none; }
.drawer-sec-title {
  font-size: 10px;
  font-weight: 900;
  letter-spacing: 0.12em;
  padding-bottom: 6px;
  border-bottom: 1px solid #0a0a0a;
}
.date-list,
.drawer-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 7px;
}
.drawer-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 10px;
  font-size: 11px;
  font-weight: 700;
  background: #fff;
  color: #0a0a0a;
  border: 2px solid #0a0a0a;
  cursor: pointer;
  transition: background 0.16s, color 0.16s, transform 0.14s;
  will-change: transform;
}
.drawer-btn:hover { transform: translateY(-1px); }
.drawer-btn.active {
  background: #0a0a0a;
  color: #f6f1e1;
  border-color: #0a0a0a;
}
.drawer-btn .count {
  font-style: normal;
  font-size: 10px;
  padding: 1px 5px;
  border: 1px solid currentColor;
  border-radius: 999px;
}
.drawer-btn.tag-btn .dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  display: inline-block;
  border: 1px solid #0a0a0a;
  flex-shrink: 0;
}
.stat-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
}
.stat {
  background: #fff;
  border: 2px solid #0a0a0a;
  padding: 8px;
  text-align: center;
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.stat span { font-size: 9px; letter-spacing: 0.08em; opacity: 0.7; font-weight: 700; }
.stat b { font-size: 18px; font-weight: 900; }
.drawer-ornament {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 2px 0;
  font-size: 12px;
}
.drawer-ornament .line {
  flex: 1;
  height: 1px;
  background: #0a0a0a;
}
.drawer-note {
  font-size: 11px;
  line-height: 1.6;
  color: #1a1a1a;
  background: #f6f1e1;
  border: 1px solid #0a0a0a;
  padding: 8px 10px;
  text-transform: none;
  font-variant: normal;
  letter-spacing: 0;
}
.index-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
  max-height: 260px;
  overflow: auto;
  padding-right: 2px;
  scrollbar-width: thin;
  scrollbar-color: #0a0a0a #efebe0;
}
.index-item {
  display: grid;
  grid-template-columns: 28px 1fr auto;
  gap: 8px;
  align-items: center;
  padding: 7px 8px;
  background: #fff;
  border: 1px solid #0a0a0a;
  cursor: pointer;
  text-align: left;
  transition: background 0.14s, color 0.14s, transform 0.14s;
  will-change: transform;
}
.index-item:hover { transform: translateX(2px); background: #f6f1e1; }
.index-item.active { background: #0a0a0a; color: #f6f1e1; }
.idx-num { font-size: 10px; font-weight: 800; letter-spacing: 0.06em; opacity: 0.7; }
.idx-title { font-size: 11px; font-weight: 700; line-height: 1.3; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.idx-meta { font-size: 10px; opacity: 0.7; white-space: nowrap; }

/* ================= 报尾 ================= */
.footer {
  background: #efebe0;
  border-top: 2px solid #0a0a0a;
  padding: 10px 12px 12px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.footer-row {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  flex-wrap: wrap;
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.06em;
}
.footer-row.sub { opacity: 0.7; font-size: 9px; }

/* ================= 详情内页（报纸内页推门） ================= */
.detail-overlay {
  position: fixed;
  inset: 0;
  z-index: 40;
  background: rgba(232,228,216,0.88);
  backdrop-filter: blur(6px);
  -webkit-backdrop-filter: blur(6px);
  display: flex;
  align-items: flex-start;
  justify-content: center;
  padding: 18px;
  overflow: auto;
}
.inner-paper {
  position: relative;
  width: min(980px, 100%);
  background: #fdfbf0;
  border: 2px solid #0a0a0a;
  box-shadow: 10px 10px 0 #0a0a0a, 0 16px 40px rgba(0,0,0,0.22);
  padding: 0 0 14px;
  margin: auto;
  /* 内页也叠加极淡噪点 */
  background-image: radial-gradient(ellipse at 50% 0%, rgba(0,0,0,0.025), transparent 68%);
}
.close-btn {
  position: sticky;
  top: 10px;
  float: right;
  margin: 10px 10px 0 0;
  z-index: 2;
  padding: 7px 14px;
  font-size: 11px;
  font-weight: 900;
  background: #0a0a0a;
  color: #f6f1e1;
  border: 2px solid #0a0a0a;
  cursor: pointer;
  transition: background 0.16s, color 0.16s;
}
.close-btn:hover { background: #f6f1e1; color: #0a0a0a; }
.inner-head {
  display: flex;
  justify-content: space-between;
  gap: 10px;
  flex-wrap: wrap;
  padding: 10px 14px 8px;
  font-size: 10px;
  font-weight: 800;
  letter-spacing: 0.08em;
  background: #efebe0;
  border-bottom: 2px solid #0a0a0a;
}
.inner-title {
  font-family: 'Playfair Display', Georgia, serif;
  font-weight: 900;
  font-size: clamp(26px, 4vw, 40px);
  line-height: 0.98;
  letter-spacing: -0.01em;
  text-align: center;
  padding: 14px 18px 6px;
  color: #0a0a0a;
  text-wrap: balance;
}
.inner-kicker {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  flex-wrap: wrap;
  padding: 0 18px 10px;
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-align: center;
  border-bottom: 1px solid #0a0a0a;
  margin: 0 18px;
}
.inner-kicker .sep { opacity: 0.4; }
.inner-body {
  display: grid;
  grid-template-columns: 380px 1fr;
  gap: 18px;
  padding: 16px 18px;
}
.inner-cover-wrap {
  position: relative;
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.inner-cover {
  width: 100%;
  height: 320px;
  object-fit: cover;
  display: block;
  border: 2px solid #0a0a0a;
  filter: grayscale(1) contrast(1.32) brightness(0.97) sepia(0.05);
}
.inner-caption {
  font-size: 10px;
  line-height: 1.5;
  background: #efebe0;
  border: 1px solid #0a0a0a;
  padding: 6px 8px;
  letter-spacing: 0.04em;
  text-transform: none;
  font-variant: normal;
}
.inner-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
.action-btn {
  padding: 7px 12px;
  font-size: 11px;
  font-weight: 800;
  background: #fff;
  color: #0a0a0a;
  border: 2px solid #0a0a0a;
  cursor: pointer;
  transition: background 0.16s, color 0.16s, transform 0.14s;
  will-change: transform;
}
.action-btn:hover { transform: translateY(-1px); }
.action-btn.primary { background: #0a0a0a; color: #f6f1e1; }
.action-btn.primary.liked { background: #f6f1e1; color: #0a0a0a; }
.inner-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}
.inner-tag {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 8px;
  font-size: 10px;
  font-weight: 800;
  background: #fff;
  border: 1px solid #0a0a0a;
}
.inner-tag .dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  border: 1px solid #0a0a0a;
  display: inline-block;
}
.inner-text {
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.pullquote {
  font-family: 'EB Garamond', Georgia, serif;
  font-size: 18px;
  line-height: 1.4;
  font-style: italic;
  color: #1a1a1a;
  border-left: 3px solid #0a0a0a;
  padding: 8px 12px;
  background: #f6f1e1;
  margin: 0;
}
.content {
  white-space: pre-wrap;
  word-break: break-word;
  font-size: 12px;
  line-height: 1.82;
  background: #fff;
  border: 2px solid #0a0a0a;
  padding: 14px 12px;
  margin: 0;
  max-height: 420px;
  overflow: auto;
  color: #0a0a0a;
  scrollbar-width: thin;
  scrollbar-color: #0a0a0a #fff;
}
/* 首字下沉：仅首段首字母放大（通过 pre 首字符视觉模拟，改用首行加粗） */
.content::first-letter {
  font-size: 1.6em;
  font-weight: 900;
  float: left;
  line-height: 1;
  padding-right: 4px;
}
.end-mark {
  text-align: center;
  font-size: 14px;
  letter-spacing: 0.18em;
  font-weight: 900;
  padding: 4px 0;
  border-top: 1px solid #0a0a0a;
  border-bottom: 1px solid #0a0a0a;
  background: #efebe0;
}
.inner-nav {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  flex-wrap: wrap;
  padding: 10px 14px 0;
  border-top: 2px solid #0a0a0a;
  margin: 6px 18px 0;
  font-size: 10px;
  font-weight: 800;
  letter-spacing: 0.06em;
}
.nav-btn {
  padding: 7px 12px;
  background: #fff;
  color: #0a0a0a;
  border: 2px solid #0a0a0a;
  cursor: pointer;
  font-size: 10px;
  font-weight: 800;
  transition: background 0.16s, color 0.16s, opacity 0.16s;
  max-width: 42%;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.nav-btn:disabled { opacity: 0.4; cursor: not-allowed; }
.nav-btn:not(:disabled):hover { background: #0a0a0a; color: #f6f1e1; }
.nav-center {
  opacity: 0.7;
  text-align: center;
  flex: 1;
}

/* —— 过渡：推门纸张淡入 + 内页轻缩放 —— */
.paper-fade-enter-active { transition: opacity 0.22s, transform 0.28s cubic-bezier(0.16, 1, 0.3, 1); }
.paper-fade-leave-active { transition: opacity 0.18s, transform 0.2s ease; }
.paper-fade-enter-from,
.paper-fade-leave-to { opacity: 0; }
.paper-fade-enter-from .inner-paper { transform: translateY(10px) scale(0.985); }
.paper-fade-leave-to .inner-paper { transform: translateY(8px) scale(0.988); }

/* ================= 响应式 ================= */
@media (max-width: 1100px) {
  .lower { grid-template-columns: 1fr; }
  .columns { border-right: none; border-bottom: 2px solid #0a0a0a; }
  .drawer { border-left: none; }
  .grid-3 { grid-template-columns: repeat(2, 1fr); }
  .col-article:nth-child(3n) { border-right: 1px solid #0a0a0a; }
  .col-article:nth-child(2n) { border-right: none; }
  .col-article:nth-child(n+4) { border-bottom: 1px solid #0a0a0a; }
  .col-article:nth-last-child(-n+2) { border-bottom: none; }
  .inner-body { grid-template-columns: 1fr; }
  .inner-cover { height: 280px; }
  .headline-body { grid-template-columns: 1fr; }
  .headline-cover { height: 320px; }
}
@media (max-width: 640px) {
  .newspaper-root { padding: 10px 8px 20px; }
  .paper { box-shadow: 5px 5px 0 #0a0a0a; }
  .mast-title { font-size: 40px; }
  .mast-top { justify-content: center; text-align: center; }
  .grid-3 { grid-template-columns: 1fr; }
  .col-article { border-right: none !important; }
  .col-article:nth-last-child(1) { border-bottom: none; }
  .category-bar { gap: 6px; }
  .cat-meta { flex-basis: 100%; margin-left: 0; padding-top: 4px; border-top: 1px solid rgba(246,241,225,0.2); }
  .inner-nav { flex-direction: column; }
  .nav-btn { max-width: 100%; width: 100%; }
}
</style>
