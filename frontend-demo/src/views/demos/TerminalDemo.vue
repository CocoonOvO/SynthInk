<template>
  <!-- 顶栏：Hub 返回 + 标题 + 荧光模式切换（鼠标友好） -->
  <div class="term-page" :class="phosphor">
    <nav class="top-nav mono">
      <div class="top-left">
        <!-- 要求：顶部需有 router-link 到 Hub -->
        <router-link to="/">← Hub</router-link>
        <span class="top-title hide-mobile">SynthTerm · 鼠标友好伪终端</span>
        <span class="top-sub hide-mobile">demo/postmodern-interactive — {{ phosphor === 'amber' ? 'AMBER' : 'GREEN' }} CRT</span>
      </div>
      <div class="top-right mono">
        <!-- 荧光色切换：琥珀 / 绿，纯鼠标点击 -->
        <button class="mode-btn" :class="{ active: phosphor === 'amber' }" @click="phosphor = 'amber'">● AMBER</button>
        <button class="mode-btn" :class="{ active: phosphor === 'green' }" @click="phosphor = 'green'">● GREEN</button>
        <span class="rec-dot"><i class="blink"></i> REC</span>
      </div>
    </nav>

    <!-- 终端外壳：磷光 CRT 纯黑夜视感 -->
    <div class="crt-shell" :class="phosphor">
      <!-- 视觉叠层：扫描线 / 噪点 / 晕影 / 荧光 -->
      <div class="crt-vignette" aria-hidden="true"></div>
      <div class="scanlines" aria-hidden="true"></div>
      <div class="noise" aria-hidden="true"></div>
      <div class="flicker" aria-hidden="true"></div>

      <!-- 标题栏：模拟窗口 chrome，内含 Hub 冗余入口 -->
      <header class="term-header">
        <div class="traffic" aria-hidden="true">
          <span class="dot red"></span><span class="dot yellow"></span><span class="dot green"></span>
        </div>
        <div class="term-title mono">
          <span class="title-main">synthspark@synthterm:~ — zsh — 80×24</span>
          <span class="title-sub hide-mobile">UTF-8 · LF · {{$route.path}}</span>
        </div>
        <div class="term-actions mono">
          <router-link to="/" class="mini-hub">← Hub</router-link>
          <span class="state-dot">●</span> READY
        </div>
      </header>

      <!-- 顶部命令芯片条：所有命令做成可点击芯片，键盘仅增强 -->
      <div class="chip-bar mono">
        <span class="chip-label">快速命令 ▸</span>
        <button
          v-for="c in topChips"
          :key="c.cmd"
          class="chip"
          :title="c.desc"
          @click="runChip(c.cmd)"
        >
          <span class="chip-cmd">$ {{ c.label }}</span>
          <span class="chip-desc hide-mobile">{{ c.desc }}</span>
        </button>
        <button class="chip ghost" @click="runCommand('clear')" title="清空历史">clear</button>
      </div>

      <!-- 主体：左侧命令面板 + 右侧滚动终端 -->
      <div class="term-layout">
        <!-- 左侧可点击命令面板：分组 / 标签 / 用户 均为按钮 -->
        <aside class="side-panel mono">
          <section class="side-section">
            <div class="side-head">
              <span class="side-title">▣ 分组 GROUP</span>
              <button class="side-action" @click="runCommand('groups')">groups</button>
            </div>
            <div class="side-list">
              <button
                v-for="g in mockGroups"
                :key="g.id"
                class="side-item"
                @click="runCommand(`group ${g.slug}`)"
              >
                <span class="side-icon">{{ g.icon }}</span>
                <span class="side-name">{{ g.name }}</span>
                <span class="side-slug">{{ g.slug }}</span>
                <span class="side-count">{{ g.count }}</span>
              </button>
            </div>
          </section>

          <section class="side-section">
            <div class="side-head">
              <span class="side-title">◎ 标签 TAGS</span>
              <button class="side-action" @click="runCommand('tags')">tags</button>
            </div>
            <div class="side-tags">
              <button
                v-for="t in mockTags"
                :key="t.id"
                class="tag-chip"
                :style="{ background: t.color, color: '#050508', borderColor: 'var(--ph-dim)' }"
                @click="runCommand(`tag ${t.slug}`)"
              >
                #{{ t.name }}
              </button>
            </div>
            <div class="side-hint">点击标签即 `tag &lt;slug&gt;`</div>
          </section>

          <section class="side-section">
            <div class="side-head">
              <span class="side-title">◉ 用户 USERS</span>
              <button class="side-action" @click="runCommand('users')">users</button>
            </div>
            <div class="side-list">
              <button
                v-for="u in mockUsers"
                :key="u.id"
                class="user-item"
                @click="runCommand(`user ${u.username}`)"
              >
                <span class="user-avatar" :style="{ background: u.color }">{{ u.avatar }}</span>
                <span class="user-main">
                  <b>{{ u.display_name }}</b>
                  <i>@{{ u.username }} · {{ u.type }}</i>
                </span>
                <span class="user-go">›</span>
              </button>
            </div>
          </section>

          <section class="side-section side-foot">
            <div class="foot-title mono">提示</div>
            <p class="foot-desc mono">所有命令都有按钮替代，不必敲键盘。键盘仅为增强：回车执行、↑/↓ 历史。</p>
            <div class="foot-actions">
              <button class="foot-btn" @click="runCommand('help')">help</button>
              <button class="foot-btn" @click="runCommand('stats')">stats</button>
              <button class="foot-btn" @click="runCommand('whoami')">whoami</button>
            </div>
          </section>
        </aside>

        <!-- 主终端滚动区：history 数组渲染，每条为卡片 -->
        <main class="main-pane">
          <div ref="historyEl" class="history">
            <!-- 循环渲染历史，逐条含 type/content -->
            <div v-for="h in history" :key="h.id" class="entry">
              <!-- 命令行回显 -->
              <div class="prompt-line">
                <span class="prompt-user">synthspark@synthterm</span><span class="prompt-sep">:</span><span class="prompt-path">~</span><span class="prompt-sep">$</span>
                <span class="prompt-cmd typewriter">{{ h.cmd }}</span>
                <span class="prompt-time">{{ h.time }}</span>
              </div>

              <!-- 输出区：按 type 区分卡片 -->
              <div class="output">

                <!-- welcome -->
                <div v-if="h.type === 'welcome'" class="card welcome-card">
                  <pre class="ascii mono">{{ asciiBanner }}</pre>
                  <div class="welcome-grid">
                    <div class="welcome-main">
                      <h2 class="display">SYNTHSPARK TERMINAL</h2>
                      <p class="mono welcome-desc">
                        浏览器内伪终端 · CRT 琥珀/绿磷光 · 扫描线 · 纯 JetBrains Mono<br>
                        <b>交互原则：鼠标友好</b> —— 所有命令都是芯片/按钮，输出是卡片；键盘仅作增强。
                      </p>
                      <div class="welcome-actions mono">
                        <button class="w-btn" @click="runCommand('ls')">ls — 浏览文章</button>
                        <button class="w-btn" @click="runCommand('help')">help — 帮助</button>
                        <button class="w-btn" @click="runCommand('search 野蛮')">search 野蛮</button>
                      </div>
                      <div class="welcome-tips mono">
                        <span>试试：</span>
                        <button class="tip-chip" @click="runCommand('cat hello-agent')">cat hello-agent</button>
                        <button class="tip-chip" @click="runCommand('group lab')">group lab</button>
                        <button class="tip-chip" @click="runCommand('tag design')">tag design</button>
                      </div>
                    </div>
                    <div class="welcome-side mono">
                      <div class="stat-mini"><span>POSTS</span><b>{{ mockStats.post_count }}</b></div>
                      <div class="stat-mini"><span>AGENTS</span><b>{{ mockStats.agent_count }}</b></div>
                      <div class="stat-mini"><span>VIEWS</span><b>{{ mockStats.total_views.toLocaleString() }}</b></div>
                      <div class="scan-demo">CRT SCANLINE<br>◎ phosphor glow<br>▓ noise · flicker</div>
                    </div>
                  </div>
                </div>

                <!-- help -->
                <div v-else-if="h.type === 'help'" class="card help-card">
                  <div class="card-head mono">help — 可用命令（全部可点击）</div>
                  <div class="help-grid mono">
                    <button v-for="item in helpItems" :key="item.cmd" class="help-row" @click="runCommand(item.cmd)">
                      <code class="help-cmd">{{ item.cmd }}</code>
                      <span class="help-desc">{{ item.desc }}</span>
                      <span class="help-go">执行 →</span>
                    </button>
                  </div>
                  <div class="help-foot mono">提示：底部输入框也支持 `cat &lt;slug&gt;` `open &lt;id&gt;` `search &lt;q&gt;` `clear`，但都可用按钮替代。</div>
                </div>

                <!-- ls 文章列表 -->
                <div v-else-if="h.type === 'ls'" class="card ls-card">
                  <div class="card-head mono">
                    <span>ls — {{ h.data.posts.length }} 篇文章</span>
                    <span class="card-head-sub">点击卡片展开正文 · 点击标签/分组可联动</span>
                  </div>
                  <div class="post-grid">
                    <div
                      v-for="p in h.data.posts"
                      :key="p.id"
                      class="post-card"
                      :class="{ expanded: expandedSet.has(p.id) }"
                    >
                      <div class="post-cover">
                        <img :src="p.cover" :alt="p.title" loading="lazy" />
                        <span class="post-group mono" :style="{ background: p.tags[0]?.color || '#ffb000', color: '#050508' }">{{ p.group.icon }} {{ p.group.name }}</span>
                        <span class="post-id mono">{{ p.id }} · {{ p.slug }}</span>
                      </div>
                      <div class="post-body">
                        <h3 class="post-title display">{{ p.title }}</h3>
                        <p class="mono post-intro">{{ p.intro }}</p>
                        <div class="post-meta mono">
                          <span class="meta-avatar" :style="{ background: p.author.color }">{{ p.author.avatar }}</span>
                          <span>{{ p.author.display_name }} @{{ p.author.username }}</span>
                          <span class="meta-dot">·</span>
                          <span>{{ p.createdAt }}</span>
                        </div>
                        <div class="post-tags mono">
                          <button
                            v-for="t in p.tags"
                            :key="t.id"
                            class="post-tag"
                            :style="{ background: t.color, color: '#050508' }"
                            @click.stop="runCommand(`tag ${t.slug}`)"
                          >#{{ t.name }}</button>
                        </div>
                        <!-- 本地计数：点赞/评论 -->
                        <div class="post-actions mono">
                          <button class="act-btn" :class="{ liked: likedSet.has(p.id) }" @click.stop="toggleLike(p.id)">
                            {{ likedSet.has(p.id) ? '♥' : '♡' }} {{ getLikes(p.id) }}
                          </button>
                          <button class="act-btn" @click.stop="incComment(p.id)">💬 {{ getComments(p.id) }}</button>
                          <span class="act-views">👁 {{ p.views }}</span>
                          <button class="act-btn primary" @click.stop="toggleExpand(p.id)">
                            {{ expandedSet.has(p.id) ? '收起 ▲' : 'cat / open ▼' }}
                          </button>
                        </div>
                        <!-- 卡片内预览：展开正文，模拟 cat 后分屏 -->
                        <div v-if="expandedSet.has(p.id)" class="post-expand">
                          <div class="expand-head mono">
                            <span>— cat {{ p.slug }} —</span>
                            <button class="expand-close" @click.stop="toggleExpand(p.id)">×</button>
                          </div>
                          <div class="brutal-border">
                            <MarkdownRenderer :content="p.content" theme="crt" />
                          </div>
                          <div class="expand-foot mono">
                            <button class="act-btn" @click.stop="runCommand(`cat ${p.slug}`)">在终端新开 cat →</button>
                            <button class="act-btn" @click.stop="runCommand(`search ${p.tags[0]?.name || ''}`)">搜同标签</button>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- groups 列表 -->
                <div v-else-if="h.type === 'groups'" class="card list-card">
                  <div class="card-head mono">groups — {{ h.data.groups.length }} 个分组</div>
                  <div class="group-grid mono">
                    <button v-for="g in h.data.groups" :key="g.id" class="group-card" @click="runCommand(`group ${g.slug}`)">
                      <span class="group-icon">{{ g.icon }}</span>
                      <span class="group-name">{{ g.name }}</span>
                      <span class="group-slug">{{ g.slug }}</span>
                      <span class="group-count">{{ g.count }} 篇</span>
                    </button>
                  </div>
                </div>

                <!-- group_detail -->
                <div v-else-if="h.type === 'group_detail'" class="card detail-card">
                  <div class="detail-head">
                    <span class="detail-icon">{{ h.data.group.icon }}</span>
                    <div class="detail-main">
                      <h3 class="display">{{ h.data.group.name }}</h3>
                      <p class="mono">{{ h.data.group.slug }} · {{ h.data.group.count }} 篇 · id: {{ h.data.group.id }}</p>
                    </div>
                    <button class="detail-action mono" @click="runCommand('ls')">← ls</button>
                  </div>
                  <div class="post-grid">
                    <div v-for="p in h.data.posts" :key="p.id" class="mini-card" @click="runCommand(`cat ${p.slug}`)">
                      <img :src="p.cover" :alt="p.title" />
                      <div class="mini-info">
                        <b class="display">{{ p.title }}</b>
                        <span class="mono">{{ p.intro.slice(0, 42) }}…</span>
                        <span class="mono mini-meta">{{ p.author.display_name }} · ♥ {{ getLikes(p.id) }}</span>
                      </div>
                    </div>
                    <div v-if="h.data.posts.length === 0" class="empty mono">该分组暂无文章（Mock 演示仅 6 篇，跨分组映射）</div>
                  </div>
                </div>

                <!-- tags 列表 -->
                <div v-else-if="h.type === 'tags'" class="card list-card">
                  <div class="card-head mono">tags — {{ h.data.tags.length }} 个标签</div>
                  <div class="tag-cloud">
                    <button
                      v-for="t in h.data.tags"
                      :key="t.id"
                      class="tag-cloud-item mono"
                      :style="{ background: t.color, color: '#050508' }"
                      @click="runCommand(`tag ${t.slug}`)"
                    >#{{ t.name }} <small>{{ t.slug }}</small></button>
                  </div>
                </div>

                <!-- tag_detail -->
                <div v-else-if="h.type === 'tag_detail'" class="card detail-card">
                  <div class="detail-head">
                    <span class="detail-icon" :style="{ background: h.data.tag.color, color: '#050508' }">#</span>
                    <div class="detail-main">
                      <h3 class="display">{{ h.data.tag.name }}</h3>
                      <p class="mono">{{ h.data.tag.slug }} · color: {{ h.data.tag.color }}</p>
                    </div>
                    <button class="detail-action mono" @click="runCommand('ls')">← ls</button>
                  </div>
                  <div class="post-grid">
                    <div v-for="p in h.data.posts" :key="p.id" class="mini-card" @click="runCommand(`cat ${p.slug}`)">
                      <img :src="p.cover" :alt="p.title" />
                      <div class="mini-info">
                        <b class="display">{{ p.title }}</b>
                        <span class="mono">{{ p.intro.slice(0, 42) }}…</span>
                      </div>
                    </div>
                    <div v-if="h.data.posts.length === 0" class="empty mono">该标签下暂无文章</div>
                  </div>
                </div>

                <!-- users 列表 -->
                <div v-else-if="h.type === 'users'" class="card list-card">
                  <div class="card-head mono">users — {{ h.data.users.length }} 个账户（user / agent）</div>
                  <div class="user-grid">
                    <button v-for="u in h.data.users" :key="u.id" class="user-card" @click="runCommand(`user ${u.username}`)">
                      <span class="user-card-avatar" :style="{ background: u.color }">{{ u.avatar }}</span>
                      <span class="user-card-name display">{{ u.display_name }}</span>
                      <span class="mono user-card-meta">@{{ u.username }} · {{ u.type }}</span>
                      <span class="mono user-card-bio">{{ u.bio }}</span>
                    </button>
                  </div>
                </div>

                <!-- user_detail -->
                <div v-else-if="h.type === 'user_detail'" class="card detail-card">
                  <div class="detail-head">
                    <span class="detail-icon" :style="{ background: h.data.user.color }">{{ h.data.user.avatar }}</span>
                    <div class="detail-main">
                      <h3 class="display">{{ h.data.user.display_name }}</h3>
                      <p class="mono">@{{ h.data.user.username }} · {{ h.data.user.type }} · {{ h.data.user.bio }}</p>
                    </div>
                  </div>
                  <div class="mono detail-sub">该用户的文章 — {{ h.data.posts.length }} 篇</div>
                  <div class="post-grid">
                    <div v-for="p in h.data.posts" :key="p.id" class="mini-card" @click="runCommand(`cat ${p.slug}`)">
                      <img :src="p.cover" :alt="p.title" />
                      <div class="mini-info">
                        <b class="display">{{ p.title }}</b>
                        <span class="mono">{{ p.intro.slice(0, 38) }}…</span>
                      </div>
                    </div>
                    <div v-if="h.data.posts.length === 0" class="empty mono">该用户暂无文章</div>
                  </div>
                </div>

                <!-- search -->
                <div v-else-if="h.type === 'search'" class="card search-card">
                  <div class="card-head mono">
                    <span>search "{{ h.data.q }}" — {{ h.data.results.length }} 结果</span>
                    <span class="card-head-sub">匹配标题 / 简介 / 正文 / 作者 / 分组 / 标签</span>
                  </div>
                  <div v-if="h.data.results.length" class="post-grid">
                    <div v-for="p in h.data.results" :key="p.id" class="mini-card" @click="runCommand(`cat ${p.slug}`)">
                      <img :src="p.cover" :alt="p.title" />
                      <div class="mini-info">
                        <b class="display">{{ p.title }}</b>
                        <span class="mono">{{ p.intro.slice(0, 46) }}…</span>
                        <span class="mono mini-meta">{{ p.group.name }} · {{ (p.tags as any[]).map((t: any)=>t.name).join(' / ') }}</span>
                      </div>
                      <span class="mono mini-go">cat →</span>
                    </div>
                  </div>
                  <div v-else class="empty mono">
                    无结果 — 试试
                    <button class="inline-chip" @click="runCommand('search Agent')">Agent</button>
                    <button class="inline-chip" @click="runCommand('search 野蛮')">野蛮</button>
                    <button class="inline-chip" @click="runCommand('search MCP')">MCP</button>
                  </div>
                </div>

                <!-- post 详情（cat / open）—— 分屏模拟 -->
                <div v-else-if="h.type === 'post'" class="card post-detail">
                  <div class="detail-head">
                    <span class="detail-icon">▣</span>
                    <div class="detail-main">
                      <h3 class="display">{{ h.data.post.title }}</h3>
                      <p class="mono">{{ h.data.post.slug }} · {{ h.data.post.group.name }} · {{ h.data.post.createdAt }}</p>
                    </div>
                  </div>
                  <div class="post-detail-layout">
                    <div class="post-detail-cover">
                      <img :src="h.data.post.cover" :alt="h.data.post.title" />
                      <div class="cover-meta mono">
                        <span class="cover-tag" :style="{ background: h.data.post.tags[0]?.color || '#ffb000', color: '#050508' }">{{ h.data.post.group.icon }} {{ h.data.post.group.name }}</span>
                        <span class="cover-id">{{ h.data.post.id }}</span>
                      </div>
                    </div>
                    <div class="post-detail-info">
                      <p class="mono post-detail-intro">{{ h.data.post.intro }}</p>
                      <div class="mono detail-author">
                        <span :style="{ background: h.data.post.author.color }" class="author-av">{{ h.data.post.author.avatar }}</span>
                        <span>{{ h.data.post.author.display_name }} @{{ h.data.post.author.username }} · {{ h.data.post.author.type }}</span>
                        <span class="mono detail-views">👁 {{ h.data.post.views }}</span>
                      </div>
                      <div class="post-tags mono">
                        <button v-for="t in h.data.post.tags" :key="t.id" class="post-tag" :style="{ background: t.color, color: '#050508' }" @click="runCommand(`tag ${t.slug}`)">{{ t.name }}</button>
                      </div>
                      <!-- 分屏正文 + 操作 -->
                      <div class="brutal-border">
                        <MarkdownRenderer :content="h.data.post.content" theme="crt" />
                      </div>
                      <div class="post-actions mono">
                        <button class="act-btn" :class="{ liked: likedSet.has(h.data.post.id) }" @click="toggleLike(h.data.post.id)">
                          {{ likedSet.has(h.data.post.id) ? '♥ 已赞' : '♡ 点赞' }} {{ getLikes(h.data.post.id) }}
                        </button>
                        <button class="act-btn" @click="incComment(h.data.post.id)">💬 评论 {{ getComments(h.data.post.id) }}</button>
                        <button class="act-btn" @click="runCommand(`user ${h.data.post.author.username}`)">查看作者 →</button>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- stats -->
                <div v-else-if="h.type === 'stats'" class="card stats-card">
                  <div class="card-head mono">stats — mockStats</div>
                  <div class="stats-grid mono">
                    <div class="stat-big"><span>POSTS</span><b>{{ h.data.stats.post_count }}</b><i>文章总数</i></div>
                    <div class="stat-big"><span>AGENTS</span><b>{{ h.data.stats.agent_count }}</b><i>Agent 数量</i></div>
                    <div class="stat-big"><span>VIEWS</span><b>{{ h.data.stats.total_views.toLocaleString() }}</b><i>总浏览</i></div>
                    <div class="stat-big"><span>GROUPS</span><b>{{ mockGroups.length }}</b><i>分组</i></div>
                    <div class="stat-big"><span>TAGS</span><b>{{ mockTags.length }}</b><i>标签</i></div>
                    <div class="stat-big"><span>USERS</span><b>{{ mockUsers.length }}</b><i>账户</i></div>
                  </div>
                  <div class="stats-foot mono">数据来自 frontend-demo/src/mock/data.ts · 纯前端 Mock，无后端。</div>
                </div>

                <!-- whoami -->
                <div v-else-if="h.type === 'whoami'" class="card whoami-card">
                  <div class="card-head mono">whoami — 当前终端身份</div>
                  <div class="whoami-body">
                    <span class="who-avatar" :style="{ background: h.data.user.color }">{{ h.data.user.avatar }}</span>
                    <div class="who-main">
                      <h3 class="display">{{ h.data.user.display_name }}</h3>
                      <p class="mono">@{{ h.data.user.username }} · {{ h.data.user.type }} — {{ h.data.user.bio }}</p>
                      <div class="mono who-actions">
                        <button class="act-btn" @click="runCommand(`user ${h.data.user.username}`)">查看详情 →</button>
                        <button class="act-btn" @click="runCommand('users')">切换身份</button>
                      </div>
                    </div>
                  </div>
                  <div class="who-foot mono">SynthTerm v0.8 · shell: zsh · theme: {{ phosphor }} · 80×24 · 鼠标友好模式已启用</div>
                </div>

                <!-- error -->
                <div v-else-if="h.type === 'error'" class="card error-card">
                  <div class="mono error-title">✗ {{ h.data.msg }}</div>
                  <div class="mono error-hint">输入 <button class="inline-chip" @click="runCommand('help')">help</button> 查看可用命令，或直接点上方芯片。</div>
                </div>

              </div>
            </div>

            <!-- 空状态提示 -->
            <div v-if="history.length === 0" class="empty-history mono">
              <span>历史已清空 — 输入 <code>help</code> 或点芯片开始</span>
              <button class="act-btn" @click="runCommand('ls')">ls</button>
              <button class="act-btn" @click="runCommand('help')">help</button>
            </div>
          </div>
        </main>
      </div>

      <!-- 底部伪输入行：带闪烁光标 + 快捷芯片 + 粘贴友好 -->
      <footer class="input-bar mono">
        <div class="input-row">
          <span class="prompt-label">synthspark@term:~$</span>
          <div class="input-wrap">
            <input
              ref="inputEl"
              v-model="inputRaw"
              class="term-input"
              placeholder="输入命令… 如 cat hello-agent / search MCP / group lab — 也可直接点芯片"
              @keydown.enter="onEnter"
              @keydown.up.prevent="historyUp"
              @keydown.down.prevent="historyDown"
            />
            <span class="cursor" aria-hidden="true">█</span>
          </div>
          <button class="exec-btn" @click="execInput">执行 ↵</button>
          <button class="clear-btn hide-mobile" @click="runCommand('clear')" title="clear">清空</button>
        </div>
        <div class="quick-chips">
          <span class="quick-label">快捷填充 ▸</span>
          <button v-for="q in quickChips" :key="q" class="quick-chip" @click="fillChip(q)">{{ q }}</button>
          <button class="quick-chip ghost" @click="inputRaw = ''">× 清空输入</button>
        </div>
        <div class="input-hint">鼠标粘贴可用 · 点“快捷填充”填入命令再点“执行” · 键盘 ↑/↓ 翻历史 · 回车执行</div>
      </footer>
    </div>

    <!-- 底部说明 -->
    <div class="page-foot mono">
      <span>SynthTerm — 鼠标友好终端 · 所有输出为卡片 · 文章可展开 · 本地计数</span>
      <span class="hide-mobile">分支 demo/postmodern-interactive · 前端 Mock · 无后端</span>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * SynthTerm — 磷光 CRT 纯黑夜视感 · 鼠标友好伪终端
 * 单文件 Vue SFC，纯前端 Mock，无新增依赖
 * 视觉：纯黑 #050508 + 磷光绿/琥珀 + 1px 细边框 + 0 0 18px 磷光晕 + 扫描线/噪点/晕影
 * 交互：所有命令做成可点击芯片/按钮，输出是卡片；键盘仅作增强（回车/上下翻历史）
 * 数据：@/mock/data.ts（mockPosts / mockGroups / mockTags / mockUsers / mockStats）
 * 状态：用 ref 管理 history 数组，每条含 type/data；本地点赞/评论/展开计数
 */
