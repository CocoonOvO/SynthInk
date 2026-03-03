# SynthInk 主题系统设计文档

> 概念句：凌晨两点，耳机里循环的片尾曲，窗外雨丝反射街灯
> 
> 宅度等级：浓宅（6个灵动点）

---

## ⚠️ 问题整理（以demo16为准，对比home）

### 一、主题缺失（home少了4个主题）

| 主题ID | 主题名称 | 粒子类型 | 状态 |
|--------|----------|----------|------|
| `bamboo` | 竹林绿 | firefly | ❌ 缺失 |
| `mint-choco` | 薄荷巧克力 | creamy | ❌ 缺失 |
| `strawberry-cream` | 草莓奶油 | bubble | ❌ 缺失 |
| `orange-soda` | 香橙气泡 | rising | ❌ 缺失 |
| `mygo-light` | 星歌 | musical | ❌ 缺失 |
| `bangdream-dark` | 夜奏 | spotlight | ❌ 缺失 |

### 二、同名主题但样式完全不同

#### 2.1 cyber / cyberpunk
| 变量 | demo16 (cyber) | home (cyberpunk) | 状态 |
|------|---------------|------------------|------|
| --bg-primary | #0a0a0f | #0a0a12 | ⚠️ 不同 |
| --bg-secondary | #12121a | #120a1a | ⚠️ 不同 |
| --accent-primary | #00f5d4 (青) | #ff00ff (紫) | ❌ 完全不同 |
| --accent-secondary | #ff006e (粉) | #00ffff (青) | ❌ 完全不同 |
| --particle-type | matrix | matrix | ✅ 一致 |
| --particle-color | #00f5d4 | #ff00ff | ❌ 不同 |

**结论**：home的cyberpunk颜色完全错误，应该是青+粉，不是紫+青。

#### 2.2 exia（最严重）
| 变量 | demo16 (exia) | home (exia) | 状态 |
|------|---------------|-------------|------|
| --bg-primary | #fafafa (白) | #0a0f0a (黑绿) | ❌ 完全相反 |
| --text-primary | #0a0a0a (黑) | #e8f0e8 (白) | ❌ 完全相反 |
| --accent-primary | #1a1a1a (黑) | #00c853 (绿) | ❌ 完全不同 |
| --accent-secondary | #4a4a4a (灰) | #69f0ae (亮绿) | ❌ 完全不同 |
| --particle-type | wireframe | wireframe | ✅ 一致 |
| --card-radius | 2px | (未设置) | ⚠️ 缺失 |
| --button-radius | 0px | (未设置) | ⚠️ 缺失 |

**结论**：home的exia是暗绿风格，demo16是白底黑线极简风格。完全不是同一个主题概念。

#### 2.3 sakura-white / sakura
| 变量 | demo16 (sakura-white) | home (sakura) | 状态 |
|------|----------------------|---------------|------|
| --bg-primary | #ffffff (白) | #1a1218 (暗粉) | ❌ 完全相反 |
| --text-primary | #1a1a1a (黑) | #f5e8f0 (白) | ❌ 完全相反 |
| --accent-primary | #ff69b4 (粉) | #ffb7c5 (浅粉) | ⚠️ 不同 |
| --particle-type | sakura | sakura | ✅ 一致 |

**结论**：home的sakura是暗色主题，demo16是白色主题。

### 三、粒子类型缺失（home的粒子系统）

| 粒子类型 | demo16 | home | 状态 |
|----------|--------|------|------|
| `matrix` | ✅ | ✅ | cyber/cyberpunk |
| `firefly` | ✅ | ✅ | bamboo/forest |
| `sakura` | ✅ | ✅ | sakura-white/sakura |
| `creamy` | ✅ | ❌ | mint-choco |
| `bubble` | ✅ | ✅ | strawberry-cream/ocean |
| `rising` | ✅ | ✅ | orange-soda/midnight |
| `musical` | ✅ | ❌ | mygo-light |
| `spotlight` | ✅ | ❌ | bangdream-dark |
| `wireframe` | ✅ | ✅ | exia |
| `datastream` | ✅ | ✅ | veda |
| `twinparticle` | ✅ | ✅ | raiser/twins |

**缺失的粒子类型**：`creamy`, `musical`, `spotlight`

### 四、CSS变量差异

#### 4.1 demo16有但home没有
| 变量 | 用途 |
|------|------|
| `--bg-tertiary` | 第三层背景 |
| `--text-muted` | 更弱的文字色 |
| `--shadow-color` | 阴影颜色 |
| `--particle-glow` | 粒子发光效果 |
| `--card-backdrop` | 卡片背景模糊 |
| `--font-heading` | 标题字体 |
| `--font-body` | 正文字体 |
| `--font-mono` | 等宽字体 |
| `--transition-smooth` | 平滑过渡 |
| `--transition-bounce` | 弹性过渡 |
| `--transition-fast` | 快速过渡 |

#### 4.2 home有但demo16没有
| 变量 | 用途 |
|------|------|
| `--glow-strong` | 强光晕 |
| `--scanline-opacity` | 扫描线透明度 |
| `--grid-opacity` | 网格透明度 |
| `--noise-opacity` | 噪点透明度 |
| `--font-display` | 展示字体 |

### 五、粒子行为差异

#### 5.1 gnbeam（demo16有，home没有）
- demo16: 向上飘动
- home: ❌ 未实现

#### 5.2 wireframe
- demo16: 水平向右移动，分散在屏幕各处
- home: 水平向右移动，分散在屏幕各处
- **状态**：✅ 一致

#### 5.3 datastream
- demo16: 垂直下落，有length参数
- home: 垂直下落，有length参数
- **状态**：✅ 一致

---

