# SynthInk 页面动态效果设计文档

> 概念句：每一次交互都是与灵感的触碰，每一帧动画都是思绪的流动

---

## 目录

1. [设计哲学](#设计哲学)
2. [架构设计](#架构设计)
3. [效果模块详解](#效果模块详解)
4. [被移除的效果](#被移除的效果)
5. [动画规范](#动画规范)
6. [使用指南](#使用指南)
7. [扩展开发](#扩展开发)
8. [附录](#附录)

---

## 设计哲学

### 核心原则

#### 1. 服务而非炫技
动画存在的唯一目的是增强用户体验，而非展示技术能力。判断一个动画是否必要的方法：**如果删掉它，页面依然完整且功能不受影响，那就考虑删掉它**。

#### 2. 克制与留白
动画密度控制在"轻宅"级别（1-3个灵动点）。过多的动画会：
- 分散用户对内容的注意力
- 增加认知负荷
- 降低页面性能
- 引发视觉疲劳

给用户留出思考和呼吸的空间，留白本身就是一种设计。

#### 3. 一致性体验
所有动画遵循统一的规范：
- **时长标准**：同类型动画使用相同时长
- **缓动函数**：统一的缓动曲线家族
- **视觉风格**：与主题系统保持协调
- **交互反馈**：相似的操作产生相似的反馈

#### 4. 尊重用户偏好
- 支持 `prefers-reduced-motion` 媒体查询，尊重用户的减少动画偏好
- 触摸设备自动降级或禁用复杂效果（如3D倾斜）
- 提供关闭动画的选项（通过主题系统或独立开关）

### 设计决策流程

当考虑添加一个新效果时，按以下顺序思考：

```
1. 这个效果要解决什么问题？
   ↓ 如果不能明确回答，不要添加

2. 是否有更简单的解决方案？
   ↓ 如果有，优先使用简单方案

3. 这个效果是否符合品牌调性？
   ↓ SynthInk是写作工具，专业、冷静、有质感

4. 是否会影响性能或可访问性？
   ↓ 如果会，需要优化或放弃

5. 用户能否感知到这个效果的价值？
   ↓ 如果用户不会注意到，不要添加
```

---

## 架构设计

### 模块结构

```
design-system/js/effects/
├── typewriter.js          # 打字机效果
├── count-up.js            # 数字滚动
├── tilt-card.js           # 3D卡片倾斜
├── floating-elements.js   # 浮动装饰元素
├── mouse-glow.js          # [已停用] 鼠标光晕
└── text-scramble.js       # [已停用] 文字解码
```

### 统一接口规范

每个效果模块必须实现以下接口：

```javascript
const EffectName = {
    // 配置默认值
    config: { ... },
    
    // 初始化入口
    init(selector, options) { ... },
    
    // 销毁/清理（可选）
    destroy() { ... },
    
    // 暂停/恢复（可选）
    pause() { ... },
    resume() { ... }
};
```

### 与主题系统的协作

页面动态效果**独立于**主题系统，但会**适配**主题系统：

- **独立**：不依赖主题系统的CSS变量，确保在任何主题下都能正常工作
- **适配**：通过读取 `--accent-primary` 等CSS变量，使效果颜色与当前主题协调

```javascript
// 示例：获取主题色
const accentColor = getComputedStyle(document.documentElement)
    .getPropertyValue('--accent-primary').trim();
```

---

## 效果模块详解

### 1. Typewriter - 打字机效果

#### 设计意图
- **营造临场感**：模拟"正在输入"的状态，强调 SynthInk 作为写作工具的定位
- **制造期待感**：标题的逐字出现让用户产生"接下来会是什么"的好奇
- **强化品牌记忆**：独特的交互方式加深用户对产品的印象

#### 技术实现

**核心机制**：
```javascript
// 逐字符输出
function type(element, text, speed, index) {
    if (index < text.length) {
        element.textContent += text[index];
        setTimeout(() => type(element, text, speed, index + 1), speed);
    }
}
```

**光标实现**：
```css
.typewriter-cursor {
    animation: blink 1s infinite;
    color: var(--accent-primary);
}

@keyframes blink {
    0%, 50% { opacity: 1; }
    51%, 100% { opacity: 0; }
}
```

**配置选项**：
| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `speed` | number | 50 | 字符输出间隔（毫秒） |
| `delay` | number | 0 | 开始打字前的延迟（毫秒） |
| `cursor` | boolean | true | 是否显示光标 |
| `cursorChar` | string | '\|' | 光标字符 |

#### 使用场景

**适合**：
- Hero 区域主标题
- 强调性的 Slogan
- 短句（不超过20个字符）

**不适合**：
- 长文本（影响阅读效率）
- 需要快速获取信息的场景
- 频繁切换的页面

#### 最佳实践

```javascript
// Hero标题 - 较慢速度营造仪式感
Typewriter.init('.hero-title', { speed: 80, delay: 300 });

// Slogan - 较快速度保持流畅
Typewriter.init('.slogan', { speed: 50, delay: 100 });
```

---

### 2. CountUp - 数字滚动效果

#### 设计意图
- **增强可信度**：动态增长的数字比静态数字更有说服力
- **暗示积累**：从0增长到目标值的过程，象征平台的成长和用户积累
- **吸引注意力**：动态变化自然吸引视线，突出关键指标

#### 技术实现

**动画循环**：
```javascript
function animate(timestamp) {
    const elapsed = timestamp - startTime;
    const progress = Math.min(elapsed / duration, 1);
    
    // easeOutExpo 缓动：先快后慢
    const easeProgress = 1 - Math.pow(2, -10 * progress);
    const current = startValue + (target - startValue) * easeProgress;
    
    element.textContent = formatNumber(current);
    
    if (progress < 1) {
        requestAnimationFrame(animate);
    }
}
```

**缓动函数对比**：
| 缓动类型 | 曲线 | 适用场景 |
|----------|------|----------|
| Linear | 直线 | 机械计数器 |
| EaseOut | 先快后慢 | 一般数字展示 |
| EaseOutExpo | 急剧减速 | 强调数字的冲击感（推荐） |
| EaseInOut | 慢-快-慢 | 需要平衡感的场景 |

**配置选项**：
| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `duration` | number | 2000 | 动画持续时间（毫秒） |
| `suffix` | string | '' | 数字后缀（如'+'、'%'） |
| `prefix` | string | '' | 数字前缀（如'$'、'¥'） |
| `separator` | string | ',' | 千分位分隔符 |
| `decimals` | number | 0 | 小数位数 |

#### 使用场景

**适合**：
- 统计数据展示（用户数、文章数、阅读量）
- 成就里程碑
- 实时数据更新（可扩展）

**不适合**：
- 频繁变化的数字（造成视觉疲劳）
- 精确到小数点后多位的财务数据（动画过程中的中间值不准确）

#### HTML 标记方式

```html
<!-- 基础用法 -->
<span class="stat-value" data-count-target="10000">0</span>

<!-- 带后缀 -->
<span class="stat-value" data-count-target="10" data-count-suffix="K+">0</span>

<!-- 带前缀和小数 -->
<span class="stat-value" data-count-target="99.9" data-count-prefix="¥" data-count-decimals="1">0</span>
```

#### 最佳实践

```javascript
// 默认配置 - 2秒时长，适合大多数场景
CountUp.init('.stat-value', { duration: 2000 });

// 快速展示 - 1秒时长，适合次要数据
CountUp.init('.secondary-stat', { duration: 1000 });
```

---

### 3. TiltCard - 3D卡片倾斜效果

#### 设计意图
- **增加层次感**：打破平面的单调，创造立体空间感
- **提升交互质感**：鼠标悬停时的微妙反馈，让用户感受到"可交互"
- **模拟材质**：反光效果模拟真实材质的光泽，增强视觉丰富度

#### 技术实现

**3D变换计算**：
```javascript
function calculateTilt(mouseX, mouseY, rect) {
    const centerX = rect.width / 2;
    const centerY = rect.height / 2;
    
    // 鼠标相对于卡片中心的位置（-1 到 1）
    const percentX = (mouseX - centerX) / centerX;
    const percentY = (mouseY - centerY) / centerY;
    
    // 计算旋转角度（Y轴旋转由X位置决定，X轴旋转由Y位置决定）
    const rotateY = percentX * maxTilt;
    const rotateX = -percentY * maxTilt;
    
    return { rotateX, rotateY };
}

// 应用变换
element.style.transform = `
    perspective(${perspective}px)
    rotateX(${rotateX}deg)
    rotateY(${rotateY}deg)
    scale3d(${scale}, ${scale}, ${scale})
`;
```

**反光效果**：
```javascript
function createGlare(element) {
    const glare = document.createElement('div');
    glare.className = 'tilt-glare';
    glare.style.cssText = `
        position: absolute;
        inset: 0;
        background: radial-gradient(
            circle at var(--mouse-x, 50%) var(--mouse-y, 50%),
            rgba(255,255,255,0.3) 0%,
            transparent 60%
        );
        pointer-events: none;
        opacity: 0;
        transition: opacity 0.3s;
    `;
    element.appendChild(glare);
    return glare;
}
```

**配置选项**：
| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `maxTilt` | number | 15 | 最大倾斜角度（度） |
| `perspective` | number | 1000 | 透视距离（像素） |
| `scale` | number | 1.02 | 悬停时的缩放比例 |
| `speed` | number | 400 | 过渡动画时长（毫秒） |
| `glare` | boolean | true | 是否启用反光效果 |
| `maxGlare` | number | 0.3 | 反光最大透明度 |

#### 使用场景

**适合**：
- 特性卡片（feature cards）
- 产品展示卡片
- 需要强调交互性的元素

**不适合**：
- 列表项（性能考虑，大量DOM操作）
- 触摸设备（无法悬停，体验不一致）
- 内容密集区域（视觉混乱）

#### 性能考虑

- 使用 `transform` 实现动画，触发GPU加速
- 反光效果使用伪元素或独立div，避免重绘
- 鼠标移动事件使用 `requestAnimationFrame` 节流

#### 最佳实践

```javascript
// 特性卡片 - 适度倾斜，带反光
TiltCard.init('.feature-card', { maxTilt: 10, glare: true });

// 产品卡片 - 较大倾斜，增强视觉冲击
TiltCard.init('.product-card', { maxTilt: 20, scale: 1.05 });

// 禁用反光 - 简洁风格
TiltCard.init('.minimal-card', { maxTilt: 5, glare: false });
```

---

### 4. FloatingElements - 浮动装饰元素

#### 设计意图
- **背景丰富度**：避免大面积留白造成的单调感
- **营造氛围**：缓慢的运动创造轻盈、灵动的氛围
- **品牌呼应**：几何形状（圆、方）呼应"合成"、"构建"的品牌意象

#### 技术实现

**元素生成**：
```javascript
function createElement(config) {
    const el = document.createElement('div');
    const size = random(config.minSize, config.maxSize);
    const shape = randomChoice(config.shapes);
    
    // 基础样式
    el.style.cssText = `
        position: fixed;
        width: ${size}px;
        height: ${size}px;
        background: ${randomChoice(config.colors)};
        z-index: ${config.zIndex};
        pointer-events: none;
        opacity: ${random(0.1, 0.5)};
    `;
    
    // 形状样式
    if (shape === 'circle') {
        el.style.borderRadius = '50%';
    } else if (shape === 'triangle') {
        // 三角形使用border技巧
        el.style.width = '0';
        el.style.height = '0';
        el.style.background = 'transparent';
        el.style.borderLeft = `${size/2}px solid transparent`;
        el.style.borderRight = `${size/2}px solid transparent`;
        el.style.borderBottom = `${size}px solid ${randomChoice(config.colors)}`;
    }
    
    return {
        el,
        x: random(0, window.innerWidth),
        y: random(0, window.innerHeight),
        speedX: random(-0.3, 0.3),
        speedY: random(-0.3, 0.3),
        rotation: random(0, 360),
        rotationSpeed: random(-0.2, 0.2)
    };
}
```

**动画循环**：
```javascript
function animate() {
    elements.forEach(item => {
        // 更新位置
        item.x += item.speedX;
        item.y += item.speedY;
        item.rotation += item.rotationSpeed;
        
        // 边界循环
        if (item.x < -100) item.x = window.innerWidth + 100;
        if (item.x > window.innerWidth + 100) item.x = -100;
        if (item.y < -100) item.y = window.innerHeight + 100;
        if (item.y > window.innerHeight + 100) item.y = -100;
        
        // 应用变换
        item.el.style.transform = `translate(${item.x}px, ${item.y}px) rotate(${item.rotation}deg)`;
    });
    
    requestAnimationFrame(animate);
}
```

**配置选项**：
| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `count` | number | 5 | 元素数量 |
| `shapes` | array | ['circle', 'square'] | 形状类型 |
| `minSize` | number | 20 | 最小尺寸（像素） |
| `maxSize` | number | 80 | 最大尺寸（像素） |
| `colors` | array | ['rgba(255,255,255,0.03)'] | 颜色数组 |
| `zIndex` | number | -1 | 层级 |

#### 使用场景

**适合**：
- 页面背景装饰
- Hero区域的大面积留白
- 登录/注册页面的氛围营造

**不适合**：
- 内容密集区域（干扰阅读）
- 需要专注的编辑界面
- 性能敏感的老旧设备

#### 性能优化

- 元素数量控制在10个以内
- 使用 `transform` 而非 `top/left` 移动
- 触摸设备减少数量或完全禁用
- 页面不可见时暂停动画（使用 Page Visibility API）

#### 最佳实践

```javascript
// Hero区域 - 较多元素，营造氛围
FloatingElements.init({
    count: 8,
    shapes: ['circle', 'square', 'triangle'],
    minSize: 30,
    maxSize: 100,
    colors: ['rgba(255,255,255,0.03)', 'rgba(255,255,255,0.05)']
});

// 简洁背景 - 少量元素，不喧宾夺主
FloatingElements.init({
    count: 4,
    shapes: ['circle'],
    minSize: 50,
    maxSize: 150,
    colors: ['rgba(0,0,0,0.02)']
});
```

---

## 被移除的效果

### MouseGlow - 鼠标跟随光晕

#### 原始设计
在鼠标位置显示一个跟随移动的光晕，使用径向渐变实现发光效果，颜色跟随主题色变化。

#### 移除原因

1. **干扰阅读**
   - 大面积色块覆盖文字，降低可读性
   - 快速移动时产生视觉残留，分散注意力

2. **与主题系统冲突**
   - 主题系统已有粒子效果作为背景装饰
   - 鼠标光晕与粒子效果叠加，造成视觉混乱

3. **性能问题**
   - 鼠标移动事件触发频繁，持续计算位置
   - 大模糊半径的径向渐变消耗GPU资源

4. **不符合品牌调性**
   - SynthInk定位是专业写作工具，光晕效果过于"游戏化"
   - 冷静、克制的品牌风格与花哨的光晕不匹配

#### 替代方案
如果需要强调鼠标位置，考虑：
- 按钮/链接的悬停状态变化
- 光标样式的微调（如自定义光标）
- 点击时的涟漪效果（Ripple）

---

### TextScramble - 文字解码效果

#### 原始设计
文字从随机字符逐渐"解码"为正确内容，模拟黑客帝国风格的字符下落效果。

#### 移除原因

1. **影响可读性**
   - 解码过程中文字不可读，用户无法获取信息
   - 随机字符可能造成误解（如被误认为乱码）

2. **阅读中断**
   - 用户需要等待解码完成才能阅读
   - 打断用户的阅读流（Reading Flow）

3. **不符合专业定位**
   - 解码效果过于"炫酷"，与写作工具的专业形象冲突
   - 可能让用户觉得不够严肃

4. **可访问性问题**
   - 屏幕阅读器无法正确读取解码中的文字
   - 对阅读障碍用户不友好

#### 替代方案
如果需要文字动画效果，考虑：
- 打字机效果（Typewriter）- 已采用
- 简单的淡入效果
- 逐行出现的滑动效果

---

## 动画规范

### 时长标准

| 类型 | 时长范围 | 典型值 | 说明 |
|------|----------|--------|------|
| 微交互 | 100-200ms | 150ms | 按钮hover、状态切换 |
| 过渡动画 | 200-400ms | 300ms | 页面切换、元素出现/消失 |
| 强调动画 | 500-1000ms | 800ms | 打字机、数字滚动 |
| 环境动画 | 持续 | - | 浮动元素、粒子效果 |

**选择原则**：
- 越小的元素，动画时长越短
- 越重要的操作，动画时长越长（给予用户反馈）
- 环境动画速度要慢，不干扰主要内容

### 缓动函数

#### 标准缓动家族

```css
:root {
    /* 标准缓出 - 快速开始，缓慢结束 */
    --ease-out: cubic-bezier(0.16, 1, 0.3, 1);
    
    /* 标准缓入缓出 - 缓慢开始，快速中间，缓慢结束 */
    --ease-in-out: cubic-bezier(0.65, 0, 0.35, 1);
    
    /* 弹性缓出 - 带有轻微回弹 */
    --ease-bounce: cubic-bezier(0.34, 1.56, 0.64, 1);
    
    /* 急剧缓出 - 非常快速的开始，极慢的结束 */
    --ease-expo: cubic-bezier(0.19, 1, 0.22, 1);
}
```

#### 使用场景

| 缓动类型 | 适用场景 |
|----------|----------|
| `ease-out` | 元素进入视口、展开面板 |
| `ease-in-out` | 状态切换、开关按钮 |
| `ease-bounce` | 强调性动画、成功提示 |
| `ease-expo` | 数字滚动、需要冲击感的动画 |

### 性能优化

#### DO（推荐）

1. **使用GPU加速属性**
   ```css
   /* 推荐 */
   transform: translateX(100px);
   opacity: 0.5;
   ```

2. **使用 will-change 提示**
   ```css
   .animated-element {
       will-change: transform, opacity;
   }
   
   /* 动画结束后移除 */
   .animated-element.animation-complete {
       will-change: auto;
   }
   ```

3. **使用 requestAnimationFrame**
   ```javascript
   function animate() {
       // 更新动画状态
       updateAnimation();
       requestAnimationFrame(animate);
   }
   ```

4. **节流高频事件**
   ```javascript
   // 鼠标移动事件节流
   let ticking = false;
   element.addEventListener('mousemove', (e) => {
       if (!ticking) {
           requestAnimationFrame(() => {
               handleMouseMove(e);
               ticking = false;
           });
           ticking = true;
       }
   });
   ```

#### DON'T（避免）

1. **避免触发重排的属性**
   ```css
   /* 避免 */
   width: 100px;
   height: 100px;
   top: 50px;
   left: 50px;
   margin: 10px;
   padding: 10px;
   ```

2. **避免在动画中读取布局属性**
   ```javascript
   // 避免 - 强制重排
   function badAnimate() {
       const height = element.offsetHeight; // 读取布局
       element.style.height = height + 1 + 'px'; // 修改布局
       requestAnimationFrame(badAnimate);
   }
   ```

3. **避免过多同时运行的动画**
   - 限制同时运行的动画数量
   - 使用 Intersection Observer 暂停视口外动画

### 可访问性

#### 尊重用户偏好

```css
/* 检测用户是否偏好减少动画 */
@media (prefers-reduced-motion: reduce) {
    *,
    *::before,
    *::after {
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.01ms !important;
    }
}
```

#### JavaScript 检测

```javascript
// 检测减少动画偏好
const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

if (!prefersReducedMotion) {
    // 初始化动画
    initAnimations();
}
```

#### 触摸设备适配

```javascript
// 检测触摸设备
const isTouchDevice = window.matchMedia('(pointer: coarse)').matches;

if (!isTouchDevice) {
    // 仅在非触摸设备启用悬停相关效果
    TiltCard.init('.card');
}
```

---

## 使用指南

### 快速开始

#### 1. 引入效果模块

```html
<!-- 在页面底部引入 -->
<script src="../js/effects/typewriter.js"></script>
<script src="../js/effects/count-up.js"></script>
```

#### 2. 初始化效果

```javascript
// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', () => {
    Typewriter.init('.hero-title', { speed: 80 });
    CountUp.init('.stat-value', { duration: 2000 });
});
```

### 通过 data 属性自动初始化

#### Typewriter

```html
<!-- 基础用法 -->
<h1 data-typewriter>标题文字</h1>

<!-- 自定义速度 -->
<h1 data-typewriter data-typewriter-speed="100">慢速打字</h1>

<!-- 带延迟 -->
<h1 data-typewriter data-typewriter-delay="500">延迟开始</h1>
```

#### CountUp

```html
<!-- 基础用法 -->
<span data-count-target="1000">0</span>

<!-- 带后缀 -->
<span data-count-target="10" data-count-suffix="K+">0</span>

<!-- 带前缀和小数 -->
<span data-count-target="99.9" data-count-prefix="¥" data-count-decimals="1">0</span>
```

#### TiltCard

```html
<!-- 基础用法 -->
<div data-tilt>卡片内容</div>

<!-- 自定义倾斜角度 -->
<div data-tilt data-tilt-max="20">大角度倾斜</div>

<!-- 禁用反光 -->
<div data-tilt data-tilt-glare="false">无反光</div>
```

#### FloatingElements

```html
<!-- 通过JavaScript初始化，无data属性支持 -->
```

### 组合使用

```html
<!-- Hero区域 -->
<section class="hero">
    <h1 class="hero-title" data-typewriter data-typewriter-speed="80">
        人机共创的写作空间
    </h1>
    <p class="hero-desc">让灵感自由流动</p>
    
    <div class="hero-stats">
        <div class="stat">
            <span class="stat-value" data-count-target="10" data-count-suffix="K+">0</span>
            <span class="stat-label">创作者</span>
        </div>
    </div>
</section>

<!-- 特性卡片 -->
<section class="features">
    <div class="feature-card" data-tilt data-tilt-max="10">
        <h3>AI协作</h3>
        <p>与AI共同创作</p>
    </div>
</section>
```

```javascript
document.addEventListener('DOMContentLoaded', () => {
    // 初始化所有效果
    Typewriter.init('[data-typewriter]');
    CountUp.init('[data-count-target]');
    TiltCard.init('[data-tilt]');
    FloatingElements.init({ count: 6 });
});
```

---

## 扩展开发

### 添加新效果的标准流程

#### 1. 需求分析

在动手编码前，回答以下问题：
- 这个效果要解决什么问题？
- 目标用户是谁？
- 在什么场景下使用？
- 是否有现成的解决方案？

#### 2. 设计文档

在 `effects-design.md` 中添加新章节，包含：
- 设计意图
- 技术实现方案
- 配置选项
- 使用场景
- 最佳实践

#### 3. 代码实现

创建 `design-system/js/effects/{effect-name}.js`：

```javascript
/**
 * EffectName - 效果描述
 * 
 * @author 星绘
 * @date 2026-03-03
 */

const EffectName = {
    // 默认配置
    config: {
        duration: 300,
        easing: 'ease-out'
    },
    
    /**
     * 初始化效果
     * @param {string} selector - CSS选择器
     * @param {Object} options - 配置选项
     */
    init(selector, options = {}) {
        // 检测减少动画偏好
        if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
            return;
        }
        
        // 合并配置
        const config = { ...this.config, ...options };
        
        // 获取元素
        const elements = document.querySelectorAll(selector);
        
        // 初始化逻辑
        elements.forEach(el => {
            this.bindEvents(el, config);
        });
    },
    
    /**
     * 绑定事件
     * @param {HTMLElement} element - DOM元素
     * @param {Object} config - 配置
     */
    bindEvents(element, config) {
        // 事件绑定逻辑
    },
    
    /**
     * 清理资源
     */
    destroy() {
        // 清理逻辑
    }
};

// 自动初始化（通过data属性）
document.addEventListener('DOMContentLoaded', () => {
    const autoElements = document.querySelectorAll('[data-effect-name]');
    if (autoElements.length > 0) {
        EffectName.init('[data-effect-name]');
    }
});
```

#### 4. 测试验证

- 在Chrome、Firefox、Safari测试
- 在移动端测试
- 开启 `prefers-reduced-motion` 测试降级
- 性能测试（Chrome DevTools Performance面板）

#### 5. 文档更新

- 更新本文档
- 更新 `agent_memo.md` 中的知识条目
- 在 `agent_project.md` 中记录任务

### 可考虑添加的效果

#### 1. ParallaxScroll - 视差滚动

**设计意图**：背景与前景以不同速度滚动，增加页面深度感。

**技术要点**：
- 监听滚动事件，计算不同层级的位移
- 使用 `transform: translateY()` 实现
- 限制层级数量（建议不超过3层）

**使用场景**：
- Hero区域的背景图
- 长页面的装饰元素

#### 2. MagneticButton - 磁性按钮

**设计意图**：按钮对鼠标产生轻微吸引，提升点击欲望。

**技术要点**：
- 计算鼠标与按钮中心的距离和方向
- 在阈值范围内产生位移
- 使用弹性缓动回归原位

**使用场景**：
- 主要CTA按钮
- 需要强调的操作按钮

#### 3. ScrollReveal - 滚动渐显

**设计意图**：元素进入视口时的出现动画，引导用户视线流动。

**技术要点**：
- 使用 Intersection Observer API
- 支持多种动画类型（淡入、滑动、缩放）
- 可配置触发阈值和根边距

**使用场景**：
- 长页面的内容区块
- 列表项的依次出现

---

## 附录

### A. 常见问题

#### Q1: 动画卡顿怎么办？

**排查步骤**：
1. 打开Chrome DevTools Performance面板
2. 录制动画过程
3. 查看是否有长任务（Long Tasks）
4. 检查是否触发了重排（Layout）

**解决方案**：
- 使用 `transform` 和 `opacity` 替代其他属性
- 减少同时运行的动画数量
- 使用 `will-change` 提示浏览器优化

#### Q2: 如何禁用特定效果？

```javascript
// 不初始化即可
// Typewriter.init('.title'); // 注释掉
```

或在CSS中覆盖：

```css
.typewriter-cursor {
    display: none !important;
}
```

#### Q3: 效果与主题系统冲突？

确保效果模块读取CSS变量时处理异常情况：

```javascript
const accentColor = getComputedStyle(document.documentElement)
    .getPropertyValue('--accent-primary').trim() || '#00f5d4';
```

### B. 浏览器兼容性

| 特性 | Chrome | Firefox | Safari | Edge |
|------|--------|---------|--------|------|
| transform | ✅ 36+ | ✅ 16+ | ✅ 9+ | ✅ 12+ |
| requestAnimationFrame | ✅ 24+ | ✅ 23+ | ✅ 6.1+ | ✅ 12+ |
| Intersection Observer | ✅ 51+ | ✅ 55+ | ✅ 12.1+ | ✅ 15+ |
| CSS Variables | ✅ 49+ | ✅ 31+ | ✅ 9.1+ | ✅ 15+ |

### C. 性能基准

在以下设备上，动画应达到60fps：

- **桌面**：Intel i5 / 8GB RAM / 集成显卡
- **中端手机**：Snapdragon 700系列 / 6GB RAM
- **低端手机**：Snapdragon 600系列 / 4GB RAM（部分效果禁用）

### D. 文件清单

```
design-system/
├── js/effects/
│   ├── typewriter.js          # 打字机效果
│   ├── count-up.js            # 数字滚动
│   ├── tilt-card.js           # 3D卡片倾斜
│   ├── floating-elements.js   # 浮动装饰元素
│   ├── mouse-glow.js          # [已停用]
│   └── text-scramble.js       # [已停用]
└── docs/
    └── effects-design.md      # 本设计文档
```

---

*星绘注：动画是盐，不是主食。恰到好处才能提味，过量则毁了一锅汤。*

*设计是克制的艺术，留白是沉默的诗。*