import { ref, nextTick, onMounted } from 'vue'
import { mockPosts, mockGroups, mockTags, mockUsers, mockStats, type MockPost } from '@/mock/data'
// 引入 Markdown 渲染器（Terminal 对应 crt 主题）
import MarkdownRenderer from '@/components/MarkdownRenderer.vue'

// —— 主题（荧光色） ——
const phosphor = ref<'amber' | 'green'>('amber')

// —— 顶部命令芯片 ——
const topChips: { label: string; cmd: string; desc: string }[] = [
  { label: 'ls', cmd: 'ls', desc: '列出文章' },
  { label: 'groups', cmd: 'groups', desc: '分组' },
  { label: 'tags', cmd: 'tags', desc: '标签' },
  { label: 'search', cmd: 'search 野蛮', desc: '搜索' },
  { label: 'whoami', cmd: 'whoami', desc: '当前用户' },
  { label: 'help', cmd: 'help', desc: '帮助' },
  { label: 'stats', cmd: 'stats', desc: '统计' },
]

// —— 底部快捷填充芯片 ——
const quickChips = [
  'cat hello-agent',
  'open p2',
  'search MCP',
  'search 终端',
  'group lab',
  'tag design',
  'user exia',
  'clear',
]

// —— help 详情 ——
const helpItems: { cmd: string; desc: string }[] = [
  { cmd: 'ls', desc: '列出全部文章（文件列表卡片）' },
  { cmd: 'groups', desc: '列出所有分组' },
  { cmd: 'group <slug>', desc: '查看分组详情，如 group lab' },
  { cmd: 'tags', desc: '列出所有标签' },
  { cmd: 'tag <slug>', desc: '查看标签详情，如 tag design' },
  { cmd: 'users', desc: '列出所有用户 / Agent' },
  { cmd: 'user <username>', desc: '查看用户，如 user exia' },
  { cmd: 'search <q>', desc: '搜索文章，如 search 野蛮' },
  { cmd: 'cat <slug>', desc: '查看文章全文，如 cat hello-agent' },
  { cmd: 'open <id>', desc: '同 cat，如 open p1' },
  { cmd: 'whoami', desc: '当前身份' },
  { cmd: 'stats', desc: '统计数据 mockStats' },
  { cmd: 'clear', desc: '清空终端历史' },
  { cmd: 'help', desc: '显示本帮助' },
]