## 🎨 正确主题定义（以demo16为准，共11个主题）

### 基础变量规范

```css
/* 背景 */
--bg-primary:     /* 页面背景 */
--bg-secondary:   /* 卡片背景 */
--bg-tertiary:    /* 第三层背景 */
--bg-elevated:    /* 高亮背景 */
--bg-card:        /* 卡片背景（带透明度） */

/* 文字 */
--text-primary:   /* 主文字 */
--text-secondary: /* 次文字 */
--text-tertiary:  /* 辅助文字 */
--text-muted:     /* 弱化文字 */

/* 强调色 */
--accent-primary:   /* 主强调色 */
--accent-secondary: /* 次强调色 */
--accent-tertiary:  /* 第三强调色 */
--accent-gradient:  /* 渐变定义 */

/* 效果 */
--glow-primary:   /* 主光晕 */
--glow-secondary: /* 次光晕 */
--border-subtle:  /*  subtle边框 */
--border-glow:    /* 发光边框 */
--shadow-color:   /* 阴影色 */

/* 状态色 */
--success: /* 成功 */
--warning: /* 警告 */
--error:   /* 错误 */
--info:    /* 信息 */

/* 粒子 */
--particle-color:   /* 粒子颜色 */
--particle-opacity: /* 粒子透明度 */
--particle-glow:    /* 粒子发光 */
--particle-type:    /* 粒子类型 */

/* 组件 */
--card-backdrop:  /* 卡片背景模糊 */
--card-radius:    /* 卡片圆角 */
--button-radius:  /* 按钮圆角 */

/* 字体 */
--font-heading: /* 标题字体 */
--font-body:    /* 正文字体 */
--font-mono:    /* 等宽字体 */

/* 过渡 */
--transition-smooth: /* 平滑过渡 */
--transition-bounce: /* 弹性过渡 */
--transition-fast:   /* 快速过渡 */
```

---

### 主题1：赛博霓虹 (cyber)
**概念**：深夜代码编辑器，光标在黑暗中呼吸

```css
[data-theme="cyber"] {
    --bg-primary: #0a0a0f;
    --bg-secondary: #12121a;
    --bg-tertiary: #1a1a25;
    --bg-elevated: #252535;
    --bg-card: rgba(18, 18, 26, 0.8);
    
    --text-primary: #e8e8f0;
    --text-secondary: #9090a0;
    --text-tertiary: #606070;
    --text-muted: #505060;
    
    --accent-primary: #00f5d4;
    --accent-secondary: #ff006e;
    --accent-tertiary: #00bbf9;
    --accent-gradient: linear-gradient(135deg, #00f5d4 0%, #ff006e 100%);
    
    --glow-primary: rgba(0, 245, 212, 0.4);
    --glow-secondary: rgba(255, 0, 110, 0.4);
    --border-subtle: rgba(255, 255, 255, 0.06);
    --border-glow: rgba(0, 245, 212, 0.2);
    --shadow-color: rgba(0, 0, 0, 0.5);
    
    --success: #00f5d4;
    --warning: #fbbf24;
    --error: #ff006e;
    --info: #00bbf9;
    
    --particle-color: #00f5d4;
    --particle-opacity: 0.5;
    --particle-glow: 0 0 6px #00f5d4;
    --particle-type: matrix;
    
    --card-backdrop: blur(20px);
    --card-radius: 16px;
    --button-radius: 8px;
    
    --font-heading: 'Inter', sans-serif;
    --font-body: 'Inter', sans-serif;
    --font-mono: 'JetBrains Mono', monospace;
    
    --transition-smooth: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    --transition-bounce: all 0.5s cubic-bezier(0.68, -0.55, 0.265, 1.55);
    --transition-fast: all 0.2s ease-out;
}
```

**灵动点**：
- 粒子：matrix代码雨效果
- 光晕：青色发光边框
- 渐变：青粉渐变强调色

---

### 主题2：竹林绿 (bamboo)
**概念**：雨后竹林，清新自然

```css
[data-theme="bamboo"] {
    --bg-primary: #f0f4f0;
    --bg-secondary: rgba(224, 235, 224, 0.7);
    --bg-tertiary: rgba(200, 220, 200, 0.5);
    --bg-elevated: rgba(255, 255, 255, 0.8);
    --bg-card: rgba(224, 235, 224, 0.6);
    
    --text-primary: #1a2e1a;
    --text-secondary: #4a6b4a;
    --text-tertiary: #7a9a7a;
    --text-muted: #9ab89a;
    
    --accent-primary: #2d6a4f;
    --accent-secondary: #52b788;
    --accent-tertiary: #40916c;
    --accent-gradient: linear-gradient(135deg, #2d6a4f 0%, #52b788 100%);
    
    --glow-primary: rgba(45, 106, 79, 0.3);
    --glow-secondary: rgba(82, 183, 136, 0.3);
    --border-subtle: rgba(45, 106, 79, 0.15);
    --border-glow: rgba(82, 183, 136, 0.25);
    --shadow-color: rgba(26, 46, 26, 0.06);
    
    --success: #2d6a4f;
    --warning: #d4a373;
    --error: #e63946;
    --info: #457b9d;
    
    --particle-color: #52b788;
    --particle-opacity: 0.4;
    --particle-glow: 0 0 6px #52b788;
    --particle-type: firefly;
    
    --card-backdrop: blur(12px);
    --card-radius: 16px;
    --button-radius: 8px;
    
    --font-heading: 'Inter', sans-serif;
    --font-body: 'Inter', sans-serif;
    --font-mono: 'JetBrains Mono', monospace;
    
    --transition-smooth: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    --transition-bounce: all 0.5s cubic-bezier(0.68, -0.55, 0.265, 1.55);
    --transition-fast: all 0.2s ease-out;
}
```

**灵动点**：
- 粒子：萤火虫闪烁效果
- 玻璃拟态：半透明模糊卡片
- 清新感：绿色自然配色

---

### 主题3：纯白樱 (sakura-white)
**概念**：樱花飘落的纯净世界

```css
[data-theme="sakura-white"] {
    --bg-primary: #ffffff;
    --bg-secondary: rgba(250, 250, 250, 0.9);
    --bg-tertiary: rgba(240, 240, 240, 0.8);
    --bg-elevated: rgba(255, 255, 255, 0.95);
    --bg-card: rgba(255, 255, 255, 0.7);
    
    --text-primary: #1a1a1a;
    --text-secondary: #666666;
    --text-tertiary: #999999;
    --text-muted: #bbbbbb;
    
    --accent-primary: #ff69b4;
    --accent-secondary: #ffb6c1;
    --accent-tertiary: #ffc8dd;
    --accent-gradient: linear-gradient(135deg, #ff1493 0%, #ff69b4 50%, #ffb6c1 100%);
    
    --glow-primary: rgba(255, 105, 180, 0.4);
    --glow-secondary: rgba(255, 182, 193, 0.3);
    --border-subtle: rgba(255, 105, 180, 0.15);
    --border-glow: rgba(255, 182, 193, 0.35);
    --shadow-color: rgba(255, 105, 180, 0.08);
    
    --success: #00c853;
    --warning: #ffd600;
    --error: #ff1744;
    --info: #2979ff;
    
    --particle-color: #ffb6c1;
    --particle-opacity: 0.6;
    --particle-glow: 0 0 6px #ffb6c1;
    --particle-type: sakura;
    
    --card-backdrop: blur(12px);
    --card-radius: 16px;
    --button-radius: 8px;
    
    --font-heading: 'Inter', sans-serif;
    --font-body: 'Inter', sans-serif;
    --font-mono: 'JetBrains Mono', monospace;
    
    --transition-smooth: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    --transition-bounce: all 0.5s cubic-bezier(0.68, -0.55, 0.265, 1.55);
    --transition-fast: all 0.2s ease-out;
}
```

**灵动点**：
- 粒子：樱花瓣旋转飘落
- 玻璃拟态：粉色边框模糊卡片
- 纯净感：白色背景+粉色强调

---

### 主题4：薄荷巧克力 (mint-choco)
**概念**：甜点时光，奶油质感

```css
[data-theme="mint-choco"] {
    --bg-primary: #2d1f1a;
    --bg-secondary: rgba(61, 42, 34, 0.95);
    --bg-tertiary: rgba(77, 53, 43, 0.9);
    --bg-elevated: rgba(93, 64, 55, 0.95);
    --bg-card: rgba(61, 42, 34, 0.8);
    
    --text-primary: #f5f5f5;
    --text-secondary: #d4c4b0;
    --text-tertiary: #a89080;
    --text-muted: #8a7060;
    
    --accent-primary: #98ff98;
    --accent-secondary: #50c878;
    --accent-tertiary: #2e8b57;
    --accent-gradient: linear-gradient(135deg, #98ff98 0%, #50c878 50%, #2e8b57 100%);
    
    --glow-primary: rgba(152, 255, 152, 0.5);
    --glow-secondary: rgba(80, 200, 120, 0.4);
    --border-subtle: rgba(152, 255, 152, 0.15);
    --border-glow: rgba(152, 255, 152, 0.25);
    --shadow-color: rgba(152, 255, 152, 0.12);
    
    --success: #90ee90;
    --warning: #ffd700;
    --error: #ff6b6b;
    --info: #87ceeb;
    
    --particle-color: #98ff98;
    --particle-opacity: 0.6;
    --particle-glow: 0 0 6px #98ff98;
    --particle-type: creamy;
    
    --card-backdrop: blur(16px);
    --card-radius: 24px;
    --button-radius: 50px;
    
    --font-heading: 'Inter', sans-serif;
    --font-body: 'Inter', sans-serif;
    --font-mono: 'JetBrains Mono', monospace;
    
    --transition-smooth: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    --transition-bounce: all 0.5s cubic-bezier(0.68, -0.55, 0.265, 1.55);
    --transition-fast: all 0.2s ease-out;
}
```

**灵动点**：
- 粒子：奶油融化效果（极缓慢移动）
- 大圆角：24px卡片+50px按钮
- 甜点感：巧克力色+薄荷绿

---

### 主题5：草莓奶油 (strawberry-cream)
**概念**：玻璃泡泡，甜美梦幻

```css
[data-theme="strawberry-cream"] {
    --bg-primary: #fff8f8;
    --bg-secondary: rgba(255, 240, 240, 0.85);
    --bg-tertiary: rgba(255, 232, 232, 0.7);
    --bg-elevated: rgba(255, 255, 255, 0.9);
    --bg-card: rgba(255, 240, 240, 0.7);
    
    --text-primary: #4a1a2a;
    --text-secondary: #8a4a5a;
    --text-tertiary: #ba8a9a;
    --text-muted: #dababa;
    
    --accent-primary: #ff6b8a;
    --accent-secondary: #ffb8c9;
    --accent-tertiary: #ffd1dc;
    --accent-gradient: linear-gradient(135deg, #ff1744 0%, #ff6b8a 50%, #ffb8c9 100%);
    
    --glow-primary: rgba(255, 107, 138, 0.4);
    --glow-secondary: rgba(255, 184, 201, 0.3);
    --border-subtle: rgba(255, 107, 138, 0.15);
    --border-glow: rgba(255, 184, 201, 0.35);
    --shadow-color: rgba(255, 107, 138, 0.08);
    
    --success: #4ade80;
    --warning: #fbbf24;
    --error: #ff1744;
    --info: #60a5fa;
    
    --particle-color: #ffb8c9;
    --particle-opacity: 0.5;
    --particle-glow: 0 0 6px #ffb8c9;
    --particle-type: bubble;
    
    --card-backdrop: blur(16px);
    --card-radius: 20px;
    --button-radius: 50px;
    
    --font-heading: 'Inter', sans-serif;
    --font-body: 'Inter', sans-serif;
    --font-mono: 'JetBrains Mono', monospace;
    
    --transition-smooth: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    --transition-bounce: all 0.5s cubic-bezier(0.68, -0.55, 0.265, 1.55);
    --transition-fast: all 0.2s ease-out;
}
```