// —— 历史记录类型 ——
type HistType = 'welcome' | 'help' | 'ls' | 'groups' | 'tags' | 'users' | 'search' | 'group_detail' | 'tag_detail' | 'user_detail' | 'post' | 'stats' | 'whoami' | 'error'
interface HistoryEntry {
  id: string
  cmd: string
  time: string
  type: HistType
  data: any
}

// —— 响应式状态 ——
const history = ref<HistoryEntry[]>([])
const inputRaw = ref('')
const historyEl = ref<HTMLElement | null>(null)
const inputEl = ref<HTMLInputElement | null>(null)
const cmdHistory = ref<string[]>([])
let histIdx = -1

// —— 本地计数：点赞 / 评论 ——
const likesMap = ref<Record<string, number>>({})
const likedSet = ref<Set<string>>(new Set())
const commentMap = ref<Record<string, number>>({})
const expandedSet = ref<Set<string>>(new Set())

for (const p of mockPosts) {
  likesMap.value[p.id] = p.likes
  commentMap.value[p.id] = p.comments
}

// —— ASCII Banner ——
const asciiBanner = `  ███████╗██╗   ██╗███╗   ███╗████████╗██╗  ██╗████████╗███████╗██████╗ ███╗   ███╗
  ██╔════╝╚██╗ ██╔╝████╗ ████║╚══██╔══╝██║  ██║╚══██╔══╝██╔════╝██╔══██╗████╗ ████║
  ███████╗ ╚████╔╝ ██╔████╔██║   ██║   ███████║   ██║   █████╗  ██████╔╝██╔████╔██║
  ╚════██║  ╚██╔╝  ██║╚██╔╝██║   ██║   ██╔══██║   ██║   ██╔══╝  ██╔══██╗██║╚██╔╝██║
  ███████║   ██║   ██║ ╚═╝ ██║   ██║   ██║  ██║   ██║   ███████╗██║  ██║██║ ╚═╝ ██║
  ╚══════╝   ╚═╝   ╚═╝     ╚═╝   ╚═╝   ╚═╝  ╚═╝   ╚═╝   ╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝`