**灵动点**：
- 粒子：泡泡上升+反光效果
- 玻璃拟态：强模糊+粉色边框
- 甜美感：粉白配色+大圆角

---

### 主题6：香橙气泡 (orange-soda)
**概念**：柑橘清爽，气泡上升

```css
[data-theme="orange-soda"] {
    --bg-primary: #fffaf5;
    --bg-secondary: rgba(255, 245, 235, 0.9);
    --bg-tertiary: rgba(255, 232, 214, 0.75);
    --bg-elevated: rgba(255, 255, 255, 0.95);
    --bg-card: rgba(255, 245, 235, 0.8);
    
    --text-primary: #2d1f1a;
    --text-secondary: #6b5a4a;
    --text-tertiary: #a09080;
    --text-muted: #c0b0a0;
    
    --accent-primary: #ff8c42;
    --accent-secondary: #ffb366;
    --accent-tertiary: #ffd699;
    --accent-gradient: linear-gradient(135deg, #ff6b35 0%, #ff8c42 50%, #ffb366 100%);
    
    --glow-primary: rgba(255, 140, 66, 0.4);
    --glow-secondary: rgba(255, 179, 102, 0.3);
    --border-subtle: rgba(255, 140, 66, 0.15);
    --border-glow: rgba(255, 179, 102, 0.3);
    --shadow-color: rgba(255, 140, 66, 0.08);
    
    --success: #22c55e;
    --warning: #f59e0b;
    --error: #ef4444;
    --info: #3b82f6;
    
    --particle-color: #ffb366;
    --particle-opacity: 0.5;
    --particle-glow: 0 0 6px #ffb366;
    --particle-type: rising;
    
    --card-backdrop: blur(12px);
    --card-radius: 18px;
    --button-radius: 50px;
    
    --font-heading: 'Inter', sans-serif;
    --font-body: 'Inter', sans-serif;
    --font-mono: 'JetBrains Mono', monospace;
    
    --transition-smooth: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    --transition-bounce: all 0.5s cubic-bezier(0.68, -0.55, 0.265, 1.55);
    --transition-fast: all 0.2s ease-out;
}
```

**灵动点**：
- 粒子：气泡快速上升+合并效果
- 清爽感：橙白配色
- 玻璃拟态：中等模糊+白色边框

---

### 主题7：星歌 (mygo-light)
**概念**：MyGO!!!!! 灯宝的诗与呐喊，粉蓝交织的迷途之星

```css
[data-theme="mygo-light"] {
    --bg-primary: #f8f9ff;
    --bg-secondary: rgba(238, 240, 255, 0.9);
    --bg-tertiary: rgba(230, 233, 255, 0.8);
    --bg-elevated: rgba(255, 255, 255, 0.95);
    --bg-card: rgba(238, 240, 255, 0.8);
    
    --text-primary: #1a1a3a;
    --text-secondary: #4a4a7a;
    --text-tertiary: #8a8aba;
    --text-muted: #aaaacc;
    
    --accent-primary: #6b8cff;
    --accent-secondary: #ff8ad8;
    --accent-tertiary: #a78bfa;
    --accent-gradient: linear-gradient(135deg, #6b8cff 0%, #a78bfa 50%, #ff8ad8 100%);
    
    --glow-primary: rgba(107, 140, 255, 0.4);
    --glow-secondary: rgba(255, 138, 216, 0.3);
    --border-subtle: rgba(167, 139, 250, 0.15);
    --border-glow: rgba(167, 139, 250, 0.3);
    --shadow-color: rgba(107, 140, 255, 0.08);
    
    --success: #4ade80;
    --warning: #fbbf24;
    --error: #f472b6;
    --info: #60a5fa;
    
    --particle-color: #a78bfa;
    --particle-opacity: 0.5;
    --particle-glow: 0 0 6px #a78bfa;
    --particle-type: musical;
    
    --card-backdrop: blur(12px);
    --card-radius: 16px;
    --button-radius: 12px;
    
    --font-heading: 'Inter', sans-serif;
    --font-body: 'Inter', sans-serif;
    --font-mono: 'JetBrains Mono', monospace;
    
    --transition-smooth: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    --transition-bounce: all 0.5s cubic-bezier(0.68, -0.55, 0.265, 1.55);
    --transition-fast: all 0.2s ease-out;
}
```

**灵动点**：
- 粒子：音符跳动+波形效果
- 少女乐队：粉蓝渐变强调色
- 玻璃拟态：淡紫边框模糊卡片

---

### 主题8：夜奏 (bangdream-dark)
**概念**：BanG Dream! 夜晚的Live House，聚光灯与应援棒的海洋

```css
[data-theme="bangdream-dark"] {
    --bg-primary: #0d0d1f;
    --bg-secondary: rgba(21, 21, 45, 0.95);
    --bg-tertiary: rgba(34, 34, 68, 0.9);
    --bg-elevated: rgba(45, 45, 92, 0.95);
    --bg-card: rgba(21, 21, 45, 0.8);
    
    --text-primary: #f0f0ff;
    --text-secondary: #b0b0e0;
    --text-tertiary: #7070a0;
    --text-muted: #505080;
    
    --accent-primary: #ff5e9a;
    --accent-secondary: #00d9ff;
    --accent-tertiary: #c084fc;
    --accent-gradient: linear-gradient(135deg, #ff5e9a 0%, #c084fc 50%, #00d9ff 100%);
    
    --glow-primary: rgba(255, 94, 154, 0.6);
    --glow-secondary: rgba(0, 217, 255, 0.5);
    --border-subtle: rgba(255, 94, 154, 0.2);
    --border-glow: rgba(255, 94, 154, 0.4);
    --shadow-color: rgba(255, 94, 154, 0.2);
    
    --success: #4ade80;
    --warning: #fbbf24;
    --error: #ff5e9a;
    --info: #00d9ff;
    
    --particle-color: #ff5e9a;
    --particle-opacity: 0.7;
    --particle-glow: 0 0 6px #ff5e9a;
    --particle-type: spotlight;
    
    --card-backdrop: blur(12px);
    --card-radius: 12px;
    --button-radius: 8px;
    
    --font-heading: 'Inter', sans-serif;
    --font-body: 'Inter', sans-serif;
    --font-mono: 'JetBrains Mono', monospace;
    
    --transition-smooth: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    --transition-bounce: all 0.5s cubic-bezier(0.68, -0.55, 0.265, 1.55);
    --transition-fast: all 0.2s ease-out;
}
```

**灵动点**：
- 粒子：聚光灯效果，向中心聚集+拖尾
- 霓虹光晕：粉色霓虹发光
- Live感：粉蓝渐变+高对比

---

### 主题9：能天使 (exia)
**概念**：Gundam Exia 白底黑线，GN粒子的纯粹

```css
[data-theme="exia"] {
    --bg-primary: #fafafa;
    --bg-secondary: rgba(240, 240, 240, 0.95);
    --bg-tertiary: rgba(232, 232, 232, 0.9);
    --bg-elevated: rgba(255, 255, 255, 0.98);
    --bg-card: rgba(240, 240, 240, 0.95);
    
    --text-primary: #0a0a0a;
    --text-secondary: #404040;
    --text-tertiary: #808080;
    --text-muted: #a0a0a0;
    
    --accent-primary: #1a1a1a;
    --accent-secondary: #4a4a4a;
    --accent-tertiary: #6a6a6a;
    --accent-gradient: linear-gradient(135deg, #0a0a0a 0%, #2a2a2a 50%, #4a4a4a 100%);
    
    --glow-primary: rgba(26, 26, 26, 0.15);
    --glow-secondary: rgba(74, 74, 74, 0.1);
    --border-subtle: rgba(0, 0, 0, 0.12);
    --border-glow: rgba(0, 0, 0, 0.08);
    --shadow-color: rgba(0, 0, 0, 0.04);
    
    --success: #00c853;
    --warning: #ff9100;
    --error: #ff1744;
    --info: #2979ff;
    
    --particle-color: #00c853;
    --particle-opacity: 0.4;
    --particle-glow: 0 0 6px #00c853;
    --particle-type: wireframe;
    
    --card-backdrop: none;
    --card-radius: 2px;
    --button-radius: 0px;
    
    --font-heading: 'Inter', sans-serif;
    --font-body: 'Inter', sans-serif;
    --font-mono: 'JetBrains Mono', monospace;
    
    --transition-smooth: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    --transition-bounce: all 0.5s cubic-bezier(0.68, -0.55, 0.265, 1.55);
    --transition-fast: all 0.2s ease-out;
}
```

**灵动点**：
- 粒子：wireframe水平线条划过
- 极简线条：白底黑线，无圆角
- GN粒子：绿色粒子+纯粹感

---

### 主题10：VEDA (veda)
**概念**：VEDA系统界面，宇宙数据流的蓝紫透明感

```css
[data-theme="veda"] {
    --bg-primary: #0a0a1a;
    --bg-secondary: rgba(13, 16, 32, 0.95);
    --bg-tertiary: rgba(18, 24, 48, 0.9);
    --bg-elevated: rgba(26, 32, 64, 0.95);
    --bg-card: rgba(13, 16, 32, 0.95);
    
    --text-primary: #e8f0ff;
    --text-secondary: #90a0d0;
    --text-tertiary: #6070a0;
    --text-muted: #405080;
    
    --accent-primary: #448aff;
    --accent-secondary: #7c4dff;
    --accent-tertiary: #e040fb;
    --accent-gradient: linear-gradient(135deg, #00b0ff 0%, #448aff 35%, #7c4dff 70%, #e040fb 100%);
    
    --glow-primary: rgba(68, 138, 255, 0.6);
    --glow-secondary: rgba(124, 77, 255, 0.5);
    --border-subtle: rgba(68, 138, 255, 0.2);
    --border-glow: rgba(68, 138, 255, 0.25);
    --shadow-color: rgba(68, 138, 255, 0.2);
    
    --success: #69f0ae;
    --warning: #ffd740;
    --error: #ff5252;
    --info: #40c4ff;
    
    --particle-color: #00b0ff;
    --particle-opacity: 0.7;
    --particle-glow: 0 0 6px #00b0ff;
    --particle-type: datastream;
    
    --card-backdrop: blur(6px);
    --card-radius: 8px;
    --button-radius: 6px;
    
    --font-heading: 'Inter', sans-serif;
    --font-body: 'Inter', sans-serif;
    --font-mono: 'JetBrains Mono', monospace;
    
    --transition-smooth: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    --transition-bounce: all 0.5s cubic-bezier(0.68, -0.55, 0.265, 1.55);
    --transition-fast: all 0.2s ease-out;
}
```