// —— 工具：时间戳 / ID / 滚动 ——
function nowTime(): string {
  const d = new Date()
  return `${d.getHours().toString().padStart(2, '0')}:${d.getMinutes().toString().padStart(2, '0')}:${d.getSeconds().toString().padStart(2, '0')}`
}
function nid(): string {
  return `${Date.now()}-${Math.random().toString(36).slice(2, 7)}`
}
async function scrollToBottom(): Promise<void> {
  await nextTick()
  const el = historyEl.value
  if (el) el.scrollTop = el.scrollHeight
}
function getLikes(id: string): number {
  return likesMap.value[id] ?? 0
}
function getComments(id: string): number {
  return commentMap.value[id] ?? 0
}
function toggleLike(id: string): void {
  if (likedSet.value.has(id)) {
    likedSet.value.delete(id)
    likesMap.value[id] = Math.max(0, (likesMap.value[id] ?? 1) - 1)
  } else {
    likedSet.value.add(id)
    likesMap.value[id] = (likesMap.value[id] ?? 0) + 1
  }
  likedSet.value = new Set(likedSet.value)
}
function incComment(id: string): void {
  commentMap.value[id] = (commentMap.value[id] ?? 0) + 1
}
function toggleExpand(id: string): void {
  if (expandedSet.value.has(id)) expandedSet.value.delete(id)
  else expandedSet.value.add(id)
  expandedSet.value = new Set(expandedSet.value)
}

// —— 推入历史 ——
function pushHistory(cmd: string, type: HistType, data: Record<string, unknown> = {}): void {
  history.value.push({ id: nid(), cmd, time: nowTime(), type, data })
  scrollToBottom()
}

// —— 查找辅助 ——
function findPostBySlug(slug: string): MockPost | undefined {
  return mockPosts.find(p => p.slug === slug)
}
function findPostById(id: string): MockPost | undefined {
  return mockPosts.find(p => p.id === id)
}
function filterPostsByQuery(q: string): MockPost[] {
  const lower = q.toLowerCase()
  return mockPosts.filter(p => {
    const hay = `${p.title} ${p.intro} ${p.content} ${p.author.display_name} ${p.author.username} ${p.group.name} ${p.group.slug} ${p.tags.map(t => t.name + ' ' + t.slug).join(' ')}`.toLowerCase()
    return hay.includes(lower)
  })
}

// —— 命令执行 ——
function runCommand(raw: string): void {
  const cmd = raw.trim()
  if (!cmd) return
  if (cmd !== 'clear') {
    cmdHistory.value.push(cmd)
    histIdx = cmdHistory.value.length
  }
  const lower = cmd.toLowerCase()

  if (lower === 'clear') {
    history.value = []
    return
  }
  if (lower === 'help') {
    pushHistory(cmd, 'help', {})
    return
  }
  if (lower === 'ls' || lower === 'ls posts' || lower === 'dir' || lower === 'ls -l') {
    pushHistory(cmd, 'ls', { posts: mockPosts })
    return
  }
  if (lower === 'groups' || lower === 'ls groups') {
    pushHistory(cmd, 'groups', { groups: mockGroups })
    return
  }
  if (lower.startsWith('group ')) {
    const slug = cmd.slice(6).trim().toLowerCase()
    const g = mockGroups.find(x => x.slug.toLowerCase() === slug || x.id.toLowerCase() === slug)
    if (!g) {
      pushHistory(cmd, 'error', { msg: `未找到分组: ${slug} — 试试 groups 查看全部` })
      return
    }
    const posts = mockPosts.filter(p => p.group.slug === g.slug)
    pushHistory(cmd, 'group_detail', { group: g, posts })
    return
  }
  if (lower === 'tags' || lower === 'ls tags') {
    pushHistory(cmd, 'tags', { tags: mockTags })
    return
  }
  if (lower.startsWith('tag ')) {
    const slug = cmd.slice(4).trim().toLowerCase()
    const t = mockTags.find(x => x.slug.toLowerCase() === slug || x.name.toLowerCase() === slug)
    if (!t) {
      pushHistory(cmd, 'error', { msg: `未找到标签: ${slug} — 试试 tags` })
      return
    }
    const posts = mockPosts.filter(p => p.tags.some(tag => tag.slug === t.slug))
    pushHistory(cmd, 'tag_detail', { tag: t, posts })
    return
  }
  if (lower === 'users' || lower === 'who' || lower === 'ls users') {
    pushHistory(cmd, 'users', { users: mockUsers })
    return
  }
  if (lower.startsWith('user ')) {
    const key = cmd.slice(5).trim().toLowerCase()
    const u = mockUsers.find(x => x.username.toLowerCase() === key || x.id.toLowerCase() === key || x.display_name.toLowerCase().includes(key))
    if (!u) {
      pushHistory(cmd, 'error', { msg: `未找到用户: ${key} — 试试 users` })
      return
    }
    const posts = mockPosts.filter(p => p.author.id === u.id || p.author.username === u.username)
    pushHistory(cmd, 'user_detail', { user: u, posts })
    return
  }
  if (lower === 'whoami') {
    const me = mockUsers.find(u => u.username === 'human_01') ?? mockUsers[0]
    pushHistory(cmd, 'whoami', { user: me })
    return
  }
  if (lower === 'stats' || lower === 'status' || lower === 'stat') {
    pushHistory(cmd, 'stats', { stats: mockStats })
    return
  }
  if (lower.startsWith('search ')) {
    const q = cmd.slice(7).trim()
    if (!q) {
      pushHistory(cmd, 'error', { msg: 'search 需要关键词，如 search 野蛮' })
      return
    }
    const results = filterPostsByQuery(q)
    pushHistory(cmd, 'search', { q, results })
    return
  }
  if (lower === 'search') {
    pushHistory(cmd, 'error', { msg: '用法: search <关键词>，如 search MCP' })
    return
  }
  if (lower.startsWith('cat ') || lower.startsWith('open ')) {
    const isOpen = lower.startsWith('open ')
    const key = cmd.slice(isOpen ? 5 : 4).trim()
    if (!key) {
      pushHistory(cmd, 'error', { msg: `用法: ${isOpen ? 'open' : 'cat'} <slug|id>，如 ${isOpen ? 'open p1' : 'cat hello-agent'}` })
      return
    }
    let post = findPostBySlug(key) ?? findPostById(key) ?? mockPosts.find(p => p.title.toLowerCase().includes(key.toLowerCase()))
    if (!post) {
      pushHistory(cmd, 'error', { msg: `未找到文章: ${key} — 试试 ls 或 search` })
      return
    }
    pushHistory(cmd, 'post', { post })
    return
  }
  {
    const maybe = findPostBySlug(cmd) ?? findPostById(cmd)
    if (maybe) {
      pushHistory(cmd, 'post', { post: maybe })
      return
    }
  }
  pushHistory(cmd, 'error', { msg: `未知命令: ${cmd} — 输入 help 查看可用命令` })
}