**灵动点**：
- 粒子：datastream数据流垂直下落
- 透明感：蓝紫渐变+深色背景
- 科技感：四色渐变强调色

---

### 主题11：00-Raiser (raiser)
**概念**：00-Raiser 双炉系统，金蓝GN粒子交织

```css
[data-theme="raiser"] {
    --bg-primary: #0a0a14;
    --bg-secondary: rgba(15, 15, 31, 0.95);
    --bg-tertiary: rgba(21, 21, 45, 0.9);
    --bg-elevated: rgba(31, 31, 61, 0.95);
    --bg-card: rgba(15, 15, 31, 0.8);
    
    --text-primary: #f0f0ff;
    --text-secondary: #a0a0d0;
    --text-tertiary: #7070a0;
    --text-muted: #505070;
    
    --accent-primary: #ffd700;
    --accent-secondary: #00bfff;
    --accent-tertiary: #ff6b9d;
    --accent-gradient: linear-gradient(135deg, #ffd700 0%, #ffed4e 25%, #00e5ff 60%, #00bfff 100%);
    
    --glow-primary: rgba(255, 215, 0, 0.6);
    --glow-secondary: rgba(0, 191, 255, 0.5);
    --border-subtle: rgba(255, 215, 0, 0.15);
    --border-glow: rgba(0, 191, 255, 0.35);
    --shadow-color: rgba(255, 215, 0, 0.15);
    
    --success: #00e676;
    --warning: #ffd740;
    --error: #ff5252;
    --info: #00bfff;
    
    --particle-color: #ffd700;
    --particle-opacity: 0.6;
    --particle-glow: 0 0 6px #ffd700;
    --particle-type: twinparticle;
    
    --card-backdrop: blur(8px);
    --card-radius: 12px;
    --button-radius: 8px;
    
    --font-heading: 'Inter', sans-serif;
    --font-body: 'Inter', sans-serif;
    --font-mono: 'JetBrains Mono', monospace;
    
    --transition-smooth: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    --transition-bounce: all 0.5s cubic-bezier(0.68, -0.55, 0.265, 1.55);
    --transition-fast: all 0.2s ease-out;
}
```

**灵动点**：
- 粒子：twinparticle金蓝交替+同步相位
- 双炉感：金蓝渐变+GN粒子
- 高达风：深色背景+亮色强调

---

## ✨ 粒子系统规范（以demo16为准）

### 粒子类型定义

| 类型ID | 名称 | 描述 | 适用主题 |
|--------|------|------|----------|
| `matrix` | 矩阵雨 | 代码雨效果 | cyber |
| `firefly` | 萤火虫 | 闪烁+随机飞行 | bamboo |
| `sakura` | 樱花 | 旋转飘落 | sakura-white |
| `creamy` | 奶油 | 极缓慢+融化感 | mint-choco |
| `bubble` | 泡泡 | 上升+反光 | strawberry-cream |
| `rising` | 上升 | 快速上升+合并 | orange-soda |
| `musical` | 音符 | 跳动+波形 | mygo-light |
| `spotlight` | 聚光灯 | 向中心聚集+拖尾 | bangdream-dark |
| `wireframe` | 线框 | 水平线条划过 | exia |
| `datastream` | 数据流 | 垂直下落+字符 | veda |
| `twinparticle` | 双炉 | 金蓝交替+同步 | raiser |

### 粒子类实现（完整版）

```javascript
class Particle {
    constructor() {
        this.reset();
    }

    getParticleType() {
        const style = getComputedStyle(document.body);
        return style.getPropertyValue('--particle-type').trim() || 'floating';
    }

    reset() {
        const style = getComputedStyle(document.body);
        const particleType = this.getParticleType();
        
        this.x = Math.random() * canvas.width;
        this.y = Math.random() * canvas.height;
        this.size = Math.random() * 3 + 1;
        this.opacity = Math.random() * 0.5 + 0.2;
        this.color = style.getPropertyValue('--particle-color').trim() || '#52b788';
        this.baseOpacity = parseFloat(style.getPropertyValue('--particle-opacity')) || 0.5;
        this.type = particleType;
        this.life = 0;
        this.maxLife = Math.random() * 200 + 100;
        
        switch(particleType) {
            case 'matrix':
                this.speedX = 0;
                this.speedY = Math.random() * 3 + 2;
                this.char = String.fromCharCode(0x30A0 + Math.floor(Math.random() * 96));
                this.brightness = Math.random();
                break;
            case 'firefly':
                this.speedX = (Math.random() - 0.5) * 0.8;
                this.speedY = (Math.random() - 0.5) * 0.8;
                this.flashSpeed = Math.random() * 0.05 + 0.02;
                this.flashPhase = Math.random() * Math.PI * 2;
                break;
            case 'sakura':
                this.speedX = (Math.random() - 0.5) * 1.2;
                this.speedY = Math.random() * 0.6 + 0.3;
                this.rotation = Math.random() * Math.PI * 2;
                this.rotationSpeed = (Math.random() - 0.5) * 0.04;
                this.swayAmplitude = Math.random() * 30 + 20;
                this.swayPhase = Math.random() * Math.PI * 2;
                break;
            case 'creamy':
                this.speedX = (Math.random() - 0.5) * 0.15;
                this.speedY = (Math.random() - 0.5) * 0.15;
                this.meltSize = this.size;
                this.melting = false;
                break;
            case 'bubble':
                this.speedX = (Math.random() - 0.5) * 0.3;
                this.speedY = -(Math.random() * 0.4 + 0.15);
                this.wobble = Math.random() * Math.PI * 2;
                this.wobbleSpeed = Math.random() * 0.03 + 0.01;
                break;
            case 'rising':
                this.speedX = (Math.random() - 0.5) * 0.2;
                this.speedY = -(Math.random() * 1.2 + 0.6);
                break;
            case 'musical':
                this.speedX = (Math.random() - 0.5) * 0.4;
                this.speedY = (Math.random() - 0.5) * 0.4;
                this.pulse = Math.random() * Math.PI * 2;
                this.pulseSpeed = Math.random() * 0.08 + 0.04;
                this.noteType = Math.floor(Math.random() * 3);
                break;
            case 'spotlight':
                this.speedX = (Math.random() - 0.5) * 3;
                this.speedY = (Math.random() - 0.5) * 3;
                this.targetX = canvas.width / 2;
                this.targetY = canvas.height / 2;
                this.trail = [];
                break;
            case 'wireframe':
                this.speedX = Math.random() * 4 + 3;
                this.speedY = (Math.random() - 0.5) * 0.5;
                this.length = Math.random() * 25 + 10;
                this.x = Math.random() * (canvas.width + 400) - 200;
                this.y = Math.random() * canvas.height;
                break;
            case 'datastream':
                this.speedX = 0;
                this.speedY = Math.random() * 2 + 1;
                this.length = Math.random() * 30 + 10;
                this.char = String.fromCharCode(0x30A0 + Math.floor(Math.random() * 96));
                break;
            case 'twinparticle':
                this.speedX = (Math.random() - 0.5) * 1.5;
                this.speedY = (Math.random() - 0.5) * 1.5;
                this.isGold = Math.random() > 0.5;
                break;
            default:
                this.speedX = (Math.random() - 0.5) * 0.5;
                this.speedY = (Math.random() - 0.5) * 0.5;
        }
    }

    update() {
        const particleType = this.getParticleType();
        if (this.type !== particleType) {
            this.reset();
            return;
        }

        this.life++;

        switch(this.type) {
            case 'matrix':
                this.y += this.speedY;
                if (Math.random() < 0.05) {
                    this.char = String.fromCharCode(0x30A0 + Math.floor(Math.random() * 96));
                }
                if (this.y > canvas.height || this.life > this.maxLife) {
                    this.reset();
                }
                break;
            case 'firefly':
                this.x += this.speedX;
                this.y += this.speedY;
                this.opacity = this.baseOpacity * (0.5 + 0.5 * Math.sin(this.life * this.flashSpeed + this.flashPhase));
                if (this.x < 0 || this.x > canvas.width || this.y < 0 || this.y > canvas.height || this.life > this.maxLife) {
                    this.reset();
                }
                break;
            case 'sakura':
                this.swayPhase += 0.02;
                this.x += this.speedX + Math.sin(this.swayPhase) * 0.5;
                this.y += this.speedY;
                this.rotation += this.rotationSpeed;
                if (this.y > canvas.height || this.life > this.maxLife) {
                    this.reset();
                }
                break;
            case 'creamy':
                if (!this.melting && Math.random() < 0.001) {
                    this.melting = true;
                }
                if (this.melting) {
                    this.meltSize += 0.05;
                    this.opacity *= 0.99;
                }
                this.x += this.speedX;
                this.y += this.speedY;
                if (this.opacity < 0.1) this.reset();
                break;
            case 'bubble':
                this.wobble += this.wobbleSpeed;
                this.x += this.speedX + Math.sin(this.wobble) * 0.3;
                this.y += this.speedY;
                this.opacity = this.baseOpacity * (0.7 + 0.3 * Math.sin(this.wobble));
                if (this.y < -20 || this.life > this.maxLife) {
                    this.reset();
                }
                break;
            case 'rising':
                this.x += this.speedX;
                this.y += this.speedY;
                this.opacity = this.baseOpacity * Math.min(1, this.life / 30);
                if (this.y < -20 || this.life > this.maxLife) {
                    this.reset();
                }
                break;
            case 'musical':
                this.pulse += this.pulseSpeed;
                this.x += this.speedX;
                this.y += this.speedY;
                this.size = 2 + Math.sin(this.pulse) * 1;
                if (this.x < 0 || this.x > canvas.width || this.y < 0 || this.y > canvas.height || this.life > this.maxLife) {
                    this.reset();
                }
                break;
            case 'spotlight':
                const dx = this.targetX - this.x;
                const.dy = this.targetY - this.y;
                this.speedX += dx * 0.0005;
                this.speedY += dy * 0.0005;
                this.speedX *= 0.98;
                this.speedY *= 0.98;
                this.x += this.speedX;
                this.y += this.speedY;
                this.trail.push({x: this.x, y: this.y, life: 10});
                this.trail = this.trail.filter(t => --t.life > 0);
                if (this.life > this.maxLife) {
                    this.reset();
                }
                break;
            case 'wireframe':
                this.x += this.speedX;
                this.y += this.speedY;
                if (this.x > canvas.width + 50) {
                    this.reset();
                }
                break;
            case 'datastream':
                this.y += this.speedY;
                if (this.y > canvas.height || this.life > this.maxLife) {
                    this.reset();
                }
                break;
            case 'twinparticle':
                this.x += this.speedX;
                this.y += this.speedY;
                this.color = this.isGold ? '#ffd700' : '#00bfff';
                if (this.x < 0 || this.x > canvas.width || this.y < 0 || this.y > canvas.height || this.life > this.maxLife) {
                    this.reset();
                }
                break;
            default:
                this.x += this.speedX;
                this.y += this.speedY;
                if (this.x < 0 || this.x > canvas.width || this.y < 0 || this.y > canvas.height || this.life > this.maxLife) {
                    this.reset();
                }
        }
    }

    draw() {
        ctx.save();

        switch(this.type) {
            case 'matrix':
                ctx.globalAlpha = this.baseOpacity * this.brightness;
                ctx.fillStyle = this.color;
                ctx.font = '14px monospace';
                ctx.textAlign = 'center';
                ctx.fillText(this.char, this.x, this.y);
                break;
            case 'firefly':
                ctx.globalAlpha = this.opacity;
                ctx.fillStyle = this.color;
                ctx.shadowBlur = 15;
                ctx.shadowColor = this.color;
                ctx.beginPath();
                ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
                ctx.fill();
                break;
            case 'sakura':
                ctx.globalAlpha = this.baseOpacity;
                ctx.fillStyle = this.color;
                ctx.translate(this.x, this.y);
                ctx.rotate(this.rotation);
                // 绘制樱花形状
                for (let i = 0; i < 5; i++) {
                    ctx.rotate((Math.PI * 2) / 5);
                    ctx.beginPath();
                    ctx.ellipse(0, -this.size * 2, this.size * 0.6, this.size * 1.5, 0, 0, Math.PI * 2);
                    ctx.fill();
                }
                break;
            case 'creamy':
                ctx.globalAlpha = this.opacity * this.baseOpacity;
                ctx.fillStyle = this.color;
                ctx.beginPath();
                ctx.arc(this.x, this.y, this.melting ? this.meltSize : this.size, 0, Math.PI * 2);
                ctx.fill();
                break;
            case 'bubble':
                ctx.globalAlpha = this.baseOpacity * 0.6;
                ctx.strokeStyle = this.color;
                ctx.lineWidth = 1;
                ctx.beginPath();
                ctx.arc(this.x, this.y, this.size * 3, 0, Math.PI * 2);
                ctx.stroke();
                ctx.globalAlpha = this.baseOpacity * 0.8;
                ctx.fillStyle = '#ffffff';
                ctx.beginPath();
                ctx.arc(this.x - this.size, this.y - this.size, this.size * 0.5, 0, Math.PI * 2);
                ctx.fill();
                break;
            case 'rising':
                ctx.globalAlpha = this.opacity;
                ctx.fillStyle = this.color;
                ctx.beginPath();
                ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
                ctx.fill();
                break;
            case 'musical':
                ctx.globalAlpha = this.baseOpacity;
                ctx.fillStyle = this.color;
                ctx.font = `${this.size * 3}px Arial`;
                ctx.textAlign = 'center';
                ctx.textBaseline = 'middle';
                const notes = ['♪', '♫', '♬'];
                ctx.fillText(notes[this.noteType], this.x, this.y);
                break;
            case 'spotlight':
                this.trail.forEach((t, i) => {
                    ctx.globalAlpha = t.life / 10 * this.baseOpacity * 0.5;
                    ctx.fillStyle = this.color;
                    ctx.beginPath();
                    ctx.arc(t.x, t.y, this.size * (t.life / 10), 0, Math.PI * 2);
                    ctx.fill();
                });
                ctx.globalAlpha = this.baseOpacity;
                ctx.fillStyle = this.color;
                ctx.shadowBlur = 15;
                ctx.shadowColor = this.color;
                ctx.beginPath();
                ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
                ctx.fill();
                break;
            case 'wireframe':
                ctx.globalAlpha = this.baseOpacity * 0.8;
                ctx.strokeStyle = this.color;
                ctx.lineWidth = 1.5;
                ctx.shadowBlur = 8;
                ctx.shadowColor = this.color;
                ctx.beginPath();
                ctx.moveTo(this.x, this.y);
                ctx.lineTo(this.x - this.length, this.y);
                ctx.stroke();
                break;
            case 'datastream':
                ctx.globalAlpha = this.baseOpacity;
                ctx.fillStyle = this.color;
                ctx.font = `${this.size * 4}px monospace`;
                ctx.textAlign = 'center';
                ctx.fillText(this.char, this.x, this.y);
                break;
            case 'twinparticle':
                ctx.globalAlpha = this.baseOpacity;
                ctx.fillStyle = this.color;
                ctx.shadowBlur = 10;
                ctx.shadowColor = this.color;
                ctx.beginPath();
                ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
                ctx.fill();
                break;
            default:
                ctx.globalAlpha = this.baseOpacity;
                ctx.fillStyle = this.color;
                ctx.beginPath();
                ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
                ctx.fill();
        }
        
        ctx.restore();
    }
}
```

---

## 🎯 彩蛋提示

> 代码注释里藏一句：「// 凌晨两点的光标，还在等待下一行代码」

---

## ♿ Accessibility 规范

所有动效必须支持 `prefers-reduced-motion`：

```css
@media (prefers-reduced-motion: reduce) {
    * {
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.01ms !important;
    }
    
    #particles-canvas {
        display: none;
    }
}
```

---

## 📋 home系统修正清单

### 必须修正的主题
1. **cyberpunk** → 按demo16的cyber修正颜色（青+粉）
2. **exia** → 完全重写为白底黑线风格
3. **sakura** → 改为白色背景（或新增sakura-white）

### 必须添加的主题
- bamboo, mint-choco, strawberry-cream, orange-soda, mygo-light, bangdream-dark

### 必须添加的粒子类型
- creamy, musical, spotlight

### 建议统一的变量
- demo16的变量名更完整，建议home系统添加：
  - `--bg-tertiary`
  - `--text-muted`
  - `--shadow-color`
  - `--particle-glow`
  - `--card-backdrop`
  - `--font-heading/body/mono`
  - `--transition-*`

---

*星绘注：本文档以demo16-optimized-themes.html为准，home系统需要按此修正*