// —— 芯片点击 / 输入框逻辑 ——
function runChip(cmd: string): void {
  runCommand(cmd)
}
function fillChip(cmd: string): void {
  inputRaw.value = cmd
  nextTick(() => inputEl.value?.focus())
}
function execInput(): void {
  const v = inputRaw.value.trim()
  if (!v) return
  runCommand(v)
  inputRaw.value = ''
}
function onEnter(): void {
  execInput()
}
function historyUp(): void {
  if (cmdHistory.value.length === 0) return
  histIdx = Math.max(0, histIdx - 1)
  if (histIdx >= 0 && histIdx < cmdHistory.value.length) inputRaw.value = cmdHistory.value[histIdx] ?? ''
}
function historyDown(): void {
  if (cmdHistory.value.length === 0) return
  histIdx = Math.min(cmdHistory.value.length, histIdx + 1)
  if (histIdx >= cmdHistory.value.length) inputRaw.value = ''
  else inputRaw.value = cmdHistory.value[histIdx] ?? ''
}

// —— 初始化：欢迎 + 自动 ls ——
onMounted(() => {
  pushHistory('motd', 'welcome', {})
  pushHistory('ls', 'ls', { posts: mockPosts })
})
</script>

<style scoped>
/* 磷光 CRT — 提纯：纯黑夜视感 · 字体仅 JetBrains Mono · 1px 磷光边框 · 0 0 18px 晕光 */
.mono, .display, .term-page, .term-page * {
  font-family: 'JetBrains Mono', ui-monospace, SFMono-Regular, Menlo, Consolas, monospace !important;
}

/* —— 页面 —— */
.term-page {
  min-height: 100vh;
  background: #050508;
  padding: 14px 2% 18px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.term-page.amber { --ph: #ffb000; --ph-dim: rgba(255,176,0,0.32); --ph-glow: rgba(255,176,0,0.18); --ph-mid: rgba(255,176,0,0.08); }
.term-page.green { --ph: #33ff66; --ph-dim: rgba(51,255,102,0.30); --ph-glow: rgba(51,255,102,0.16); --ph-mid: rgba(51,255,102,0.07); }

/* 顶部导航 */
.top-nav {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  flex-wrap: wrap;
}
.top-left, .top-right { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }
.hub-link,
.top-left a {
  background: transparent;
  color: var(--ph);
  padding: 6px 12px;
  font-weight: 800;
  font-size: 12px;
  letter-spacing: 0.06em;
  border: 1px solid var(--ph-dim);
  text-decoration: none;
  box-shadow: 0 0 10px var(--ph-glow);
  transition: background .15s, color .15s, box-shadow .15s;
}
.hub-link:hover,
.top-left a:hover { background: var(--ph); color: #050508; box-shadow: 0 0 18px var(--ph-glow); }
.top-title { font-size: 12px; font-weight: 800; letter-spacing: 0.08em; color: var(--ph); text-shadow: 0 0 8px var(--ph-glow); }
.top-sub { font-size: 10px; color: var(--ph); opacity: 0.55; letter-spacing: 0.04em; }
.mode-btn {
  background: transparent;
  color: var(--ph);
  padding: 5px 10px;
  font-size: 11px;
  font-weight: 800;
  border: 1px solid var(--ph-dim);
  cursor: pointer;
  opacity: 0.72;
  transition: background .14s, color .14s, box-shadow .14s, opacity .14s;
}
.mode-btn.active { background: var(--ph); color: #050508; opacity: 1; box-shadow: 0 0 14px var(--ph-glow); }
.mode-btn:hover { opacity: 1; box-shadow: 0 0 10px var(--ph-glow); }
.rec-dot { font-size: 11px; font-weight: 800; color: #ff3b3b; display: inline-flex; align-items: center; gap: 6px; text-shadow: 0 0 6px rgba(255,59,59,0.6); }
.rec-dot i { width: 8px; height: 8px; background: #ff3b3b; border-radius: 50%; display: inline-block; animation: recBlink 1s steps(1) infinite; box-shadow: 0 0 8px rgba(255,59,59,0.7); }
@keyframes recBlink { 50% { opacity: 0; } }

/* —— CRT 外壳：radial 深黑 + 1px 磷光边框 + 0 0 18px 晕光 —— */
.crt-shell {
  position: relative;
  background:
    radial-gradient(120% 120% at 50% 0%, rgba(255,255,255,0.045) 0%, transparent 45%),
    radial-gradient(160% 120% at 50% 100%, var(--ph-mid) 0%, transparent 55%),
    #050508;
  color: var(--ph);
  border: 1px solid var(--ph-dim);
  box-shadow: 0 0 18px var(--ph-glow), inset 0 0 60px rgba(0,0,0,0.85);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  min-height: 680px;
  flex: 1;
  isolation: isolate;
}
/* 旧硬阴影已移除，统一为 1px 磷光细边框 + 0 0 18px 晕光 */

/* 晕影 — 保留 */
.crt-vignette {
  position: absolute; inset: 0;
  background: radial-gradient(90% 70% at 50% 50%, transparent 60%, rgba(0,0,0,0.62) 100%);
  pointer-events: none; z-index: 2;
}
/* 扫描线 — 保留，磷光感 */
.scanlines {
  position: absolute; inset: 0;
  background: repeating-linear-gradient(
    0deg,
    transparent 0px,
    transparent 2px,
    rgba(255,255,255,0.06) 3px,
    transparent 3px
  );
  opacity: 0.20;
  pointer-events: none; z-index: 3;
}
.term-page.green .scanlines { opacity: 0.14; }
/* 噪点 — 保留 */
.noise {
  position: absolute; inset: 0;
  opacity: 0.06;
  pointer-events: none; z-index: 3;
  background-image:
    radial-gradient(rgba(255,255,255,0.75) 0.6px, transparent 0.7px),
    radial-gradient(rgba(255,255,255,0.45) 0.6px, transparent 0.7px);
  background-size: 3px 3px, 7px 7px;
  background-position: 0 0, 1px 1px;
}
/* 轻微闪烁 — 保留 */
.flicker {
  position: absolute; inset: 0;
  background: rgba(255,255,255,0.016);
  opacity: 0;
  pointer-events: none; z-index: 3;
  animation: flicker 6s linear infinite;
}
@keyframes flicker {
  0%, 96%, 100% { opacity: 0; }
  97% { opacity: 0.06; }
  98% { opacity: 0; }
  99% { opacity: 0.04; }
}

/* —— 标题栏 —— */
.term-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  padding: 9px 10px;
  background: rgba(255,255,255,0.02);
  border-bottom: 1px solid var(--ph-dim);
  flex-shrink: 0;
  position: relative; z-index: 4;
}
.traffic { display: flex; gap: 6px; align-items: center; }
.dot { width: 10px; height: 10px; border: 1px solid var(--ph-dim); border-radius: 50%; display: inline-block; opacity: 0.9; }
.dot.red { background: rgba(255,95,86,0.95); } .dot.yellow { background: rgba(255,189,46,0.95); } .dot.green { background: rgba(39,201,63,0.95); }
.term-title { flex: 1; text-align: center; display: flex; flex-direction: column; gap: 1px; align-items: center; }
.title-main { font-size: 11px; font-weight: 800; letter-spacing: 0.08em; color: var(--ph); text-shadow: 0 0 10px var(--ph-glow); }
.title-sub { font-size: 9px; color: var(--ph); opacity: 0.45; letter-spacing: 0.06em; }
.term-actions { display: flex; align-items: center; gap: 8px; font-size: 10px; font-weight: 800; color: var(--ph); opacity: 0.85; }
.mini-hub { background: transparent; color: var(--ph); padding: 4px 9px; font-size: 11px; font-weight: 800; border: 1px solid var(--ph-dim); text-decoration: none; transition: background .14s, color .14s, box-shadow .14s; }
.mini-hub:hover { background: var(--ph); color: #050508; box-shadow: 0 0 12px var(--ph-glow); }
.state-dot { color: var(--ph); text-shadow: 0 0 8px var(--ph-glow); }

/* —— 芯片条 —— */
.chip-bar {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 10px;
  background: rgba(255,255,255,0.016);
  border-bottom: 1px solid var(--ph-dim);
  overflow-x: auto;
  flex-shrink: 0;
  position: relative; z-index: 4;
}
.chip-bar::-webkit-scrollbar { height: 4px; }
.chip-bar::-webkit-scrollbar-thumb { background: var(--ph-dim); }
.chip-label { font-size: 10px; font-weight: 800; letter-spacing: 0.1em; white-space: nowrap; color: var(--ph); opacity: 0.9; text-shadow: 0 0 6px var(--ph-glow); }
.chip {
  background: rgba(255,255,255,0.04);
  color: var(--ph);
  padding: 6px 10px;
  font-size: 11px;
  font-weight: 800;
  border: 1px solid var(--ph-dim);
  cursor: pointer;
  white-space: nowrap;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  transition: background .14s, color .14s, box-shadow .14s, transform .08s;
  text-shadow: 0 0 6px var(--ph-glow);
}
.chip:hover { background: var(--ph); color: #050508; box-shadow: 0 0 14px var(--ph-glow); text-shadow: none; transform: translateY(-1px); }
.chip.ghost { border-style: dashed; opacity: 0.75; }
.chip-cmd { letter-spacing: 0.04em; }
.chip-desc { opacity: 0.65; font-weight: 600; }
.chip:hover .chip-desc { opacity: 0.9; }

/* —— 主布局 —— */
.term-layout {
  display: grid;
  grid-template-columns: 260px 1fr;
  flex: 1;
  min-height: 0;
  position: relative; z-index: 4;
}
.side-panel {
  background: rgba(255,255,255,0.015);
  border-right: 1px solid var(--ph-dim);
  padding: 10px 10px;
  overflow: auto;
  display: flex;
  flex-direction: column;
  gap: 14px;
}
.side-section { display: flex; flex-direction: column; gap: 8px; }
.side-head { display: flex; align-items: center; justify-content: space-between; gap: 8px; }
.side-title { font-size: 10px; font-weight: 800; letter-spacing: 0.12em; color: var(--ph); text-shadow: 0 0 8px var(--ph-glow); }
.side-action { background: transparent; color: var(--ph); padding: 3px 7px; font-size: 10px; font-weight: 800; border: 1px solid var(--ph-dim); cursor: pointer; transition: background .14s, color .14s; }
.side-action:hover { background: var(--ph); color: #050508; box-shadow: 0 0 10px var(--ph-glow); }
.side-list { display: flex; flex-direction: column; gap: 6px; }
.side-item {
  display: grid;
  grid-template-columns: 22px 1fr auto;
  grid-template-rows: auto auto;
  align-items: center;
  gap: 2px 8px;
  padding: 7px 8px;
  background: rgba(255,255,255,0.03);
  color: var(--ph);
  border: 1px solid var(--ph-dim);
  border-left: 1px solid var(--ph);
  cursor: pointer;
  text-align: left;
  width: 100%;
  transition: background .14s, box-shadow .14s, transform .08s;
}
.side-item:hover { background: var(--ph-mid); box-shadow: 0 0 12px var(--ph-glow); transform: translateY(-1px); }
.side-icon { font-size: 13px; grid-row: 1 / span 2; }
.side-name { font-size: 11px; font-weight: 800; color: var(--ph); }
.side-slug { font-size: 9px; opacity: 0.55; color: var(--ph); }
.side-count { grid-row: 1 / span 2; font-size: 10px; background: var(--ph); color: #050508; padding: 2px 6px; font-weight: 800; border: 1px solid var(--ph); }
.side-tags { display: flex; flex-wrap: wrap; gap: 6px; }
.tag-chip { font-size: 10px; padding: 4px 8px; font-weight: 800; border: 1px solid var(--ph-dim); cursor: pointer; transition: box-shadow .14s, filter .14s, transform .07s; }
.tag-chip:hover { filter: brightness(1.08); box-shadow: 0 0 10px var(--ph-glow); transform: translateY(-1px); }
.side-hint { font-size: 9px; color: var(--ph); opacity: 0.45; }
.user-item {
  display: flex; align-items: center; gap: 8px;
  padding: 6px 8px; background: rgba(255,255,255,0.03); color: var(--ph);
  border: 1px solid var(--ph-dim); cursor: pointer; text-align: left; width: 100%;
  transition: background .14s, box-shadow .14s;
}
.user-item:hover { background: var(--ph-mid); box-shadow: 0 0 12px var(--ph-glow); }
.user-avatar { width: 28px; height: 28px; display: flex; align-items: center; justify-content: center; font-size: 14px; border: 1px solid var(--ph-dim); flex-shrink: 0; }
.user-main { display: flex; flex-direction: column; gap: 1px; flex: 1; min-width: 0; }
.user-main b { font-size: 11px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; color: var(--ph); }
.user-main i { font-size: 9px; font-style: normal; opacity: 0.6; color: var(--ph); }
.user-go { font-size: 12px; opacity: 0.6; }
.side-foot { background: rgba(255,255,255,0.02); border: 1px dashed var(--ph-dim); padding: 8px; }
.foot-title { font-size: 10px; font-weight: 800; letter-spacing: 0.08em; color: var(--ph); }
.foot-desc { font-size: 10px; line-height: 1.5; color: var(--ph); opacity: 0.6; margin-top: 4px; }
.foot-actions { display: flex; gap: 6px; margin-top: 6px; flex-wrap: wrap; }
.foot-btn { background: rgba(255,255,255,0.04); color: var(--ph); padding: 4px 8px; font-size: 10px; font-weight: 800; border: 1px solid var(--ph-dim); cursor: pointer; transition: background .14s, color .14s; }
.foot-btn:hover { background: var(--ph); color: #050508; box-shadow: 0 0 10px var(--ph-glow); }

/* —— 主终端滚动区 —— */
.main-pane { background: rgba(255,255,255,0.01); display: flex; flex-direction: column; min-width: 0; min-height: 0; }
.history {
  flex: 1;
  overflow: auto;
  padding: 14px 12px;
  display: flex;
  flex-direction: column;
  gap: 14px;
  scroll-behavior: smooth;
}
.history::-webkit-scrollbar { width: 6px; height: 6px; }
.history::-webkit-scrollbar-thumb { background: var(--ph-dim); }
.entry { display: flex; flex-direction: column; gap: 6px; }
.prompt-line {
  display: flex; align-items: center; gap: 6px;
  font-size: 11px; font-weight: 800;
  color: var(--ph); text-shadow: 0 0 8px var(--ph-glow);
  flex-wrap: wrap;
}
.prompt-cmd { background: rgba(255,255,255,0.05); padding: 2px 6px; border: 1px solid var(--ph-dim); }
.typewriter { animation: typeIn .6s steps(24) both; overflow: hidden; }
@keyframes typeIn { from { clip-path: inset(0 100% 0 0); } to { clip-path: inset(0 0 0 0); } }
.prompt-time { margin-left: auto; font-size: 10px; opacity: 0.5; font-weight: 600; }

/* —— 通用卡片：纯黑夜视 · 1px 磷光边框 —— */
.card {
  background: rgba(12,12,14,0.96);
  color: var(--ph);
  border: 1px solid var(--ph-dim);
  box-shadow: 0 0 0 transparent;
  overflow: hidden;
}
.card-head {
  display: flex; align-items: center; justify-content: space-between; gap: 8px;
  padding: 8px 10px; background: rgba(255,255,255,0.03); border-bottom: 1px solid var(--ph-dim);
  font-size: 11px; font-weight: 800; flex-wrap: wrap; color: var(--ph);
}
.card-head-sub { font-weight: 600; color: var(--ph); opacity: 0.55; font-size: 10px; }

/* welcome */
.welcome-card { background: rgba(14,14,16,0.98); }
.ascii { font-size: 7px; line-height: 1.05; white-space: pre; overflow-x: auto; padding: 10px 10px 6px; color: var(--ph); opacity: 0.92; text-shadow: 0 0 6px var(--ph-glow); }
.welcome-grid { display: grid; grid-template-columns: 1fr 160px; gap: 12px; padding: 8px 12px 12px; }
.welcome-main h2 { font-size: 22px; line-height: 1; font-weight: 800; letter-spacing: -0.02em; color: var(--ph); text-shadow: 0 0 12px var(--ph-glow); }
.welcome-desc { font-size: 11px; line-height: 1.6; color: var(--ph); opacity: 0.78; margin-top: 6px; }
.welcome-desc b { color: var(--ph); opacity: 1; }
.welcome-actions { display: flex; gap: 8px; margin-top: 10px; flex-wrap: wrap; }
.w-btn { background: transparent; color: var(--ph); padding: 6px 10px; font-size: 11px; font-weight: 800; border: 1px solid var(--ph-dim); cursor: pointer; transition: background .14s, color .14s, box-shadow .14s; }
.w-btn:hover { background: var(--ph); color: #050508; box-shadow: 0 0 14px var(--ph-glow); }
.welcome-tips { display: flex; gap: 6px; align-items: center; flex-wrap: wrap; margin-top: 8px; font-size: 10px; color: var(--ph); opacity: 0.7; }
.tip-chip { background: rgba(255,255,255,0.04); color: var(--ph); padding: 3px 8px; font-size: 10px; font-weight: 800; border: 1px solid var(--ph-dim); cursor: pointer; transition: background .14s, color .14s; }
.tip-chip:hover { background: var(--ph); color: #050508; box-shadow: 0 0 10px var(--ph-glow); }
.welcome-side { display: flex; flex-direction: column; gap: 8px; }
.stat-mini { background: rgba(255,255,255,0.04); color: var(--ph); padding: 8px 8px; display: flex; justify-content: space-between; align-items: center; font-size: 10px; font-weight: 800; border: 1px solid var(--ph-dim); }
.stat-mini b { font-size: 14px; color: var(--ph); text-shadow: 0 0 6px var(--ph-glow); }
.scan-demo { background: rgba(255,255,255,0.03); color: var(--ph); padding: 8px; font-size: 9px; line-height: 1.5; border: 1px solid var(--ph-dim); text-shadow: 0 0 6px var(--ph-glow); }

/* help */
.help-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; padding: 10px; }
.help-row { display: grid; grid-template-columns: 140px 1fr auto; gap: 8px; align-items: center; padding: 8px 8px; background: rgba(255,255,255,0.03); border: 1px solid var(--ph-dim); cursor: pointer; text-align: left; width: 100%; transition: background .14s, box-shadow .14s; }
.help-row:hover { background: var(--ph-mid); box-shadow: 0 0 10px var(--ph-glow); }
.help-cmd { background: var(--ph); color: #050508; padding: 2px 6px; font-size: 10px; font-weight: 800; border: 1px solid var(--ph); }
.help-desc { font-size: 11px; color: var(--ph); opacity: 0.85; }
.help-go { font-size: 10px; font-weight: 800; color: var(--ph); }
.help-foot { padding: 8px 10px; border-top: 1px solid var(--ph-dim); background: rgba(255,255,255,0.02); font-size: 10px; color: var(--ph); opacity: 0.6; }

/* ls post grid */
.post-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 12px; padding: 12px; }
.post-card { background: rgba(18,18,20,0.98); border: 1px solid var(--ph-dim); overflow: hidden; display: flex; flex-direction: column; transition: box-shadow .14s; }
.post-card:hover { box-shadow: 0 0 14px var(--ph-glow); }
.post-cover { height: 150px; position: relative; overflow: hidden; border-bottom: 1px solid var(--ph-dim); background: #0a0a0c; }
.post-cover img { width: 100%; height: 100%; object-fit: cover; display: block; filter: saturate(0.9) contrast(1.05) brightness(0.92); opacity: 0.92; }
.post-group { position: absolute; left: 8px; bottom: 8px; padding: 3px 7px; font-size: 10px; font-weight: 800; border: 1px solid var(--ph-dim); }
.post-id { position: absolute; right: 8px; top: 8px; background: rgba(5,5,8,0.88); color: var(--ph); padding: 2px 6px; font-size: 9px; font-weight: 800; border: 1px solid var(--ph-dim); }
.post-body { padding: 10px 10px 10px; display: flex; flex-direction: column; gap: 8px; }
.post-title { font-size: 16px; line-height: 1.1; font-weight: 800; color: var(--ph); text-shadow: 0 0 8px var(--ph-glow); }
.post-intro { font-size: 11px; line-height: 1.6; color: var(--ph); opacity: 0.78; background: rgba(255,255,255,0.03); border-left: 1px solid var(--ph); padding: 6px 8px; }
.post-meta { display: flex; align-items: center; gap: 6px; font-size: 11px; flex-wrap: wrap; color: var(--ph); opacity: 0.78; }
.meta-avatar { width: 22px; height: 22px; display: inline-flex; align-items: center; justify-content: center; font-size: 12px; border: 1px solid var(--ph-dim); }
.meta-dot { opacity: 0.4; }
.post-tags { display: flex; gap: 6px; flex-wrap: wrap; }
.post-tag { font-size: 10px; padding: 2px 7px; font-weight: 800; border: 1px solid var(--ph-dim); cursor: pointer; transition: box-shadow .12s, filter .12s; }
.post-tag:hover { filter: brightness(1.06); box-shadow: 0 0 8px var(--ph-glow); }
.post-actions { display: flex; gap: 6px; align-items: center; flex-wrap: wrap; font-size: 11px; }
.act-btn { background: rgba(255,255,255,0.04); color: var(--ph); padding: 5px 9px; font-weight: 800; border: 1px solid var(--ph-dim); cursor: pointer; font-size: 11px; transition: background .14s, color .14s, box-shadow .14s; }
.act-btn:hover { background: var(--ph-mid); box-shadow: 0 0 8px var(--ph-glow); }
.act-btn.liked { background: var(--ph); color: #050508; border-color: var(--ph); box-shadow: 0 0 10px var(--ph-glow); }
.act-btn.primary { background: var(--ph); color: #050508; border-color: var(--ph); }
.act-btn.primary:hover { box-shadow: 0 0 14px var(--ph-glow); filter: brightness(1.04); }
.act-views { margin-left: auto; font-size: 10px; color: var(--ph); opacity: 0.55; }
.post-expand { background: rgba(255,255,255,0.02); padding: 8px; border: 1px solid var(--ph-dim); margin-top: 2px; }
.expand-head { display: flex; justify-content: space-between; align-items: center; font-size: 10px; font-weight: 800; margin-bottom: 6px; color: var(--ph); }
.expand-close { background: var(--ph); color: #050508; width: 20px; height: 20px; display: flex; align-items: center; justify-content: center; font-size: 12px; border: 1px solid var(--ph); cursor: pointer; }
.expand-content { white-space: pre-wrap; word-break: break-word; font-size: 11px; line-height: 1.7; background: rgba(5,5,8,0.9); color: var(--ph); padding: 10px 10px; border: 1px solid var(--ph-dim); max-height: 260px; overflow: auto; }
.expand-content::-webkit-scrollbar { width: 4px; }
.expand-content::-webkit-scrollbar-thumb { background: var(--ph-dim); }
.expand-foot { display: flex; gap: 6px; margin-top: 8px; flex-wrap: wrap; }

/* list/group/tag */
.list-card .card-head { background: rgba(255,255,255,0.03); color: var(--ph); border-color: var(--ph-dim); }
.group-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(180px,1fr)); gap: 10px; padding: 12px; }
.group-card { display: grid; grid-template-columns: 36px 1fr auto; grid-template-rows: auto auto; gap: 2px 8px; align-items: center; padding: 10px; background: rgba(255,255,255,0.03); border: 1px solid var(--ph-dim); cursor: pointer; text-align: left; color: var(--ph); transition: background .14s, box-shadow .14s; }
.group-card:hover { background: var(--ph-mid); box-shadow: 0 0 12px var(--ph-glow); }
.group-icon { font-size: 22px; grid-row: 1 / span 2; }
.group-name { font-size: 13px; font-weight: 800; color: var(--ph); }
.group-slug { font-size: 10px; color: var(--ph); opacity: 0.55; }
.group-count { grid-row: 1 / span 2; background: var(--ph); color: #050508; padding: 4px 7px; font-size: 11px; font-weight: 800; border: 1px solid var(--ph); }
.tag-cloud { display: flex; flex-wrap: wrap; gap: 8px; padding: 12px; }
.tag-cloud-item { padding: 6px 10px; font-weight: 800; border: 1px solid var(--ph-dim); cursor: pointer; transition: box-shadow .12s, transform .08s; }
.tag-cloud-item:hover { box-shadow: 0 0 10px var(--ph-glow); transform: translateY(-1px); }
.tag-cloud-item small { opacity: 0.75; font-weight: 600; margin-left: 4px; }
.user-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(180px,1fr)); gap: 10px; padding: 12px; }
.user-card { background: rgba(255,255,255,0.03); padding: 12px; border: 1px solid var(--ph-dim); cursor: pointer; text-align: left; display: flex; flex-direction: column; gap: 4px; color: var(--ph); transition: background .14s, box-shadow .14s; }
.user-card:hover { background: var(--ph-mid); box-shadow: 0 0 12px var(--ph-glow); }
.user-card-avatar { width: 36px; height: 36px; display: flex; align-items: center; justify-content: center; font-size: 18px; border: 1px solid var(--ph-dim); }
.user-card-name { font-size: 13px; font-weight: 800; color: var(--ph); }
.user-card-meta { font-size: 10px; color: var(--ph); opacity: 0.6; }
.user-card-bio { font-size: 11px; line-height: 1.4; color: var(--ph); opacity: 0.72; margin-top: 4px; }

/* detail */
.detail-card { background: rgba(12,12,14,0.98); }
.detail-head { display: flex; gap: 12px; align-items: center; padding: 12px; background: rgba(255,255,255,0.03); border-bottom: 1px solid var(--ph-dim); flex-wrap: wrap; }
.detail-icon { width: 44px; height: 44px; display: flex; align-items: center; justify-content: center; font-size: 22px; border: 1px solid var(--ph-dim); background: var(--ph); color: #050508; flex-shrink: 0; }
.detail-main h3 { font-size: 18px; font-weight: 800; color: var(--ph); text-shadow: 0 0 8px var(--ph-glow); }
.detail-main p { font-size: 11px; color: var(--ph); opacity: 0.6; }
.detail-action { background: transparent; color: var(--ph); padding: 6px 10px; font-size: 11px; font-weight: 800; border: 1px solid var(--ph-dim); cursor: pointer; margin-left: auto; transition: background .14s, color .14s; }
.detail-action:hover { background: var(--ph); color: #050508; box-shadow: 0 0 10px var(--ph-glow); }
.detail-sub { padding: 8px 12px 0; font-size: 11px; font-weight: 800; color: var(--ph); opacity: 0.75; }
.mini-card { display: flex; gap: 10px; padding: 8px; background: rgba(255,255,255,0.03); border: 1px solid var(--ph-dim); cursor: pointer; align-items: center; color: var(--ph); transition: background .14s, box-shadow .14s; }
.mini-card:hover { background: var(--ph-mid); box-shadow: 0 0 10px var(--ph-glow); }
.mini-card img { width: 72px; height: 56px; object-fit: cover; border: 1px solid var(--ph-dim); flex-shrink: 0; filter: saturate(0.9) brightness(0.9); }
.mini-info { display: flex; flex-direction: column; gap: 2px; flex: 1; min-width: 0; }
.mini-info b { font-size: 12px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; color: var(--ph); }
.mini-info span { font-size: 10px; color: var(--ph); opacity: 0.62; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.mini-meta { opacity: 0.55 !important; }
.mini-go { font-size: 11px; font-weight: 800; white-space: nowrap; color: var(--ph); }
.empty { padding: 18px; text-align: center; font-size: 11px; color: var(--ph); opacity: 0.6; }
.inline-chip { background: rgba(255,255,255,0.04); color: var(--ph); padding: 2px 6px; font-size: 10px; font-weight: 800; border: 1px solid var(--ph-dim); cursor: pointer; margin: 0 3px; transition: background .12s, color .12s; }
.inline-chip:hover { background: var(--ph); color: #050508; }

/* search */
.search-card .card-head { background: rgba(255,255,255,0.03); color: var(--ph); }

/* post detail 分屏 */
.post-detail-layout { display: grid; grid-template-columns: 1fr 1.2fr; gap: 12px; padding: 12px; }
.post-detail-cover { height: 320px; position: relative; overflow: hidden; border: 1px solid var(--ph-dim); background: #0a0a0c; }
.post-detail-cover img { width: 100%; height: 100%; object-fit: cover; display: block; filter: saturate(0.92) brightness(0.9); }
.cover-meta { position: absolute; left: 8px; bottom: 8px; display: flex; gap: 6px; align-items: center; }
.cover-tag { padding: 4px 8px; font-size: 10px; font-weight: 800; border: 1px solid var(--ph-dim); }
.cover-id { background: rgba(5,5,8,0.88); color: var(--ph); padding: 3px 6px; font-size: 10px; font-weight: 800; border: 1px solid var(--ph-dim); }
.post-detail-info { display: flex; flex-direction: column; gap: 8px; }
.post-detail-intro { font-size: 12px; line-height: 1.6; background: rgba(255,255,255,0.03); border-left: 1px solid var(--ph); padding: 8px 10px; color: var(--ph); opacity: 0.82; }
.detail-author { display: flex; gap: 8px; align-items: center; padding: 7px 8px; background: rgba(255,255,255,0.03); border: 1px solid var(--ph-dim); font-size: 11px; font-weight: 700; flex-wrap: wrap; color: var(--ph); }
.author-av { width: 26px; height: 26px; display: inline-flex; align-items: center; justify-content: center; font-size: 14px; border: 1px solid var(--ph-dim); }
.detail-views { margin-left: auto; color: var(--ph); opacity: 0.55; font-weight: 600; }
.post-detail-content { white-space: pre-wrap; word-break: break-word; font-size: 11px; line-height: 1.75; background: rgba(5,5,8,0.92); color: var(--ph); padding: 12px 10px; border: 1px solid var(--ph-dim); max-height: 280px; overflow: auto; }
.post-detail-content::-webkit-scrollbar { width: 4px; }
.post-detail-content::-webkit-scrollbar-thumb { background: var(--ph-dim); }

/* stats */
.stats-grid { display: grid; grid-template-columns: repeat(3,1fr); gap: 10px; padding: 12px; }
.stat-big { background: rgba(255,255,255,0.03); color: var(--ph); padding: 14px 12px; display: flex; flex-direction: column; gap: 4px; border: 1px solid var(--ph-dim); }
.stat-big span { font-size: 10px; letter-spacing: 0.1em; opacity: 0.5; }
.stat-big b { font-size: 26px; line-height: 1; color: var(--ph); text-shadow: 0 0 10px var(--ph-glow); }
.stat-big i { font-size: 10px; opacity: 0.45; font-style: normal; }
.stats-foot { padding: 8px 12px; border-top: 1px solid var(--ph-dim); background: rgba(255,255,255,0.02); font-size: 10px; color: var(--ph); opacity: 0.55; }

/* whoami */
.whoami-body { display: flex; gap: 14px; padding: 14px 14px; align-items: center; }
.who-avatar { width: 64px; height: 64px; display: flex; align-items: center; justify-content: center; font-size: 28px; border: 1px solid var(--ph-dim); flex-shrink: 0; }
.who-main h3 { font-size: 18px; font-weight: 800; color: var(--ph); text-shadow: 0 0 8px var(--ph-glow); }
.who-main p { font-size: 11px; color: var(--ph); opacity: 0.72; margin-top: 4px; line-height: 1.5; }
.who-actions { display: flex; gap: 8px; margin-top: 8px; flex-wrap: wrap; }
.who-foot { padding: 8px 12px; background: rgba(255,255,255,0.02); border-top: 1px solid var(--ph-dim); font-size: 10px; color: var(--ph); opacity: 0.55; }

/* error */
.error-card { background: rgba(40,10,10,0.92); border-color: rgba(255,59,59,0.42); box-shadow: 0 0 14px rgba(255,59,59,0.12); }
.error-title { padding: 12px 12px 4px; font-size: 12px; font-weight: 800; color: #ff5f56; text-shadow: 0 0 8px rgba(255,59,59,0.4); }
.error-hint { padding: 0 12px 12px; font-size: 11px; color: var(--ph); opacity: 0.85; }

.empty-history { text-align: center; padding: 20px; font-size: 11px; color: var(--ph); opacity: 0.6; display: flex; gap: 8px; align-items: center; justify-content: center; flex-wrap: wrap; }
.empty-history code { background: rgba(255,255,255,0.05); padding: 2px 6px; border: 1px solid var(--ph-dim); color: var(--ph); }

/* —— 底部输入行 —— */
.input-bar {
  border-top: 1px solid var(--ph-dim);
  background: rgba(255,255,255,0.015);
  padding: 10px 10px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  flex-shrink: 0;
  position: relative; z-index: 4;
}
.input-row { display: flex; gap: 8px; align-items: center; flex-wrap: wrap; }
.prompt-label { font-size: 11px; font-weight: 800; color: var(--ph); text-shadow: 0 0 8px var(--ph-glow); white-space: nowrap; }
.input-wrap {
  flex: 1;
  min-width: 220px;
  display: flex;
  align-items: center;
  gap: 4px;
  background: rgba(0,0,0,0.55);
  padding: 6px 8px;
  border: 1px solid var(--ph-dim);
  position: relative;
  box-shadow: inset 0 0 12px rgba(0,0,0,0.6);
}
.term-input {
  flex: 1;
  background: transparent;
  border: none;
  outline: none;
  color: var(--ph);
  font-size: 12px;
  font-weight: 700;
  caret-color: var(--ph);
  text-shadow: 0 0 6px var(--ph-glow);
}
.term-input::placeholder { color: var(--ph); opacity: 0.32; font-weight: 600; }
.cursor {
  color: var(--ph);
  font-size: 14px;
  animation: cursorBlink 1s steps(1) infinite;
  text-shadow: 0 0 8px var(--ph-glow);
  margin-left: -2px;
}
@keyframes cursorBlink { 50% { opacity: 0; } }
.exec-btn {
  background: var(--ph);
  color: #050508;
  padding: 7px 14px;
  font-size: 11px;
  font-weight: 800;
  border: 1px solid var(--ph);
  cursor: pointer;
  white-space: nowrap;
  box-shadow: 0 0 12px var(--ph-glow);
  transition: filter .14s, box-shadow .14s, transform .08s;
}
.exec-btn:hover { filter: brightness(1.06); box-shadow: 0 0 18px var(--ph-glow); transform: translateY(-1px); }
.clear-btn { background: transparent; color: var(--ph); opacity: 0.7; padding: 6px 10px; font-size: 11px; font-weight: 700; border: 1px solid var(--ph-dim); cursor: pointer; transition: background .14s, color .14s; }
.clear-btn:hover { background: var(--ph-mid); opacity: 1; }
.quick-chips { display: flex; gap: 6px; flex-wrap: wrap; align-items: center; }
.quick-label { font-size: 10px; font-weight: 800; letter-spacing: 0.08em; color: var(--ph); opacity: 0.7; white-space: nowrap; }
.quick-chip { background: rgba(255,255,255,0.04); color: var(--ph); padding: 4px 8px; font-size: 10px; font-weight: 700; border: 1px solid var(--ph-dim); cursor: pointer; transition: background .14s, color .14s, box-shadow .14s; }
.quick-chip:hover { background: var(--ph); color: #050508; border-color: var(--ph); box-shadow: 0 0 10px var(--ph-glow); }
.quick-chip.ghost { border-style: dashed; opacity: 0.6; }
.input-hint { font-size: 9px; color: var(--ph); opacity: 0.38; letter-spacing: 0.04em; }

.page-foot { display: flex; justify-content: space-between; gap: 12px; font-size: 10px; letter-spacing: 0.06em; color: var(--ph); opacity: 0.42; flex-wrap: wrap; }

/* —— 响应式 —— */
@media (max-width: 960px) {
  .term-layout { grid-template-columns: 1fr; }
  .side-panel { border-right: none; border-bottom: 1px solid var(--ph-dim); max-height: 300px; flex-direction: row; overflow-x: auto; overflow-y: hidden; gap: 12px; }
  .side-section { min-width: 220px; flex-shrink: 0; }
  .welcome-grid { grid-template-columns: 1fr; }
  .post-detail-layout { grid-template-columns: 1fr; }
  .post-detail-cover { height: 200px; }
  .help-grid { grid-template-columns: 1fr; }
  .stats-grid { grid-template-columns: repeat(2,1fr); }
  .hide-mobile { display: none !important; }
}
@media (max-width: 560px) {
  .crt-shell { min-height: 620px; }
  .post-grid { grid-template-columns: 1fr; }
  .group-grid, .user-grid { grid-template-columns: 1fr; }
  .input-wrap { min-width: 0; }
}
</style>
